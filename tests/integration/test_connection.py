"""Integration tests for ChronyConnection error scenarios.

These tests verify proper error handling when connection to chronyd fails.
"""

import importlib.util
import os
import pwd
import stat
import subprocess
import sys

import pytest

from pychrony import ChronyConnection, Transport
from pychrony.exceptions import (
    ChronyConnectionError,
    ChronyLibraryError,
)

# Check if CFFI bindings are available
HAS_CFFI_BINDINGS = (
    importlib.util.find_spec("pychrony._core._cffi_bindings") is not None
)


class TestConnectionErrors:
    """Tests for connection error handling."""

    def test_invalid_socket_path_raises_connection_error(self):
        """Test that invalid socket path raises ChronyConnectionError."""
        if not HAS_CFFI_BINDINGS:
            with (
                pytest.raises(ChronyLibraryError),
                ChronyConnection("/nonexistent/path.sock") as conn,
            ):
                conn.get_tracking()
        else:
            with (
                pytest.raises(ChronyConnectionError) as exc_info,
                ChronyConnection("/nonexistent/path.sock") as conn,
            ):
                conn.get_tracking()
            assert "Failed to connect" in str(exc_info.value)

    def test_connection_error_has_error_code(self):
        """Test that ChronyConnectionError includes error code."""
        if not HAS_CFFI_BINDINGS:
            pytest.skip("CFFI bindings not available")

        with (
            pytest.raises(ChronyConnectionError) as exc_info,
            ChronyConnection("/nonexistent/path.sock") as conn,
        ):
            conn.get_tracking()
        # Error code should be set (typically negative)
        assert exc_info.value.error_code is not None


class TestLibraryErrors:
    """Tests for library availability error handling."""

    def test_library_error_message_is_helpful(self):
        """Test that ChronyLibraryError has helpful message."""
        if HAS_CFFI_BINDINGS:
            pytest.skip("CFFI bindings are available")

        with pytest.raises(ChronyLibraryError) as exc_info, ChronyConnection() as conn:
            conn.get_tracking()
        message = str(exc_info.value)
        # Should mention libchrony and installation
        assert "libchrony" in message.lower()
        assert "install" in message.lower()

    def test_library_error_has_no_error_code(self):
        """Test that ChronyLibraryError has None error_code."""
        if HAS_CFFI_BINDINGS:
            pytest.skip("CFFI bindings are available")

        with pytest.raises(ChronyLibraryError) as exc_info, ChronyConnection() as conn:
            conn.get_tracking()
        assert exc_info.value.error_code is None


@pytest.mark.skipif(not HAS_CFFI_BINDINGS, reason="CFFI bindings not compiled")
class TestSocketAutoDetection:
    """Tests for socket path auto-detection."""

    def test_auto_detects_default_socket(self):
        """Test that ChronyConnection auto-detects default socket."""
        with ChronyConnection() as conn:
            status = conn.get_tracking()
            assert status is not None

    def test_explicit_socket_path_used(self):
        """Test that explicit socket path is used."""
        # Nonexistent path should fail
        with (
            pytest.raises(ChronyConnectionError),
            ChronyConnection("/this/path/does/not/exist.sock") as conn,
        ):
            conn.get_tracking()


@pytest.mark.skipif(not HAS_CFFI_BINDINGS, reason="CFFI bindings not compiled")
class TestConnectionReuse:
    """Tests for connection reuse."""

    def test_multiple_queries_single_connection(self):
        """Test that multiple queries use the same connection."""
        with ChronyConnection() as conn:
            tracking = conn.get_tracking()
            sources = conn.get_sources()
            stats = conn.get_source_stats()
            conn.get_rtc_data()  # RTC may be None if not configured

            # All should return valid data
            assert tracking is not None
            assert isinstance(sources, list)
            assert isinstance(stats, list)

    def test_all_report_types_in_single_connection(self):
        """Test that all 4 report types work in single connection."""
        with ChronyConnection() as conn:
            # Get all reports
            tracking = conn.get_tracking()
            sources = conn.get_sources()
            stats = conn.get_source_stats()
            conn.get_rtc_data()  # RTC may be None if not configured

            # Verify we got data
            assert tracking.stratum <= 15
            assert len(sources) == len(stats)  # Should match


