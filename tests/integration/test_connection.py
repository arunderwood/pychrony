"""Integration tests for ChronyConnection error scenarios.

These tests verify proper error handling when connection to chronyd fails.
"""

import importlib.util

import pytest

from pychrony import ChronyConnection
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
            with pytest.raises(ChronyLibraryError):
                with ChronyConnection("/nonexistent/path.sock") as conn:
                    conn.get_tracking()
        else:
            with pytest.raises(ChronyConnectionError) as exc_info:
                with ChronyConnection("/nonexistent/path.sock") as conn:
                    conn.get_tracking()
            assert "Failed to connect" in str(exc_info.value)

    def test_connection_error_has_error_code(self):
        """Test that ChronyConnectionError includes error code."""
        if not HAS_CFFI_BINDINGS:
            pytest.skip("CFFI bindings not available")

        with pytest.raises(ChronyConnectionError) as exc_info:
            with ChronyConnection("/nonexistent/path.sock") as conn:
                conn.get_tracking()
        # Error code should be set (typically negative)
        assert exc_info.value.error_code is not None


class TestLibraryErrors:
    """Tests for library availability error handling."""

    def test_library_error_message_is_helpful(self):
        """Test that ChronyLibraryError has helpful message."""
        if HAS_CFFI_BINDINGS:
            pytest.skip("CFFI bindings are available")

        with pytest.raises(ChronyLibraryError) as exc_info:
            with ChronyConnection() as conn:
                conn.get_tracking()
        message = str(exc_info.value)
        # Should mention libchrony and installation
        assert "libchrony" in message.lower()
        assert "install" in message.lower()

    def test_library_error_has_no_error_code(self):
        """Test that ChronyLibraryError has None error_code."""
        if HAS_CFFI_BINDINGS:
            pytest.skip("CFFI bindings are available")

        with pytest.raises(ChronyLibraryError) as exc_info:
            with ChronyConnection() as conn:
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
        with pytest.raises(ChronyConnectionError):
            with ChronyConnection("/this/path/does/not/exist.sock") as conn:
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
