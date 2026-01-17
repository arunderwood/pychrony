"""Unit tests for pychrony data models."""

import pytest
from dataclasses import FrozenInstanceError

from pychrony.models import (
    TrackingStatus,
    Source,
    SourceStats,
    RTCData,
    _ref_id_to_name,
)


class TestTrackingStatus:
    """Tests for TrackingStatus dataclass."""

    def test_creation_with_all_fields(self, sample_tracking_data):
        """Test creating TrackingStatus with all required fields."""
        status = TrackingStatus(**sample_tracking_data)

        assert status.reference_id == sample_tracking_data["reference_id"]
        assert status.reference_id_name == sample_tracking_data["reference_id_name"]
        assert status.reference_ip == sample_tracking_data["reference_ip"]
        assert status.stratum == sample_tracking_data["stratum"]
        assert status.leap_status == sample_tracking_data["leap_status"]
        assert status.ref_time == sample_tracking_data["ref_time"]
        assert status.offset == sample_tracking_data["offset"]
        assert status.last_offset == sample_tracking_data["last_offset"]
        assert status.rms_offset == sample_tracking_data["rms_offset"]
        assert status.frequency == sample_tracking_data["frequency"]
        assert status.residual_freq == sample_tracking_data["residual_freq"]
        assert status.skew == sample_tracking_data["skew"]
        assert status.root_delay == sample_tracking_data["root_delay"]
        assert status.root_dispersion == sample_tracking_data["root_dispersion"]
        assert status.update_interval == sample_tracking_data["update_interval"]

    def test_is_frozen(self, sample_tracking_data):
        """Test that TrackingStatus is immutable (frozen)."""
        status = TrackingStatus(**sample_tracking_data)

        with pytest.raises(FrozenInstanceError):
            status.offset = 0.001

    def test_has_correct_field_count(self, sample_tracking_data):
        """Test that TrackingStatus has exactly 15 fields."""
        status = TrackingStatus(**sample_tracking_data)
        # Frozen dataclasses store fields in __dataclass_fields__
        assert len(status.__dataclass_fields__) == 15


class TestTrackingStatusIsSynchronized:
    """Tests for TrackingStatus.is_synchronized() method."""

    def test_synchronized_when_ref_id_nonzero_and_stratum_valid(
        self, sample_tracking_data
    ):
        """Test is_synchronized returns True when ref_id != 0 and stratum < 16."""
        status = TrackingStatus(**sample_tracking_data)
        assert status.is_synchronized() is True

    def test_not_synchronized_when_ref_id_zero(self, unsynchronized_tracking_data):
        """Test is_synchronized returns False when ref_id == 0."""
        status = TrackingStatus(**unsynchronized_tracking_data)
        assert status.is_synchronized() is False

    def test_not_synchronized_when_stratum_16(self, sample_tracking_data):
        """Test is_synchronized returns False when stratum == 16."""
        data = sample_tracking_data.copy()
        data["stratum"] = 16
        status = TrackingStatus(**data)
        assert status.is_synchronized() is False

    def test_synchronized_at_stratum_boundary(self, sample_tracking_data):
        """Test is_synchronized returns True at stratum 15."""
        data = sample_tracking_data.copy()
        data["stratum"] = 15
        status = TrackingStatus(**data)
        assert status.is_synchronized() is True

    def test_synchronized_at_stratum_zero(self, sample_tracking_data):
        """Test is_synchronized returns True at stratum 0 (reference clock)."""
        data = sample_tracking_data.copy()
        data["stratum"] = 0
        status = TrackingStatus(**data)
        assert status.is_synchronized() is True


class TestTrackingStatusIsLeapPending:
    """Tests for TrackingStatus.is_leap_pending() method."""

    def test_no_leap_when_status_zero(self, sample_tracking_data):
        """Test is_leap_pending returns False when leap_status == 0."""
        status = TrackingStatus(**sample_tracking_data)
        assert status.is_leap_pending() is False

    def test_leap_pending_when_insert(self, leap_pending_tracking_data):
        """Test is_leap_pending returns True when leap_status == 1 (insert)."""
        status = TrackingStatus(**leap_pending_tracking_data)
        assert status.is_leap_pending() is True

    def test_leap_pending_when_delete(self, sample_tracking_data):
        """Test is_leap_pending returns True when leap_status == 2 (delete)."""
        data = sample_tracking_data.copy()
        data["leap_status"] = 2
        status = TrackingStatus(**data)
        assert status.is_leap_pending() is True

    def test_no_leap_when_unsync(self, sample_tracking_data):
        """Test is_leap_pending returns False when leap_status == 3 (unsync)."""
        data = sample_tracking_data.copy()
        data["leap_status"] = 3
        status = TrackingStatus(**data)
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

    def test_creation_with_all_fields(self, sample_source_data):
        """Test creating Source with all required fields."""
        source = Source(**sample_source_data)

        assert source.address == sample_source_data["address"]
        assert source.poll == sample_source_data["poll"]
        assert source.stratum == sample_source_data["stratum"]
        assert source.state == sample_source_data["state"]
        assert source.mode == sample_source_data["mode"]
        assert source.flags == sample_source_data["flags"]
        assert source.reachability == sample_source_data["reachability"]
        assert source.last_sample_ago == sample_source_data["last_sample_ago"]
        assert source.orig_latest_meas == sample_source_data["orig_latest_meas"]
        assert source.latest_meas == sample_source_data["latest_meas"]
        assert source.latest_meas_err == sample_source_data["latest_meas_err"]

    def test_is_frozen(self, sample_source_data):
        """Test that Source is immutable (frozen)."""
        source = Source(**sample_source_data)

        with pytest.raises(FrozenInstanceError):
            source.address = "new.address.com"

    def test_has_correct_field_count(self, sample_source_data):
        """Test that Source has exactly 11 fields."""
        source = Source(**sample_source_data)
        assert len(source.__dataclass_fields__) == 11


