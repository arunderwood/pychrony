"""Unit tests for pychrony exception hierarchy."""

import pytest

from pychrony.exceptions import (
    ChronyConnectionError,
    ChronyDataError,
    ChronyError,
    ChronyLibraryError,
    ChronyPermissionError,
)


class TestChronyError:
    """Tests for base ChronyError exception."""

    def test_message_only(self):
        """Test exception with message only."""
        error = ChronyError("Test error message")
        assert error.message == "Test error message"
        assert error.error_code is None
        assert str(error) == "Test error message"

    def test_message_and_error_code(self):
        """Test exception with message and error code."""
        error = ChronyError("Test error message", error_code=-1)
        assert error.message == "Test error message"
        assert error.error_code == -1
        assert str(error) == "Test error message (error code: -1)"

    def test_inherits_from_exception(self):
        """Test that ChronyError inherits from Exception."""
        assert issubclass(ChronyError, Exception)

    def test_can_be_raised_and_caught(self):
        """Test that exception can be raised and caught."""
        with pytest.raises(ChronyError) as exc_info:
            raise ChronyError("test")
        assert exc_info.value.message == "test"


class TestChronyConnectionError:
    """Tests for ChronyConnectionError exception."""

    def test_inherits_from_chrony_error(self):
        """Test that ChronyConnectionError inherits from ChronyError."""
        assert issubclass(ChronyConnectionError, ChronyError)

    def test_can_be_caught_as_chrony_error(self):
        """Test that ChronyConnectionError can be caught as ChronyError."""
        with pytest.raises(ChronyError):
            raise ChronyConnectionError("Connection failed", error_code=-1)

    def test_specific_catch(self):
        """Test that ChronyConnectionError can be caught specifically."""
        with pytest.raises(ChronyConnectionError) as exc_info:
            raise ChronyConnectionError("Socket not found", error_code=-2)
        assert exc_info.value.error_code == -2


class TestChronyPermissionError:
    """Tests for ChronyPermissionError exception."""

    def test_inherits_from_chrony_error(self):
        """Test that ChronyPermissionError inherits from ChronyError."""
        assert issubclass(ChronyPermissionError, ChronyError)

    def test_can_be_caught_as_chrony_error(self):
        """Test that ChronyPermissionError can be caught as ChronyError."""
        with pytest.raises(ChronyError):
            raise ChronyPermissionError("Permission denied", error_code=-3)

    def test_specific_catch(self):
        """Test that ChronyPermissionError can be caught specifically."""
        with pytest.raises(ChronyPermissionError) as exc_info:
            raise ChronyPermissionError("Access denied", error_code=-3)
        assert exc_info.value.error_code == -3


class TestChronyDataError:
    """Tests for ChronyDataError exception."""

    def test_inherits_from_chrony_error(self):
        """Test that ChronyDataError inherits from ChronyError."""
        assert issubclass(ChronyDataError, ChronyError)

    def test_can_be_caught_as_chrony_error(self):
        """Test that ChronyDataError can be caught as ChronyError."""
        with pytest.raises(ChronyError):
            raise ChronyDataError("Invalid response", error_code=-4)

    def test_specific_catch(self):
        """Test that ChronyDataError can be caught specifically."""
        with pytest.raises(ChronyDataError) as exc_info:
            raise ChronyDataError("Field not found", error_code=-4)
        assert exc_info.value.error_code == -4


class TestChronyLibraryError:
    """Tests for ChronyLibraryError exception."""

    def test_inherits_from_chrony_error(self):
        """Test that ChronyLibraryError inherits from ChronyError."""
        assert issubclass(ChronyLibraryError, ChronyError)

    def test_error_code_always_none(self):
        """Test that ChronyLibraryError always has None error_code."""
        error = ChronyLibraryError("libchrony not found")
        assert error.error_code is None

    def test_can_be_caught_as_chrony_error(self):
        """Test that ChronyLibraryError can be caught as ChronyError."""
        with pytest.raises(ChronyError):
            raise ChronyLibraryError("Library not installed")

    def test_message_format(self):
        """Test that message is formatted correctly without error code."""
        error = ChronyLibraryError("libchrony not installed")
        assert str(error) == "libchrony not installed"

    def test_helpful_install_message(self):
        """Test that ChronyLibraryError can contain helpful installation hints."""
        error = ChronyLibraryError(
            "libchrony not available. Install with: apt-get install libchrony-dev"
        )
        assert "libchrony" in str(error)
        assert "install" in str(error).lower()

    def test_error_code_not_settable_via_init(self):
        """Test that error_code cannot be set via __init__ for ChronyLibraryError."""
        # ChronyLibraryError only takes message, error_code is always None
        error = ChronyLibraryError("test")
        assert error.error_code is None
        assert error.message == "test"
