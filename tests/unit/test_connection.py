"""Unit tests for ChronyConnection context manager."""

import os
from unittest.mock import MagicMock, patch

import pytest

from pychrony import ChronyConnection, Transport
from pychrony._core._bindings import (
    CHRONY_RECV_FAILED,
    CHRONY_SEND_FAILED,
    DEFAULT_COMMAND_PORTS,
    DEFAULT_SOCKET_PATHS,
    NANOSECONDS_PER_SECOND,
    _timespec_to_float,
)
from pychrony.exceptions import (
    ChronyConnectionError,
    ChronyDataError,
    ChronyLibraryError,
    ChronyPermissionError,
)


class TestChronyConnectionBasics:
    """Basic tests for ChronyConnection class."""

    def test_connection_is_importable(self):
        """Test that ChronyConnection can be imported."""
        from pychrony import ChronyConnection

        assert ChronyConnection is not None

    def test_connection_has_context_manager_methods(self):
        """Test that ChronyConnection implements context manager protocol."""
        assert hasattr(ChronyConnection, "__enter__")
        assert hasattr(ChronyConnection, "__exit__")

    def test_connection_has_query_methods(self):
        """Test that ChronyConnection has all query methods."""
        assert hasattr(ChronyConnection, "get_tracking")
        assert hasattr(ChronyConnection, "get_sources")
        assert hasattr(ChronyConnection, "get_source_stats")
        assert hasattr(ChronyConnection, "get_rtc_data")

    def test_connection_accepts_address_parameter(self):
        """Test that ChronyConnection accepts address parameter."""
        conn = ChronyConnection("/custom/path.sock")
        assert conn._address == "/custom/path.sock"

    def test_connection_accepts_none_address(self):
        """Test that ChronyConnection accepts None address for auto-detect."""
        conn = ChronyConnection(None)
        assert conn._address is None

    def test_connection_default_address_is_none(self):
        """Test that ChronyConnection defaults to None address."""
        conn = ChronyConnection()
        assert conn._address is None


