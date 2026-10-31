"""Unit tests for pychrony.testing and the pychrony pytest plugins."""

import subprocess
import sys
from dataclasses import FrozenInstanceError

import pytest

from pychrony import LeapStatus, RTCData, Source, SourceStats, TrackingStatus
from pychrony.testing import (
    make_rtc_data,
    make_source,
    make_source_stats,
    make_tracking,
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


class TestTestingWithoutPytest:
    """pychrony.testing must stay importable when pytest is not installed."""

    def test_import_with_pytest_blocked(self):
        """Test factories import and work with pytest blocked from importing."""
        code = (
            "import sys\n"
            "sys.modules['pytest'] = None\n"
            "from pychrony.testing import (\n"
            "    RTCDATA_DEFAULTS, SOURCE_DEFAULTS, SOURCESTATS_DEFAULTS,\n"
            "    TRACKING_DEFAULTS, make_rtc_data, make_source,\n"
            "    make_source_stats, make_tracking,\n"
            ")\n"
            "assert make_tracking().is_synchronized()\n"
            "make_source(); make_source_stats(); make_rtc_data()\n"
            "assert 'pychrony.pytest_plugin' not in sys.modules\n"
        )
        result = subprocess.run(
            [sys.executable, "-c", code],
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode == 0, result.stderr


PREFIXED_FIXTURE_TESTS = """
from pychrony import RTCData, Source, SourceStats, TrackingStatus

def test_prefixed(
    chrony_tracking_status, chrony_source, chrony_source_stats, chrony_rtc_data
):
    assert isinstance(chrony_tracking_status, TrackingStatus)
    assert chrony_tracking_status.is_synchronized()
    assert isinstance(chrony_source, Source)
    assert isinstance(chrony_source_stats, SourceStats)
    assert isinstance(chrony_rtc_data, RTCData)
"""

OLD_FIXTURE_TESTS = """
from pychrony import RTCData, Source, SourceStats, TrackingStatus

def test_tracking_status(tracking_status):
    assert isinstance(tracking_status, TrackingStatus)

def test_source(source):
    assert isinstance(source, Source)

def test_source_stats(source_stats):
    assert isinstance(source_stats, SourceStats)

def test_rtc_data(rtc_data):
    assert isinstance(rtc_data, RTCData)
"""

OPT_IN_CONFTEST = 'pytest_plugins = ["pychrony.pytest_plugin"]\n'


class TestPytestPlugin:
    """Tests for the opt-in pychrony.pytest_plugin."""

    def test_opt_in_provides_prefixed_fixtures(self, pytester):
        """Test the chrony_* fixtures are available once the plugin is enabled."""
        pytester.makeconftest(OPT_IN_CONFTEST)
        pytester.makepyfile(PREFIXED_FIXTURE_TESTS)
        result = pytester.runpytest()
        result.assert_outcomes(passed=1)

    def test_opt_in_does_not_provide_unprefixed_names(self, pytester):
        """Test the plugin registers no generic fixture names."""
        pytester.makeconftest(OPT_IN_CONFTEST)
        pytester.makepyfile(OLD_FIXTURE_TESTS)
        result = pytester.runpytest()
        result.assert_outcomes(errors=4)
        result.stdout.fnmatch_lines(["*fixture 'tracking_status' not found*"])

    def test_no_fixtures_without_opt_in(self, pytester):
        """Test installing pychrony does not add fixtures to every pytest run."""
        pytester.makepyfile(PREFIXED_FIXTURE_TESTS)
        result = pytester.runpytest()
        result.assert_outcomes(errors=1)
        result.stdout.fnmatch_lines(["*fixture 'chrony_tracking_status' not found*"])
