"""Unit tests for pychrony binding layer functions."""

import os
from unittest.mock import MagicMock, patch

import pytest

from pychrony._core._bindings import (
    _timespec_to_float,
    _find_socket_path,
    DEFAULT_SOCKET_PATHS,
    NANOSECONDS_PER_SECOND,
)
from pychrony.exceptions import ChronyConnectionError


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


class TestFindSocketPath:
    """Tests for _find_socket_path() function."""

    def test_explicit_path_returned_as_is(self):
        """Test that explicit socket path is returned unchanged."""
        result = _find_socket_path("/custom/path/chronyd.sock")

        assert result == "/custom/path/chronyd.sock"

    def test_explicit_path_not_validated(self):
        """Test that explicit path is not validated for existence."""
        # Even a non-existent explicit path should be returned
        result = _find_socket_path("/nonexistent/path/socket.sock")

        assert result == "/nonexistent/path/socket.sock"

    @patch("os.path.exists")
    def test_first_default_path_found(self, mock_exists):
        """Test that first existing default path is returned."""
        mock_exists.side_effect = lambda p: p == DEFAULT_SOCKET_PATHS[0]

        result = _find_socket_path(None)

        assert result == DEFAULT_SOCKET_PATHS[0]

    @patch("os.path.exists")
    def test_second_default_path_found(self, mock_exists):
        """Test that second default path is returned if first doesn't exist."""
        mock_exists.side_effect = lambda p: p == DEFAULT_SOCKET_PATHS[1]

        result = _find_socket_path(None)

        assert result == DEFAULT_SOCKET_PATHS[1]

    @patch("os.path.exists")
    def test_no_default_path_found_raises(self, mock_exists):
        """Test that ChronyConnectionError is raised if no socket found."""
        mock_exists.return_value = False

        with pytest.raises(ChronyConnectionError) as exc_info:
            _find_socket_path(None)

        assert "chronyd socket not found" in str(exc_info.value)
        assert "Is chronyd running?" in str(exc_info.value)

    @patch("os.path.exists")
    def test_error_message_includes_tried_paths(self, mock_exists):
        """Test that error message includes all tried paths."""
        mock_exists.return_value = False

        with pytest.raises(ChronyConnectionError) as exc_info:
            _find_socket_path(None)

        for path in DEFAULT_SOCKET_PATHS:
            assert path in str(exc_info.value)


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