class TestChronyConnectionContextManager:
    """Tests for ChronyConnection context manager behavior."""

    @patch("pychrony._core._bindings._LIBRARY_AVAILABLE", False)
    def test_raises_library_error_when_bindings_unavailable(self):
        """Test that entering context raises ChronyLibraryError when CFFI unavailable."""
        with pytest.raises(ChronyLibraryError), ChronyConnection():
            pass

    @patch("pychrony._core._bindings._check_library_available")
    @patch("pychrony._core._bindings._lib")
    @patch("pychrony._core._bindings._ffi")
    def test_opens_socket_on_enter(self, mock_ffi, mock_lib, mock_check):
        """Test that __enter__ opens socket connection."""
        mock_lib.chrony_open_socket.return_value = 5
        mock_session = MagicMock()
        mock_ffi.new.return_value = [mock_session]
        mock_ffi.NULL = None
        mock_lib.chrony_init_session.return_value = 0

        with ChronyConnection("/test.sock"):
            mock_lib.chrony_open_socket.assert_called_once()

    @patch("pychrony._core._bindings._check_library_available")
    @patch("pychrony._core._bindings._lib")
    @patch("pychrony._core._bindings._ffi")
    def test_closes_socket_on_exit(self, mock_ffi, mock_lib, mock_check):
        """Test that __exit__ closes socket connection."""
        mock_lib.chrony_open_socket.return_value = 5
        mock_session = MagicMock()
        mock_ffi.new.return_value = [mock_session]
        mock_ffi.NULL = None
        mock_lib.chrony_init_session.return_value = 0

        with ChronyConnection("/test.sock"):
            pass

        mock_lib.chrony_deinit_session.assert_called_once()
        mock_lib.chrony_close_socket.assert_called_once_with(5)

    @patch("pychrony._core._bindings._check_library_available")
    @patch("pychrony._core._bindings._lib")
    @patch("pychrony._core._bindings._ffi")
    def test_closes_socket_on_exception(self, mock_ffi, mock_lib, mock_check):
        """Test that __exit__ closes socket even when exception occurs."""
        mock_lib.chrony_open_socket.return_value = 5
        mock_session = MagicMock()
        mock_ffi.new.return_value = [mock_session]
        mock_ffi.NULL = None
        mock_lib.chrony_init_session.return_value = 0

        with pytest.raises(ValueError), ChronyConnection("/test.sock"):
            raise ValueError("test error")

        mock_lib.chrony_deinit_session.assert_called_once()
        mock_lib.chrony_close_socket.assert_called_once_with(5)

    @patch("pychrony._core._bindings._check_library_available")
    @patch("pychrony._core._bindings._lib")
    @patch("pychrony._core._bindings._ffi")
    def test_connection_error_on_failed_socket_open(
        self, mock_ffi, mock_lib, mock_check
    ):
        """Test that connection error is raised when socket open fails."""
        mock_lib.chrony_open_socket.return_value = -1
        mock_ffi.NULL = None

        with (
            pytest.raises(ChronyConnectionError) as exc_info,
            ChronyConnection("/nonexistent.sock"),
        ):
            pass

        assert "Failed to connect" in str(exc_info.value)

    @patch("pychrony._core._bindings._check_library_available")
    @patch("pychrony._core._bindings._lib")
    @patch("pychrony._core._bindings._ffi")
    @patch("os.access")
    @patch("os.path.exists")
    def test_permission_error_on_denied_access(
        self, mock_exists, mock_access, mock_ffi, mock_lib, mock_check
    ):
        """A Unix socket that exists but is not writable raises a permission error.

        libchrony's chrony_open_socket() only ever returns -1, never a negated
        errno, so permission denial is detected from the socket itself.
        """
        mock_exists.return_value = True
        mock_access.return_value = False
        mock_lib.chrony_open_socket.return_value = -1
        mock_ffi.NULL = None

        with (
            pytest.raises(ChronyPermissionError) as exc_info,
            ChronyConnection("/protected.sock"),
        ):
            pass

        assert "Permission denied" in str(exc_info.value)

    @patch("pychrony._core._bindings._check_library_available")
    @patch("pychrony._core._bindings._lib")
    @patch("pychrony._core._bindings._ffi")
    @patch("os.access")
    @patch("os.path.exists")
    def test_permission_error_recommends_command_port_not_group(
        self, mock_exists, mock_access, mock_ffi, mock_lib, mock_check
    ):
        """Remediation points at the read-only command port, not the chrony group.

        Joining chrony's group does not grant access (the socket is not
        group-writable), and the Unix socket is a read-write control channel,
        so recommending it over-privileges read-only callers.
        """
        mock_exists.return_value = True
        mock_access.return_value = False
        mock_lib.chrony_open_socket.return_value = -1
        mock_ffi.NULL = None

        with (
            pytest.raises(ChronyPermissionError) as exc_info,
            ChronyConnection("/protected.sock"),
        ):
            pass

        message = str(exc_info.value)
        assert "127.0.0.1" in message
        assert "cmdport 0" in message
        assert "add user to chrony group" not in message.lower()

    @patch("pychrony._core._bindings._check_library_available")
    @patch("pychrony._core._bindings._lib")
    @patch("pychrony._core._bindings._ffi")
    def test_session_init_failure_closes_socket(self, mock_ffi, mock_lib, mock_check):
        """Test that socket is closed if session init fails."""
        mock_lib.chrony_open_socket.return_value = 5
        mock_ffi.new.return_value = [MagicMock()]
        mock_ffi.NULL = None
        mock_lib.chrony_init_session.return_value = -1  # Failure

        with pytest.raises(ChronyConnectionError), ChronyConnection("/test.sock"):
            pass

        mock_lib.chrony_close_socket.assert_called_once_with(5)


