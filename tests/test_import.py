"""Test package import functionality for User Story 1."""



def test_package_import_success():
    """Test that pychrony package can be imported successfully."""
    # This test should pass once the package is properly structured
    import pychrony

    assert pychrony is not None
    assert hasattr(pychrony, "__version__")
    assert hasattr(pychrony, "__author__")
    assert hasattr(pychrony, "__email__")


def test_version_string_accessibility():
    """Test that version string is accessible and valid."""
    import pychrony

    version = pychrony.__version__

    assert version is not None
    assert isinstance(version, str)
    assert len(version) > 0
    # Should match semantic version pattern (basic check)
    assert version.count(".") >= 1


def test_package_metadata():
    """Test that package metadata is accessible."""
    import pychrony

    # Test basic metadata exists
    assert pychrony.__author__ == "arunderwood"
    assert pychrony.__email__ == "arunderwood@users.noreply.github.com"
    assert pychrony.__license__ == "MIT"
    assert pychrony.__description__ == "Python bindings for chrony NTP client"


def test_package_all():
    """Test that __all__ exports expected items."""
    import pychrony

    # Check that __all__ is defined and contains expected items
    assert hasattr(pychrony, "__all__")
    expected_items = [
        "__version__",
        "__author__",
        "__email__",
        "__license__",
        "__description__",
    ]

    for item in expected_items:
        assert item in pychrony.__all__
