"""Testing utilities for pychrony.

This module provides factory functions and pytest fixtures for creating
test instances of pychrony dataclasses with sensible defaults.

Factory Functions (for any test framework):
    from pychrony.testing import make_tracking, make_source
    status = make_tracking(stratum=3, offset=-0.001)

Pytest Fixtures (auto-discovered via plugin):
    def test_something(tracking_status, source):
        assert tracking_status.is_synchronized()
"""

from typing import Any

import pytest

from pychrony import (
    TrackingStatus,
    Source,
    SourceStats,
    RTCData,
    LeapStatus,
    SourceState,
    SourceMode,
)

__all__ = [
    "make_tracking",
    "make_source",
    "make_source_stats",
    "make_rtc_data",
    "TRACKING_DEFAULTS",
    "SOURCE_DEFAULTS",
    "SOURCESTATS_DEFAULTS",
    "RTCDATA_DEFAULTS",
]

# Default values based on realistic synchronized chrony output
TRACKING_DEFAULTS: dict[str, Any] = {
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

SOURCE_DEFAULTS: dict[str, Any] = {
    "address": "192.168.1.100",
    "poll": 6,  # 64 seconds
    "stratum": 2,
    "state": SourceState.SELECTED,
    "mode": SourceMode.CLIENT,
    "flags": 0,
    "reachability": 255,  # All recent polls succeeded
    "last_sample_ago": 32,
    "orig_latest_meas": 0.000123456,
    "latest_meas": 0.000123456,
    "latest_meas_err": 0.000010000,
}

SOURCESTATS_DEFAULTS: dict[str, Any] = {
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

RTCDATA_DEFAULTS: dict[str, Any] = {
    "ref_time": 1705320000.123456789,
    "samples": 10,
    "runs": 4,
    "span": 86400,
    "offset": 0.123456,
    "freq_offset": -1.234,
}


def make_tracking(**overrides: Any) -> TrackingStatus:
    """Create a TrackingStatus instance with sensible defaults.

    Default state is synchronized (reference_id != 0, stratum=2).

    Args:
        **overrides: Field values to override defaults

    Returns:
        TrackingStatus instance

    Example:
        >>> make_tracking()  # Synchronized status
        >>> make_tracking(stratum=16, reference_id=0)  # Unsynchronized
        >>> make_tracking(leap_status=LeapStatus.INSERT)  # Leap pending
    """
    return TrackingStatus(**{**TRACKING_DEFAULTS, **overrides})


def make_source(**overrides: Any) -> Source:
    """Create a Source instance with sensible defaults.

    Default state is selected and reachable.

    Args:
        **overrides: Field values to override defaults

    Returns:
        Source instance
    """
    return Source(**{**SOURCE_DEFAULTS, **overrides})


def make_source_stats(**overrides: Any) -> SourceStats:
    """Create a SourceStats instance with sensible defaults.

    Default has 8 samples (sufficient for statistics).

    Args:
        **overrides: Field values to override defaults

    Returns:
        SourceStats instance
    """
    return SourceStats(**{**SOURCESTATS_DEFAULTS, **overrides})


def make_rtc_data(**overrides: Any) -> RTCData:
    """Create an RTCData instance with sensible defaults.

    Default is calibrated (samples > 0).

    Args:
        **overrides: Field values to override defaults

    Returns:
        RTCData instance
    """
    return RTCData(**{**RTCDATA_DEFAULTS, **overrides})


# Pytest fixtures - auto-discovered via pytest plugin entry point
@pytest.fixture
def tracking_status() -> TrackingStatus:
    """Fixture providing a synchronized TrackingStatus with defaults."""
    return make_tracking()


@pytest.fixture
def source() -> Source:
    """Fixture providing a selected, reachable Source with defaults."""
    return make_source()


@pytest.fixture
def source_stats() -> SourceStats:
    """Fixture providing a SourceStats with sufficient samples."""
    return make_source_stats()


@pytest.fixture
def rtc_data() -> RTCData:
    """Fixture providing a calibrated RTCData with defaults."""
    return make_rtc_data()
