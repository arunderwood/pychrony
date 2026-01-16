"""Pytest configuration and fixtures for pychrony tests."""

import pytest


@pytest.fixture
def sample_version():
    """Provide a sample version string for testing."""
    return "0.1.0"


@pytest.fixture
def sample_author():
    """Provide sample author info for testing."""
    return {"name": "arunderwood", "email": "arunderwood@users.noreply.github.com"}


@pytest.fixture
def sample_tracking_data():
    """Provide sample tracking data for testing TrackingStatus creation."""
    return {
        "reference_id": 0x7F000001,  # 127.0.0.1
        "reference_id_name": "127.0.0.1",
        "reference_ip": "127.0.0.1",
        "stratum": 2,
        "leap_status": 0,
        "ref_time": 1705320000.123456789,
        "offset": 0.000123456,
        "last_offset": 0.000111222,
        "rms_offset": 0.000100000,
        "frequency": 1.234,
        "residual_freq": 0.001,
        "skew": 0.005,
        "root_delay": 0.001234,
        "root_dispersion": 0.002345,
        "update_interval": 64.0,
    }


@pytest.fixture
def unsynchronized_tracking_data(sample_tracking_data):
    """Provide tracking data for an unsynchronized state."""
    data = sample_tracking_data.copy()
    data["reference_id"] = 0
    data["reference_id_name"] = ""
    data["stratum"] = 16
    return data


@pytest.fixture
def leap_pending_tracking_data(sample_tracking_data):
    """Provide tracking data with a pending leap second."""
    data = sample_tracking_data.copy()
    data["leap_status"] = 1  # Insert leap second
    return data