class TestSourceIsReachable:
    """Tests for Source.is_reachable() method."""

    def test_reachable_when_nonzero(self, sample_source_data):
        """Test is_reachable returns True when reachability > 0."""
        source = Source(**sample_source_data)
        assert source.is_reachable() is True

    def test_not_reachable_when_zero(self, sample_source_data):
        """Test is_reachable returns False when reachability == 0."""
        data = sample_source_data.copy()
        data["reachability"] = 0
        source = Source(**data)
        assert source.is_reachable() is False

    def test_reachable_with_partial_reach(self, sample_source_data):
        """Test is_reachable returns True with partial reachability."""
        data = sample_source_data.copy()
        data["reachability"] = 1  # Only one recent poll succeeded
        source = Source(**data)
        assert source.is_reachable() is True


class TestSourceIsSelected:
    """Tests for Source.is_selected() method."""

    def test_selected_when_state_zero(self, sample_source_data):
        """Test is_selected returns True when state == 0."""
        source = Source(**sample_source_data)
        assert source.is_selected() is True

    def test_not_selected_when_state_nonzero(self, sample_source_data):
        """Test is_selected returns False when state != 0."""
        for state in range(1, 6):
            data = sample_source_data.copy()
            data["state"] = state
            source = Source(**data)
            assert source.is_selected() is False


class TestSourceModeName:
    """Tests for Source.mode_name property."""

    def test_mode_client(self, sample_source_data):
        """Test mode_name returns 'client' for mode 0."""
        data = sample_source_data.copy()
        data["mode"] = 0
        source = Source(**data)
        assert source.mode_name == "client"

    def test_mode_peer(self, sample_source_data):
        """Test mode_name returns 'peer' for mode 1."""
        data = sample_source_data.copy()
        data["mode"] = 1
        source = Source(**data)
        assert source.mode_name == "peer"

    def test_mode_refclock(self, sample_source_data):
        """Test mode_name returns 'reference clock' for mode 2."""
        data = sample_source_data.copy()
        data["mode"] = 2
        source = Source(**data)
        assert source.mode_name == "reference clock"

    def test_mode_unknown(self, sample_source_data):
        """Test mode_name returns 'unknown(N)' for unknown modes."""
        data = sample_source_data.copy()
        data["mode"] = 99
        source = Source(**data)
        assert source.mode_name == "unknown(99)"


class TestSourceStateName:
    """Tests for Source.state_name property."""

    def test_state_selected(self, sample_source_data):
        """Test state_name returns 'selected' for state 0."""
        data = sample_source_data.copy()
        data["state"] = 0
        source = Source(**data)
        assert source.state_name == "selected"

    def test_state_nonselectable(self, sample_source_data):
        """Test state_name returns 'nonselectable' for state 1."""
        data = sample_source_data.copy()
        data["state"] = 1
        source = Source(**data)
        assert source.state_name == "nonselectable"

    def test_state_falseticker(self, sample_source_data):
        """Test state_name returns 'falseticker' for state 2."""
        data = sample_source_data.copy()
        data["state"] = 2
        source = Source(**data)
        assert source.state_name == "falseticker"

    def test_state_jittery(self, sample_source_data):
        """Test state_name returns 'jittery' for state 3."""
        data = sample_source_data.copy()
        data["state"] = 3
        source = Source(**data)
        assert source.state_name == "jittery"

    def test_state_unselected(self, sample_source_data):
        """Test state_name returns 'unselected' for state 4."""
        data = sample_source_data.copy()
        data["state"] = 4
        source = Source(**data)
        assert source.state_name == "unselected"

    def test_state_selectable(self, sample_source_data):
        """Test state_name returns 'selectable' for state 5."""
        data = sample_source_data.copy()
        data["state"] = 5
        source = Source(**data)
        assert source.state_name == "selectable"

    def test_state_unknown(self, sample_source_data):
        """Test state_name returns 'unknown(N)' for unknown states."""
        data = sample_source_data.copy()
        data["state"] = 99
        source = Source(**data)
        assert source.state_name == "unknown(99)"