class TestChronyConnectionMethodsOutsideContext:
    """Tests for ChronyConnection methods called outside context."""

    def test_get_tracking_raises_outside_context(self):
        """Test that get_tracking raises RuntimeError outside context."""
        conn = ChronyConnection()
        with pytest.raises(RuntimeError) as exc_info:
            conn.get_tracking()
        assert "within a 'with' block" in str(exc_info.value)

    def test_get_sources_raises_outside_context(self):
        """Test that get_sources raises RuntimeError outside context."""
        conn = ChronyConnection()
        with pytest.raises(RuntimeError) as exc_info:
            conn.get_sources()
        assert "within a 'with' block" in str(exc_info.value)

    def test_get_source_stats_raises_outside_context(self):
        """Test that get_source_stats raises RuntimeError outside context."""
        conn = ChronyConnection()
        with pytest.raises(RuntimeError) as exc_info:
            conn.get_source_stats()
        assert "within a 'with' block" in str(exc_info.value)

    def test_get_rtc_data_raises_outside_context(self):
        """Test that get_rtc_data raises RuntimeError outside context."""
        conn = ChronyConnection()
        with pytest.raises(RuntimeError) as exc_info:
            conn.get_rtc_data()
        assert "within a 'with' block" in str(exc_info.value)


class TestChronyConnectionAddressResolution:
    """Tests for address resolution behavior."""

    @patch("pychrony._core._bindings._check_library_available")
    @patch("pychrony._core._bindings._lib")
    @patch("pychrony._core._bindings._ffi")
    def test_uses_first_connectable_default_socket(
        self, mock_ffi, mock_lib, mock_check
    ):
        """First candidate that connects is used, without probing the filesystem."""
        mock_lib.chrony_open_socket.return_value = 5
        mock_ffi.new.return_value = [MagicMock()]
        mock_ffi.NULL = None
        mock_lib.chrony_init_session.return_value = 0

        with ChronyConnection() as conn:
            assert conn.address == DEFAULT_SOCKET_PATHS[0]
            assert conn.transport is Transport.UNIX_SOCKET

        mock_lib.chrony_open_socket.assert_called_once_with(
            DEFAULT_SOCKET_PATHS[0].encode()
        )

    @patch("pychrony._core._bindings._check_library_available")
    @patch("pychrony._core._bindings._lib")
    @patch("pychrony._core._bindings._ffi")
    @patch("os.path.exists")
    def test_falls_back_when_existing_socket_refuses_connection(
        self, mock_exists, mock_ffi, mock_lib, mock_check
    ):
        """A socket that exists but refuses connection must not end auto-detect.

        os.path.exists() is True for the Unix socket, but connect() fails
        because the caller lacks write permission. Auto-detect must carry on to
        the command port rather than raise.
        """
        mock_exists.return_value = True
        connectable = DEFAULT_COMMAND_PORTS[0].encode()
        mock_lib.chrony_open_socket.side_effect = lambda addr: (
            5 if addr == connectable else -1
        )
        mock_ffi.new.return_value = [MagicMock()]
        mock_ffi.NULL = None
        mock_lib.chrony_init_session.return_value = 0

        with ChronyConnection() as conn:
            assert conn.address == DEFAULT_COMMAND_PORTS[0]
            assert conn.transport is Transport.COMMAND_PORT

        attempted = [c.args[0] for c in mock_lib.chrony_open_socket.call_args_list]
        assert attempted == [
            p.encode() for p in [*DEFAULT_SOCKET_PATHS, DEFAULT_COMMAND_PORTS[0]]
        ]

    @patch("pychrony._core._bindings._check_library_available")
    @patch("pychrony._core._bindings._lib")
    @patch("pychrony._core._bindings._ffi")
    @patch("os.path.exists")
    def test_unstattable_socket_is_still_attempted(
        self, mock_exists, mock_ffi, mock_lib, mock_check
    ):
        """A socket path that cannot be stat()ed is still tried.

        os.path.exists() is False when the parent directory is not traversable,
        which says nothing about whether chronyd is reachable there.
        """
        mock_exists.return_value = False
        mock_lib.chrony_open_socket.return_value = 5
        mock_ffi.new.return_value = [MagicMock()]
        mock_ffi.NULL = None
        mock_lib.chrony_init_session.return_value = 0

        with ChronyConnection() as conn:
            assert conn.address == DEFAULT_SOCKET_PATHS[0]

        mock_lib.chrony_open_socket.assert_called_once_with(
            DEFAULT_SOCKET_PATHS[0].encode()
        )

    @patch("pychrony._core._bindings._check_library_available")
    @patch("pychrony._core._bindings._lib")
    @patch("pychrony._core._bindings._ffi")
    @patch("os.path.exists")
    def test_tries_every_candidate_before_failing(
        self, mock_exists, mock_ffi, mock_lib, mock_check
    ):
        """Every candidate is attempted, and the error names them all."""
        mock_exists.return_value = False
        mock_lib.chrony_open_socket.return_value = -1
        mock_ffi.NULL = None

        with pytest.raises(ChronyConnectionError) as exc_info, ChronyConnection():
            pass

        attempted = [c.args[0] for c in mock_lib.chrony_open_socket.call_args_list]
        expected = [*DEFAULT_SOCKET_PATHS, *DEFAULT_COMMAND_PORTS]
        assert attempted == [p.encode() for p in expected]
        for candidate in expected:
            assert candidate in str(exc_info.value)

    @patch("pychrony._core._bindings._check_library_available")
    @patch("pychrony._core._bindings._lib")
    @patch("pychrony._core._bindings._ffi")
    def test_explicit_address_does_not_fall_back(self, mock_ffi, mock_lib, mock_check):
        """An explicit address is never silently swapped for another transport."""
        mock_lib.chrony_open_socket.return_value = -1
        mock_ffi.NULL = None

        with (
            pytest.raises(ChronyConnectionError),
            ChronyConnection("/custom/chronyd.sock"),
        ):
            pass

        mock_lib.chrony_open_socket.assert_called_once_with(b"/custom/chronyd.sock")

    @patch("pychrony._core._bindings._check_library_available")
    @patch("pychrony._core._bindings._lib")
    @patch("pychrony._core._bindings._ffi")
    def test_uses_explicit_address_directly(self, mock_ffi, mock_lib, mock_check):
        """Test that explicit address is used directly."""
        mock_lib.chrony_open_socket.return_value = 5
        mock_session = MagicMock()
        mock_ffi.new.return_value = [mock_session]
        mock_ffi.NULL = None
        mock_lib.chrony_init_session.return_value = 0

        with ChronyConnection("/custom/path.sock"):
            pass

        mock_lib.chrony_open_socket.assert_called_once_with(b"/custom/path.sock")

    @patch("pychrony._core._bindings._check_library_available")
    @patch("pychrony._core._bindings._lib")
    @patch("pychrony._core._bindings._ffi")
    def test_supports_ipv4_address(self, mock_ffi, mock_lib, mock_check):
        """Test that IPv4 address is passed correctly."""
        mock_lib.chrony_open_socket.return_value = 5
        mock_session = MagicMock()
        mock_ffi.new.return_value = [mock_session]
        mock_ffi.NULL = None
        mock_lib.chrony_init_session.return_value = 0

        with ChronyConnection("192.168.1.100"):
            pass

        mock_lib.chrony_open_socket.assert_called_once_with(b"192.168.1.100")

    @patch("pychrony._core._bindings._check_library_available")
    @patch("pychrony._core._bindings._lib")
    @patch("pychrony._core._bindings._ffi")
    def test_supports_ipv6_address(self, mock_ffi, mock_lib, mock_check):
        """Test that IPv6 address is passed correctly."""
        mock_lib.chrony_open_socket.return_value = 5
        mock_session = MagicMock()
        mock_ffi.new.return_value = [mock_session]
        mock_ffi.NULL = None
        mock_lib.chrony_init_session.return_value = 0

        with ChronyConnection("[::1]:323"):
            pass

        mock_lib.chrony_open_socket.assert_called_once_with(b"[::1]:323")


