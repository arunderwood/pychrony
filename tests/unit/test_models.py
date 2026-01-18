"""Unit tests for pychrony data models."""

import pytest
from dataclasses import FrozenInstanceError

from pychrony.models import (
    _ref_id_to_name,
    LeapStatus,
    SourceState,
    SourceMode,
)
from pychrony.testing import (
    make_tracking,
    make_source,
    make_source_stats,
    make_rtc_data,
    TRACKING_DEFAULTS,
    SOURCE_DEFAULTS,
    SOURCESTATS_DEFAULTS,
    RTCDATA_DEFAULTS,
)


class TestTrackingStatus:
    """Tests for TrackingStatus dataclass."""

    def test_creation_with_all_fields(self):
        """Test creating TrackingStatus with all required fields."""
        status = make_tracking()

        assert status.reference_id == TRACKING_DEFAULTS["reference_id"]
        assert status.reference_id_name == TRACKING_DEFAULTS["reference_id_name"]
        assert status.reference_ip == TRACKING_DEFAULTS["reference_ip"]
        assert status.stratum == TRACKING_DEFAULTS["stratum"]
        assert status.leap_status == TRACKING_DEFAULTS["leap_status"]
        assert status.ref_time == TRACKING_DEFAULTS["ref_time"]
        assert status.offset == TRACKING_DEFAULTS["offset"]
        assert status.last_offset == TRACKING_DEFAULTS["last_offset"]
        assert status.rms_offset == TRACKING_DEFAULTS["rms_offset"]
        assert status.frequency == TRACKING_DEFAULTS["frequency"]
        assert status.residual_freq == TRACKING_DEFAULTS["residual_freq"]
        assert status.skew == TRACKING_DEFAULTS["skew"]
        assert status.root_delay == TRACKING_DEFAULTS["root_delay"]
        assert status.root_dispersion == TRACKING_DEFAULTS["root_dispersion"]
        assert status.update_interval == TRACKING_DEFAULTS["update_interval"]

    def test_is_frozen(self):
        """Test that TrackingStatus is immutable (frozen)."""
        status = make_tracking()

        with pytest.raises(FrozenInstanceError):
            status.offset = 0.001

    def test_has_correct_field_count(self):
        """Test that TrackingStatus has exactly 15 fields."""
        status = make_tracking()
        # Frozen dataclasses store fields in __dataclass_fields__
        assert len(status.__dataclass_fields__) == 15


class TestTrackingStatusIsSynchronized:
    """Tests for TrackingStatus.is_synchronized() method."""

    def test_synchronized_when_ref_id_nonzero_and_stratum_valid(self):
        """Test is_synchronized returns True when ref_id != 0 and stratum < 16."""
        status = make_tracking()
        assert status.is_synchronized() is True

    def test_not_synchronized_when_ref_id_zero(self):
        """Test is_synchronized returns False when ref_id == 0."""
        status = make_tracking(
            reference_id=0,
            reference_id_name="",
            stratum=16,
            leap_status=LeapStatus.UNSYNC,
        )
        assert status.is_synchronized() is False

    def test_not_synchronized_when_stratum_16(self):
        """Test is_synchronized returns False when stratum == 16."""
        status = make_tracking(stratum=16)
        assert status.is_synchronized() is False

    def test_synchronized_at_stratum_boundary(self):
        """Test is_synchronized returns True at stratum 15."""
        status = make_tracking(stratum=15)
        assert status.is_synchronized() is True

    def test_synchronized_at_stratum_zero(self):
        """Test is_synchronized returns True at stratum 0 (reference clock)."""
        status = make_tracking(stratum=0)
        assert status.is_synchronized() is True


class TestTrackingStatusIsLeapPending:
    """Tests for TrackingStatus.is_leap_pending() method."""

    def test_no_leap_when_status_zero(self):
        """Test is_leap_pending returns False when leap_status == 0."""
        status = make_tracking()
        assert status.is_leap_pending() is False

    def test_leap_pending_when_insert(self):
        """Test is_leap_pending returns True when leap_status == 1 (insert)."""
        status = make_tracking(leap_status=LeapStatus.INSERT)
        assert status.is_leap_pending() is True

    def test_leap_pending_when_delete(self):
        """Test is_leap_pending returns True when leap_status is DELETE."""
        status = make_tracking(leap_status=LeapStatus.DELETE)
        assert status.is_leap_pending() is True

    def test_no_leap_when_unsync(self):
        """Test is_leap_pending returns False when leap_status is UNSYNC."""
        status = make_tracking(leap_status=LeapStatus.UNSYNC)
        assert status.is_leap_pending() is False


