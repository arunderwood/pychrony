"""Pytest fixtures for testing code that uses pychrony.

Enable the plugin in your top-level ``conftest.py``; pytest rejects
``pytest_plugins`` in nested conftest files:

    pytest_plugins = ["pychrony.pytest_plugin"]

Then request the fixtures by name:

    def test_something(chrony_tracking_status, chrony_source):
        assert chrony_tracking_status.is_synchronized()

Each fixture returns the matching `pychrony.testing` factory's default
instance. Use the factories directly when a test needs custom field values.
"""

import pytest

from pychrony import RTCData, Source, SourceStats, TrackingStatus
from pychrony.testing import (
    make_rtc_data,
    make_source,
    make_source_stats,
    make_tracking,
)

__all__ = [
    "chrony_tracking_status",
    "chrony_source",
    "chrony_source_stats",
    "chrony_rtc_data",
]


@pytest.fixture
def chrony_tracking_status() -> TrackingStatus:
    """Fixture providing a synchronized TrackingStatus with defaults."""
    return make_tracking()


@pytest.fixture
def chrony_source() -> Source:
    """Fixture providing a selected, reachable Source with defaults."""
    return make_source()


@pytest.fixture
def chrony_source_stats() -> SourceStats:
    """Fixture providing a SourceStats with sufficient samples."""
    return make_source_stats()


@pytest.fixture
def chrony_rtc_data() -> RTCData:
    """Fixture providing a calibrated RTCData with defaults."""
    return make_rtc_data()