class TestTimespecToFloat:
    """Tests for _timespec_to_float() function."""

    def test_whole_seconds_only(self):
        """Test conversion with no nanoseconds."""
        ts = MagicMock()
        ts.tv_sec = 1705320000
        ts.tv_nsec = 0

        result = _timespec_to_float(ts)

        assert result == 1705320000.0

    def test_with_nanoseconds(self):
        """Test conversion with nanoseconds."""
        ts = MagicMock()
        ts.tv_sec = 1705320000
        ts.tv_nsec = 500000000  # 0.5 seconds

        result = _timespec_to_float(ts)

        assert result == 1705320000.5

    def test_nanosecond_precision(self):
        """Test nanosecond precision is preserved."""
        ts = MagicMock()
        ts.tv_sec = 1705320000
        ts.tv_nsec = 123456789

        result = _timespec_to_float(ts)

        # Should be approximately 1705320000.123456789
        assert abs(result - 1705320000.123456789) < 1e-9

    def test_zero_timestamp(self):
        """Test conversion of zero timestamp."""
        ts = MagicMock()
        ts.tv_sec = 0
        ts.tv_nsec = 0

        result = _timespec_to_float(ts)

        assert result == 0.0

    def test_max_nanoseconds(self):
        """Test with maximum nanoseconds (just under 1 second)."""
        ts = MagicMock()
        ts.tv_sec = 100
        ts.tv_nsec = 999999999

        result = _timespec_to_float(ts)

        assert result == pytest.approx(100.999999999, rel=1e-9)