class TestRefIdToName:
    """Tests for _ref_id_to_name() helper function."""

    def test_ip_address_conversion(self):
        """Test conversion of IP address reference ID."""
        # 127.0.0.1 = 0x7F000001
        result = _ref_id_to_name(0x7F000001)
        assert result == "127.0.0.1"

    def test_ascii_name_conversion(self):
        """Test conversion of ASCII reference clock name."""
        # "GPS\0" = 0x47505300
        result = _ref_id_to_name(0x47505300)
        assert result == "GPS"

    def test_pps_name_conversion(self):
        """Test conversion of PPS reference clock name."""
        # "PPS\0" = 0x50505300
        result = _ref_id_to_name(0x50505300)
        assert result == "PPS"

    def test_locl_name_conversion(self):
        """Test conversion of LOCAL reference clock name."""
        # "LOCL" = 0x4C4F434C
        result = _ref_id_to_name(0x4C4F434C)
        assert result == "LOCL"

    def test_zero_ref_id(self):
        """Test conversion of zero reference ID."""
        result = _ref_id_to_name(0)
        assert result == ""

    def test_public_ip_address(self):
        """Test conversion of public IP address."""
        # 8.8.8.8 = 0x08080808
        result = _ref_id_to_name(0x08080808)
        assert result == "8.8.8.8"

    def test_high_octet_ip(self):
        """Test conversion of IP with high octets."""
        # 192.168.1.1 = 0xC0A80101
        result = _ref_id_to_name(0xC0A80101)
        assert result == "192.168.1.1"


class TestSource:
    """Tests for Source dataclass."""

    def test_creation_with_all_fields(self):
        """Test creating Source with all required fields."""
        source = make_source()

        assert source.address == SOURCE_DEFAULTS["address"]
        assert source.poll == SOURCE_DEFAULTS["poll"]
        assert source.stratum == SOURCE_DEFAULTS["stratum"]
        assert source.state == SOURCE_DEFAULTS["state"]
        assert source.mode == SOURCE_DEFAULTS["mode"]
        assert source.flags == SOURCE_DEFAULTS["flags"]
        assert source.reachability == SOURCE_DEFAULTS["reachability"]
        assert source.last_sample_ago == SOURCE_DEFAULTS["last_sample_ago"]
        assert source.orig_latest_meas == SOURCE_DEFAULTS["orig_latest_meas"]
        assert source.latest_meas == SOURCE_DEFAULTS["latest_meas"]
        assert source.latest_meas_err == SOURCE_DEFAULTS["latest_meas_err"]

    def test_is_frozen(self):
        """Test that Source is immutable (frozen)."""
        source = make_source()

        with pytest.raises(FrozenInstanceError):
            source.address = "new.address.com"

    def test_has_correct_field_count(self):
        """Test that Source has exactly 11 fields."""
        source = make_source()
        assert len(source.__dataclass_fields__) == 11


class TestSourceIsReachable:
    """Tests for Source.is_reachable() method."""

    def test_reachable_when_nonzero(self):
        """Test is_reachable returns True when reachability > 0."""
        source = make_source()
        assert source.is_reachable() is True

    def test_not_reachable_when_zero(self):
        """Test is_reachable returns False when reachability == 0."""
        source = make_source(reachability=0)
        assert source.is_reachable() is False

    def test_reachable_with_partial_reach(self):
        """Test is_reachable returns True with partial reachability."""
        source = make_source(reachability=1)  # Only one recent poll succeeded
        assert source.is_reachable() is True


class TestSourceIsSelected:
    """Tests for Source.is_selected() method."""

    def test_selected_when_state_zero(self):
        """Test is_selected returns True when state == 0."""
        source = make_source()
        assert source.is_selected() is True

    def test_not_selected_when_state_not_selected(self):
        """Test is_selected returns False when state != SELECTED."""
        non_selected_states = [
            SourceState.NONSELECTABLE,
            SourceState.FALSETICKER,
            SourceState.JITTERY,
            SourceState.UNSELECTED,
            SourceState.SELECTABLE,
        ]
        for state in non_selected_states:
            source = make_source(state=state)
            assert source.is_selected() is False


