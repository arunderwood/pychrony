"""Test package import functionality for User Story 1."""


def test_package_import_success():
    """Test that pychrony package can be imported successfully."""
    # This test should pass once the package is properly structured
    import pychrony

    assert pychrony is not None


def test_package_all():
    """Test that __all__ is defined."""
    import pychrony

    # Check that __all__ is defined
    assert hasattr(pychrony, "__all__")
