"""Placeholder test file for pytest discovery testing."""


def test_placeholder_function():
    """A placeholder test to verify pytest discovery works."""
    assert True


def test_placeholder_math():
    """Another placeholder test with basic math operations."""
    result = 2 + 2
    assert result == 4


class TestPlaceholderClass:
    """Placeholder test class for discovery testing."""

    def test_class_method(self):
        """Test method inside a test class."""
        assert "hello" == "hello"

    def test_another_method(self):
        """Another test method."""
        numbers = [1, 2, 3]
        assert len(numbers) == 3