UNPRIVILEGED_USER = "testuser"
CHRONY_RUNTIME_DIR = "/run/chrony"


def _unprivileged_user_exists() -> bool:
    """Return True if the unprivileged test account is present."""
    try:
        pwd.getpwnam(UNPRIVILEGED_USER)
    except KeyError:
        return False
    return True


def _run_unprivileged(code: str) -> subprocess.CompletedProcess:
    """Run a Python snippet as the unprivileged test user.

    Supplementary groups are cleared so the child cannot reach chronyd's socket
    through chrony group membership, which is the situation a read-only consumer
    is in.
    """
    entry = pwd.getpwnam(UNPRIVILEGED_USER)
    return subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
        check=False,
        user=entry.pw_uid,
        group=entry.pw_gid,
        extra_groups=[],
        cwd="/",
    )


@pytest.fixture
def traversable_runtime_dir():
    """Make chronyd's runtime directory traversable, then restore its mode.

    This is the condition under which the Unix socket stat()s successfully for
    an unprivileged user but still refuses the connection, because connecting
    to a Unix socket requires write permission the caller does not have.
    """
    original_mode = stat.S_IMODE(os.stat(CHRONY_RUNTIME_DIR).st_mode)
    os.chmod(CHRONY_RUNTIME_DIR, 0o755)
    try:
        yield
    finally:
        os.chmod(CHRONY_RUNTIME_DIR, original_mode)


@pytest.mark.skipif(not HAS_CFFI_BINDINGS, reason="CFFI bindings not compiled")
class TestResolvedTransport:
    """Tests for reporting which transport a connection ended up on."""

    def test_address_and_transport_reported_for_auto_detect(self):
        """Auto-detect reports the candidate it actually connected to."""
        with ChronyConnection() as conn:
            assert conn.address is not None
            assert conn.transport is not None
            conn.get_tracking()

    def test_address_and_transport_are_none_before_and_after_connect(self):
        """Neither property makes a claim outside an open connection."""
        conn = ChronyConnection()
        assert conn.address is None
        assert conn.transport is None

        with conn:
            assert conn.address is not None

        assert conn.address is None
        assert conn.transport is None

    def test_explicit_command_port_reports_command_port(self):
        """An explicit localhost address is reported as the read-only transport."""
        with ChronyConnection("127.0.0.1") as conn:
            assert conn.transport is Transport.COMMAND_PORT
            assert conn.address == "127.0.0.1"
            assert conn.get_tracking() is not None


@pytest.mark.skipif(not HAS_CFFI_BINDINGS, reason="CFFI bindings not compiled")
@pytest.mark.skipif(os.geteuid() != 0, reason="requires root to drop privileges")
@pytest.mark.skipif(
    not _unprivileged_user_exists(), reason=f"no {UNPRIVILEGED_USER} account"
)
class TestAutoDetectFallback:
    """Tests that auto-detect falls back on connectability, not on stat()."""

    def test_falls_back_to_command_port_when_socket_refuses_connection(
        self, traversable_runtime_dir
    ):
        """Regression: an unconnectable-but-present socket must not end auto-detect.

        With chronyd's runtime directory traversable, an unprivileged caller can
        stat() the Unix socket but cannot connect to it. Auto-detect must carry
        on to the command port instead of raising.
        """
        result = _run_unprivileged(
            "import os\n"
            "from pychrony import ChronyConnection, Transport\n"
            "assert os.path.exists('/run/chrony/chronyd.sock'), 'socket should stat'\n"
            "with ChronyConnection() as c:\n"
            "    print(c.transport.value, c.get_tracking().stratum)\n"
        )
        assert result.returncode == 0, result.stderr
        assert Transport.COMMAND_PORT.value in result.stdout

    def test_falls_back_when_socket_cannot_be_stat_ed(self):
        """The stock case still works: unstattable socket, connection via localhost."""
        result = _run_unprivileged(
            "import os\n"
            "from pychrony import ChronyConnection, Transport\n"
            "assert not os.path.exists('/run/chrony/chronyd.sock')\n"
            "with ChronyConnection() as c:\n"
            "    print(c.transport.value, c.get_tracking().stratum)\n"
        )
        assert result.returncode == 0, result.stderr
        assert Transport.COMMAND_PORT.value in result.stdout
