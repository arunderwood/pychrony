"""Pytest configuration and fixtures for pychrony tests."""

import pytest

# pytester runs inner pytest sessions to exercise pychrony's pytest plugin.
pytest_plugins = ["pytester"]


@pytest.fixture
def sample_version():
    """Provide a sample version string for testing."""
    return "0.1.0"


@pytest.fixture
def sample_author():
    """Provide sample author info for testing."""
    return {"name": "arunderwood", "email": "arunderwood@users.noreply.github.com"}