class TestConstants:
    """Tests for module constants."""

    def test_nanoseconds_per_second_value(self):
        """Test NANOSECONDS_PER_SECOND has correct value."""
        assert NANOSECONDS_PER_SECOND == 1e9

    def test_default_socket_paths_are_absolute(self):
        """Test all default socket paths are absolute."""
        for path in DEFAULT_SOCKET_PATHS:
            assert os.path.isabs(path)

    def test_default_socket_paths_are_unix_sockets(self):
        """Test default socket paths end with .sock."""
        for path in DEFAULT_SOCKET_PATHS:
            assert path.endswith(".sock")


class TestGetRtcDataReturnsNone:
    """Tests for get_rtc_data() returning None when RTC unavailable."""

    @patch("pychrony._core._bindings._check_library_available")
    @patch("pychrony._core._bindings._lib")
    @patch("pychrony._core._bindings._ffi")
    def test_returns_none_when_no_rtc_records(self, mock_ffi, mock_lib, mock_check):
        """Test that get_rtc_data returns None when num_records < 1."""
        # Setup mocks for connection
        mock_lib.chrony_open_socket.return_value = 5
        mock_session = MagicMock()
        mock_ffi.new.return_value = [mock_session]
        mock_ffi.NULL = None
        mock_lib.chrony_init_session.return_value = 0

        # Setup mocks for rtcdata request
        mock_lib.chrony_request_report_number_records.return_value = 0
        mock_lib.chrony_needs_response.side_effect = [True, False]
        mock_lib.chrony_process_response.return_value = 0
        mock_lib.chrony_get_report_number_records.return_value = 0  # No records

        with ChronyConnection("/test.sock") as conn:
            result = conn.get_rtc_data()

        assert result is None

    @patch("pychrony._core._bindings._check_library_available")
    @patch("pychrony._core._bindings._lib")
    @patch("pychrony._core._bindings._ffi")
    def test_returns_none_when_rtc_fetch_fails(self, mock_ffi, mock_lib, mock_check):
        """Test that get_rtc_data returns None when rtcdata fetch fails."""
        # Setup mocks for connection
        mock_lib.chrony_open_socket.return_value = 5
        mock_session = MagicMock()
        mock_ffi.new.return_value = [mock_session]
        mock_ffi.NULL = None
        mock_lib.chrony_init_session.return_value = 0

        # Setup mocks for rtcdata request
        mock_lib.chrony_request_report_number_records.return_value = 0
        mock_lib.chrony_needs_response.side_effect = [True, False, True]
        mock_lib.chrony_process_response.side_effect = [0, 10]  # Second call fails
        mock_lib.chrony_get_report_number_records.return_value = 1  # Has record
        mock_lib.chrony_request_record.return_value = 0

        with ChronyConnection("/test.sock") as conn:
            result = conn.get_rtc_data()

        assert result is None