class TestSourceStats:
    """Tests for SourceStats dataclass."""

    def test_creation_with_all_fields(self, sample_sourcestats_data):
        """Test creating SourceStats with all required fields."""
        stats = SourceStats(**sample_sourcestats_data)

        assert stats.reference_id == sample_sourcestats_data["reference_id"]
        assert stats.address == sample_sourcestats_data["address"]
        assert stats.samples == sample_sourcestats_data["samples"]
        assert stats.runs == sample_sourcestats_data["runs"]
        assert stats.span == sample_sourcestats_data["span"]
        assert stats.std_dev == sample_sourcestats_data["std_dev"]
        assert stats.resid_freq == sample_sourcestats_data["resid_freq"]
        assert stats.skew == sample_sourcestats_data["skew"]
        assert stats.offset == sample_sourcestats_data["offset"]
        assert stats.offset_err == sample_sourcestats_data["offset_err"]

    def test_is_frozen(self, sample_sourcestats_data):
        """Test that SourceStats is immutable (frozen)."""
        stats = SourceStats(**sample_sourcestats_data)

        with pytest.raises(FrozenInstanceError):
            stats.samples = 100

    def test_has_correct_field_count(self, sample_sourcestats_data):
        """Test that SourceStats has exactly 10 fields."""
        stats = SourceStats(**sample_sourcestats_data)
        assert len(stats.__dataclass_fields__) == 10


class TestSourceStatsHasSufficientSamples:
    """Tests for SourceStats.has_sufficient_samples() method."""

    def test_sufficient_with_default_minimum(self, sample_sourcestats_data):
        """Test has_sufficient_samples with default minimum (4)."""
        stats = SourceStats(**sample_sourcestats_data)
        assert stats.has_sufficient_samples() is True

    def test_insufficient_below_default_minimum(self, sample_sourcestats_data):
        """Test has_sufficient_samples returns False below default minimum."""
        data = sample_sourcestats_data.copy()
        data["samples"] = 3
        stats = SourceStats(**data)
        assert stats.has_sufficient_samples() is False

    def test_sufficient_at_boundary(self, sample_sourcestats_data):
        """Test has_sufficient_samples at exact minimum."""
        data = sample_sourcestats_data.copy()
        data["samples"] = 4
        stats = SourceStats(**data)
        assert stats.has_sufficient_samples() is True

    def test_custom_minimum(self, sample_sourcestats_data):
        """Test has_sufficient_samples with custom minimum."""
        stats = SourceStats(**sample_sourcestats_data)
        assert stats.has_sufficient_samples(minimum=8) is True
        assert stats.has_sufficient_samples(minimum=10) is False


class TestRTCData:
    """Tests for RTCData dataclass."""

    def test_creation_with_all_fields(self, sample_rtcdata):
        """Test creating RTCData with all required fields."""
        rtc = RTCData(**sample_rtcdata)

        assert rtc.ref_time == sample_rtcdata["ref_time"]
        assert rtc.samples == sample_rtcdata["samples"]
        assert rtc.runs == sample_rtcdata["runs"]
        assert rtc.span == sample_rtcdata["span"]
        assert rtc.offset == sample_rtcdata["offset"]
        assert rtc.freq_offset == sample_rtcdata["freq_offset"]

    def test_is_frozen(self, sample_rtcdata):
        """Test that RTCData is immutable (frozen)."""
        rtc = RTCData(**sample_rtcdata)

        with pytest.raises(FrozenInstanceError):
            rtc.offset = 0.0

    def test_has_correct_field_count(self, sample_rtcdata):
        """Test that RTCData has exactly 6 fields."""
        rtc = RTCData(**sample_rtcdata)
        assert len(rtc.__dataclass_fields__) == 6


class TestRTCDataIsCalibrated:
    """Tests for RTCData.is_calibrated() method."""

    def test_calibrated_when_samples_positive(self, sample_rtcdata):
        """Test is_calibrated returns True when samples > 0."""
        rtc = RTCData(**sample_rtcdata)
        assert rtc.is_calibrated() is True

    def test_not_calibrated_when_samples_zero(self, sample_rtcdata):
        """Test is_calibrated returns False when samples == 0."""
        data = sample_rtcdata.copy()
        data["samples"] = 0
        rtc = RTCData(**data)
        assert rtc.is_calibrated() is False