class TestSourceEnumProperties:
    """Tests for Source enum field properties."""

    def test_state_name_via_enum(self):
        """Test state.name returns uppercase string."""
        source = make_source()
        assert source.state.name == "SELECTED"

    def test_mode_name_via_enum(self):
        """Test mode.name returns uppercase string."""
        source = make_source()
        assert source.mode.name == "CLIENT"

    def test_state_values(self):
        """Test state enum values match expected integers."""
        for state in SourceState:
            source = make_source(state=state)
            assert source.state == state
            assert source.state.value == state.value

    def test_mode_values(self):
        """Test mode enum values match expected integers."""
        for mode in SourceMode:
            source = make_source(mode=mode)
            assert source.mode == mode
            assert source.mode.value == mode.value


class TestSourceStats:
    """Tests for SourceStats dataclass."""

    def test_creation_with_all_fields(self):
        """Test creating SourceStats with all required fields."""
        stats = make_source_stats()

        assert stats.reference_id == SOURCESTATS_DEFAULTS["reference_id"]
        assert stats.address == SOURCESTATS_DEFAULTS["address"]
        assert stats.samples == SOURCESTATS_DEFAULTS["samples"]
        assert stats.runs == SOURCESTATS_DEFAULTS["runs"]
        assert stats.span == SOURCESTATS_DEFAULTS["span"]
        assert stats.std_dev == SOURCESTATS_DEFAULTS["std_dev"]
        assert stats.resid_freq == SOURCESTATS_DEFAULTS["resid_freq"]
        assert stats.skew == SOURCESTATS_DEFAULTS["skew"]
        assert stats.offset == SOURCESTATS_DEFAULTS["offset"]
        assert stats.offset_err == SOURCESTATS_DEFAULTS["offset_err"]

    def test_is_frozen(self):
        """Test that SourceStats is immutable (frozen)."""
        stats = make_source_stats()

        with pytest.raises(FrozenInstanceError):
            stats.samples = 100

    def test_has_correct_field_count(self):
        """Test that SourceStats has exactly 10 fields."""
        stats = make_source_stats()
        assert len(stats.__dataclass_fields__) == 10


class TestSourceStatsHasSufficientSamples:
    """Tests for SourceStats.has_sufficient_samples() method."""

    def test_sufficient_with_default_minimum(self):
        """Test has_sufficient_samples with default minimum (4)."""
        stats = make_source_stats()
        assert stats.has_sufficient_samples() is True

    def test_insufficient_below_default_minimum(self):
        """Test has_sufficient_samples returns False below default minimum."""
        stats = make_source_stats(samples=3)
        assert stats.has_sufficient_samples() is False

    def test_sufficient_at_boundary(self):
        """Test has_sufficient_samples at exact minimum."""
        stats = make_source_stats(samples=4)
        assert stats.has_sufficient_samples() is True

    def test_custom_minimum(self):
        """Test has_sufficient_samples with custom minimum."""
        stats = make_source_stats()
        assert stats.has_sufficient_samples(minimum=8) is True
        assert stats.has_sufficient_samples(minimum=10) is False


class TestRTCData:
    """Tests for RTCData dataclass."""

    def test_creation_with_all_fields(self):
        """Test creating RTCData with all required fields."""
        rtc = make_rtc_data()

        assert rtc.ref_time == RTCDATA_DEFAULTS["ref_time"]
        assert rtc.samples == RTCDATA_DEFAULTS["samples"]
        assert rtc.runs == RTCDATA_DEFAULTS["runs"]
        assert rtc.span == RTCDATA_DEFAULTS["span"]
        assert rtc.offset == RTCDATA_DEFAULTS["offset"]
        assert rtc.freq_offset == RTCDATA_DEFAULTS["freq_offset"]

    def test_is_frozen(self):
        """Test that RTCData is immutable (frozen)."""
        rtc = make_rtc_data()

        with pytest.raises(FrozenInstanceError):
            rtc.offset = 0.0

    def test_has_correct_field_count(self):
        """Test that RTCData has exactly 6 fields."""
        rtc = make_rtc_data()
        assert len(rtc.__dataclass_fields__) == 6


class TestRTCDataIsCalibrated:
    """Tests for RTCData.is_calibrated() method."""

    def test_calibrated_when_samples_positive(self):
        """Test is_calibrated returns True when samples > 0."""
        rtc = make_rtc_data()
        assert rtc.is_calibrated() is True

    def test_not_calibrated_when_samples_zero(self):
        """Test is_calibrated returns False when samples == 0."""
        rtc = make_rtc_data(samples=0)
        assert rtc.is_calibrated() is False