class TestResponseFailureDiagnostics:
    """Tests for classifying and diagnosing a failure to reach chronyd."""

    @patch("pychrony._core._bindings._check_library_available")
    @patch("pychrony._core._bindings._lib")
    @patch("pychrony._core._bindings._ffi")
    @patch("os.access")
    @patch("os.path.exists")
    def test_recv_failure_on_command_port_explains_itself(
        self, mock_exists, mock_access, mock_ffi, mock_lib, mock_check
    ):
        """A dead command port is reported as a connection failure, and says why.

        The command port is UDP, so connect() succeeds with nothing listening.
        The failure only surfaces on the first receive.
        """
        mock_exists.return_value = True
        mock_access.return_value = False
        connectable = DEFAULT_COMMAND_PORTS[0].encode()
        mock_lib.chrony_open_socket.side_effect = lambda addr: (
            5 if addr == connectable else -1
        )
        mock_ffi.new.return_value = [MagicMock()]
        mock_ffi.NULL = None
        mock_lib.chrony_init_session.return_value = 0
        mock_lib.chrony_request_report_number_records.return_value = 0
        mock_lib.chrony_needs_response.return_value = True
        mock_lib.chrony_process_response.return_value = CHRONY_RECV_FAILED

        with (
            pytest.raises(ChronyConnectionError) as exc_info,
            ChronyConnection() as conn,
        ):
            conn.get_tracking()

        message = str(exc_info.value)
        assert "cmdport 0" in message
        # The Unix socket that pushed auto-detect onto the command port is named
        assert DEFAULT_SOCKET_PATHS[0] in message

    @patch("pychrony._core._bindings._check_library_available")
    @patch("pychrony._core._bindings._lib")
    @patch("pychrony._core._bindings._ffi")
    def test_send_failure_is_a_connection_error(self, mock_ffi, mock_lib, mock_check):
        """A failed send() is a connection failure, not a data failure."""
        mock_lib.chrony_open_socket.return_value = 5
        mock_ffi.new.return_value = [MagicMock()]
        mock_ffi.NULL = None
        mock_lib.chrony_init_session.return_value = 0
        mock_lib.chrony_request_report_number_records.return_value = CHRONY_SEND_FAILED

        with (
            pytest.raises(ChronyConnectionError) as exc_info,
            ChronyConnection() as conn,
        ):
            conn.get_tracking()

        assert "did not respond" in str(exc_info.value)

    @patch("pychrony._core._bindings._check_library_available")
    @patch("pychrony._core._bindings._lib")
    @patch("pychrony._core._bindings._ffi")
    def test_no_command_port_guidance_on_unix_socket(
        self, mock_ffi, mock_lib, mock_check
    ):
        """A Unix socket failure gets no command-port guidance."""
        mock_lib.chrony_open_socket.return_value = 5
        mock_ffi.new.return_value = [MagicMock()]
        mock_ffi.NULL = None
        mock_lib.chrony_init_session.return_value = 0
        mock_lib.chrony_request_report_number_records.return_value = 0
        mock_lib.chrony_needs_response.return_value = True
        mock_lib.chrony_process_response.return_value = CHRONY_RECV_FAILED

        with (
            pytest.raises(ChronyConnectionError) as exc_info,
            ChronyConnection() as conn,
        ):
            conn.get_tracking()

        assert "cmdport 0" not in str(exc_info.value)

    @patch("pychrony._core._bindings._check_library_available")
    @patch("pychrony._core._bindings._lib")
    @patch("pychrony._core._bindings._ffi")
    def test_non_transport_error_is_still_a_data_error(
        self, mock_ffi, mock_lib, mock_check
    ):
        """Failures that are not send/recv problems stay ChronyDataError."""
        mock_lib.chrony_open_socket.return_value = 5
        mock_ffi.new.return_value = [MagicMock()]
        mock_ffi.NULL = None
        mock_lib.chrony_init_session.return_value = 0
        # CHRONY_UNKNOWN_REPORT - a problem with the report, not the transport
        mock_lib.chrony_request_report_number_records.return_value = 3

        with pytest.raises(ChronyDataError), ChronyConnection() as conn:
            conn.get_tracking()
