"""Pytest configuration and fixtures for pychrony tests."""

import pytest

from pychrony import LeapStatus, SourceState, SourceMode


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
        "leap_status": LeapStatus.NORMAL,
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
    data["leap_status"] = LeapStatus.UNSYNC
    return data


@pytest.fixture
def leap_pending_tracking_data(sample_tracking_data):
    """Provide tracking data with a pending leap second."""
    data = sample_tracking_data.copy()
    data["leap_status"] = LeapStatus.INSERT
    return data


@pytest.fixture
def sample_source_data():
    """Provide sample source data for testing Source creation."""
    return {
        "address": "192.168.1.100",
        "poll": 6,  # 64 seconds
        "stratum": 2,
        "state": SourceState.SELECTED,
        "mode": SourceMode.CLIENT,
        "flags": 0,
        "reachability": 255,  # all recent polls succeeded
        "last_sample_ago": 32,
        "orig_latest_meas": 0.000123456,
        "latest_meas": 0.000123456,
        "latest_meas_err": 0.000010000,
    }


@pytest.fixture
def sample_sourcestats_data():
    """Provide sample sourcestats data for testing SourceStats creation."""
    return {
        "reference_id": 0xC0A80164,  # 192.168.1.100
        "address": "192.168.1.100",
        "samples": 8,
        "runs": 3,
        "span": 512,
        "std_dev": 0.000100000,
        "resid_freq": 0.001,
        "skew": 0.005,
        "offset": 0.000123456,
        "offset_err": 0.000010000,
    }


@pytest.fixture
def sample_rtcdata():
    """Provide sample RTC data for testing RTCData creation."""
    return {
        "ref_time": 1705320000.123456789,
        "samples": 10,
        "runs": 4,
        "span": 86400,
        "offset": 0.123456,
        "freq_offset": -1.234,
    }
