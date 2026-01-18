"""Unit tests for ChronyConnection context manager."""

import os
from unittest.mock import MagicMock, patch

import pytest

from pychrony import ChronyConnection
from pychrony._core._bindings import (
    _timespec_to_float,
    DEFAULT_SOCKET_PATHS,
    NANOSECONDS_PER_SECOND,
)
from pychrony.exceptions import (
    ChronyConnectionError,
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
        with pytest.raises(ChronyLibraryError):
            with ChronyConnection():
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

        with pytest.raises(ValueError):
            with ChronyConnection("/test.sock"):
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

        with pytest.raises(ChronyConnectionError) as exc_info:
            with ChronyConnection("/nonexistent.sock"):
                pass

        assert "Failed to connect" in str(exc_info.value)

    @patch("pychrony._core._bindings._check_library_available")
    @patch("pychrony._core._bindings._lib")
    @patch("pychrony._core._bindings._ffi")
    def test_permission_error_on_denied_access(self, mock_ffi, mock_lib, mock_check):
        """Test that permission error is raised when access denied."""
        mock_lib.chrony_open_socket.return_value = -13  # EACCES
        mock_ffi.NULL = None

        with pytest.raises(ChronyPermissionError) as exc_info:
            with ChronyConnection("/protected.sock"):
                pass

        assert "Permission denied" in str(exc_info.value)

    @patch("pychrony._core._bindings._check_library_available")
    @patch("pychrony._core._bindings._lib")
    @patch("pychrony._core._bindings._ffi")
    def test_session_init_failure_closes_socket(self, mock_ffi, mock_lib, mock_check):
        """Test that socket is closed if session init fails."""
        mock_lib.chrony_open_socket.return_value = 5
        mock_ffi.new.return_value = [MagicMock()]
        mock_ffi.NULL = None
        mock_lib.chrony_init_session.return_value = -1  # Failure

        with pytest.raises(ChronyConnectionError):
            with ChronyConnection("/test.sock"):
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
    @patch("os.path.exists")
    def test_uses_first_existing_default_socket(
        self, mock_exists, mock_ffi, mock_lib, mock_check
    ):
        """Test that first existing default socket is used."""
        mock_exists.side_effect = lambda p: p == DEFAULT_SOCKET_PATHS[0]
        mock_lib.chrony_open_socket.return_value = 5
        mock_session = MagicMock()
        mock_ffi.new.return_value = [mock_session]
        mock_ffi.NULL = None
        mock_lib.chrony_init_session.return_value = 0

        with ChronyConnection():
            pass

        mock_lib.chrony_open_socket.assert_called_once_with(
            DEFAULT_SOCKET_PATHS[0].encode()
        )

    @patch("pychrony._core._bindings._check_library_available")
    @patch("pychrony._core._bindings._lib")
    @patch("pychrony._core._bindings._ffi")
    @patch("os.path.exists")
    def test_uses_second_default_socket_if_first_missing(
        self, mock_exists, mock_ffi, mock_lib, mock_check
    ):
        """Test that second default socket is used if first doesn't exist."""
        mock_exists.side_effect = lambda p: p == DEFAULT_SOCKET_PATHS[1]
        mock_lib.chrony_open_socket.return_value = 5
        mock_session = MagicMock()
        mock_ffi.new.return_value = [mock_session]
        mock_ffi.NULL = None
        mock_lib.chrony_init_session.return_value = 0

        with ChronyConnection():
            pass

        mock_lib.chrony_open_socket.assert_called_once_with(
            DEFAULT_SOCKET_PATHS[1].encode()
        )

    @patch("pychrony._core._bindings._check_library_available")
    @patch("pychrony._core._bindings._lib")
    @patch("pychrony._core._bindings._ffi")
    @patch("os.path.exists")
    def test_passes_null_when_no_default_sockets_exist(
        self, mock_exists, mock_ffi, mock_lib, mock_check
    ):
        """Test that NULL is passed when no default sockets exist."""
        mock_exists.return_value = False
        mock_lib.chrony_open_socket.return_value = 5
        mock_session = MagicMock()
        mock_ffi.new.return_value = [mock_session]
        mock_ffi.NULL = None
        mock_lib.chrony_init_session.return_value = 0

        with ChronyConnection():
            pass

        mock_lib.chrony_open_socket.assert_called_once_with(None)

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
