"""Unit tests for pychrony data models."""

import pytest
from dataclasses import FrozenInstanceError

from pychrony.models import TrackingStatus, _ref_id_to_name


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
