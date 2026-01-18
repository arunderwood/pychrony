"""Unit tests for pychrony.testing module."""

from dataclasses import FrozenInstanceError

import pytest

from pychrony import TrackingStatus, Source, SourceStats, RTCData, LeapStatus
from pychrony.testing import (
    make_tracking,
    make_source,
    make_source_stats,
    make_rtc_data,
)


class TestMakeTracking:
    """Tests for make_tracking factory function."""

    def test_returns_tracking_status(self):
        """Test that make_tracking returns a TrackingStatus instance."""
        assert isinstance(make_tracking(), TrackingStatus)

    def test_default_is_synchronized(self):
        """Test that default status is synchronized."""
        assert make_tracking().is_synchronized()

    def test_override_single_field(self):
        """Test overriding a single field."""
        assert make_tracking(stratum=5).stratum == 5

    def test_override_multiple_fields(self):
        """Test overriding multiple fields."""
        status = make_tracking(stratum=3, offset=-0.001)
        assert status.stratum == 3
        assert status.offset == -0.001

    def test_returns_frozen_instance(self):
        """Test that the returned instance is frozen."""
        with pytest.raises(FrozenInstanceError):
            make_tracking().offset = 0.0

    def test_override_leap_status(self):
        """Test overriding leap_status with enum."""
        status = make_tracking(leap_status=LeapStatus.INSERT)
        assert status.leap_status == LeapStatus.INSERT
        assert status.is_leap_pending() is True


class TestMakeSource:
    """Tests for make_source factory function."""

    def test_returns_source(self):
        """Test that make_source returns a Source instance."""
        assert isinstance(make_source(), Source)

    def test_default_is_selected(self):
        """Test that default source is selected."""
        assert make_source().is_selected()

    def test_default_is_reachable(self):
        """Test that default source is reachable."""
        assert make_source().is_reachable()

    def test_override_reachability(self):
        """Test overriding reachability."""
        source = make_source(reachability=0)
        assert source.is_reachable() is False

    def test_override_address(self):
        """Test overriding address."""
        source = make_source(address="10.0.0.1")
        assert source.address == "10.0.0.1"


class TestMakeSourceStats:
    """Tests for make_source_stats factory function."""

    def test_returns_source_stats(self):
        """Test that make_source_stats returns a SourceStats instance."""
        assert isinstance(make_source_stats(), SourceStats)

    def test_default_has_sufficient_samples(self):
        """Test that default has sufficient samples."""
        assert make_source_stats().has_sufficient_samples()

    def test_override_samples(self):
        """Test overriding samples."""
        stats = make_source_stats(samples=2)
        assert stats.samples == 2
        assert stats.has_sufficient_samples() is False

    def test_override_address(self):
        """Test overriding address."""
        stats = make_source_stats(address="10.0.0.2")
        assert stats.address == "10.0.0.2"


class TestMakeRtcData:
    """Tests for make_rtc_data factory function."""

    def test_returns_rtc_data(self):
        """Test that make_rtc_data returns an RTCData instance."""
        assert isinstance(make_rtc_data(), RTCData)

    def test_default_is_calibrated(self):
        """Test that default RTC data is calibrated."""
        assert make_rtc_data().is_calibrated()

    def test_override_samples_to_zero(self):
        """Test overriding samples to zero makes it uncalibrated."""
        rtc = make_rtc_data(samples=0)
        assert rtc.is_calibrated() is False

    def test_override_offset(self):
        """Test overriding offset."""
        rtc = make_rtc_data(offset=0.5)
        assert rtc.offset == 0.5
