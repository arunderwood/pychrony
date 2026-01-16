"""Unit tests for field validation in pychrony."""

import pytest

from pychrony.exceptions import ChronyDataError
from pychrony._core._bindings import _validate_tracking


class TestValidateTracking:
    """Tests for _validate_tracking() function."""

    def test_valid_data_passes(self, sample_tracking_data):
        """Test that valid tracking data passes validation."""
        # Should not raise
        _validate_tracking(sample_tracking_data)

    def test_stratum_too_high(self, sample_tracking_data):
        """Test that stratum > 15 raises ChronyDataError."""
        data = sample_tracking_data.copy()
        data["stratum"] = 16
        with pytest.raises(ChronyDataError) as exc_info:
            _validate_tracking(data)
        assert "Invalid stratum" in str(exc_info.value)

    def test_stratum_negative(self, sample_tracking_data):
        """Test that negative stratum raises ChronyDataError."""
        data = sample_tracking_data.copy()
        data["stratum"] = -1
        with pytest.raises(ChronyDataError) as exc_info:
            _validate_tracking(data)
        assert "Invalid stratum" in str(exc_info.value)

    def test_stratum_boundary_valid(self, sample_tracking_data):
        """Test that stratum 0 and 15 are valid."""
        data = sample_tracking_data.copy()
        data["stratum"] = 0
        _validate_tracking(data)  # Should not raise

        data["stratum"] = 15
        _validate_tracking(data)  # Should not raise

    def test_leap_status_too_high(self, sample_tracking_data):
        """Test that leap_status > 3 raises ChronyDataError."""
        data = sample_tracking_data.copy()
        data["leap_status"] = 4
        with pytest.raises(ChronyDataError) as exc_info:
            _validate_tracking(data)
        assert "Invalid leap_status" in str(exc_info.value)

    def test_leap_status_negative(self, sample_tracking_data):
        """Test that negative leap_status raises ChronyDataError."""
        data = sample_tracking_data.copy()
        data["leap_status"] = -1
        with pytest.raises(ChronyDataError) as exc_info:
            _validate_tracking(data)
        assert "Invalid leap_status" in str(exc_info.value)

    def test_leap_status_boundary_valid(self, sample_tracking_data):
        """Test that leap_status 0 and 3 are valid."""
        data = sample_tracking_data.copy()
        data["leap_status"] = 0
        _validate_tracking(data)  # Should not raise

        data["leap_status"] = 3
        _validate_tracking(data)  # Should not raise

    def test_nan_float_field_rejected(self, sample_tracking_data):
        """Test that NaN values are rejected."""
        data = sample_tracking_data.copy()
        data["offset"] = float("nan")
        with pytest.raises(ChronyDataError) as exc_info:
            _validate_tracking(data)
        assert "Invalid offset" in str(exc_info.value)

    def test_inf_float_field_rejected(self, sample_tracking_data):
        """Test that infinity values are rejected."""
        data = sample_tracking_data.copy()
        data["frequency"] = float("inf")
        with pytest.raises(ChronyDataError) as exc_info:
            _validate_tracking(data)
        assert "Invalid frequency" in str(exc_info.value)

    def test_negative_inf_float_field_rejected(self, sample_tracking_data):
        """Test that negative infinity values are rejected."""
        data = sample_tracking_data.copy()
        data["skew"] = float("-inf")
        with pytest.raises(ChronyDataError) as exc_info:
            _validate_tracking(data)
        assert "Invalid skew" in str(exc_info.value)

    def test_negative_rms_offset_rejected(self, sample_tracking_data):
        """Test that negative rms_offset is rejected."""
        data = sample_tracking_data.copy()
        data["rms_offset"] = -0.001
        with pytest.raises(ChronyDataError) as exc_info:
            _validate_tracking(data)
        assert "must be non-negative" in str(exc_info.value)

    def test_negative_root_delay_rejected(self, sample_tracking_data):
        """Test that negative root_delay is rejected."""
        data = sample_tracking_data.copy()
        data["root_delay"] = -0.001
        with pytest.raises(ChronyDataError) as exc_info:
            _validate_tracking(data)
        assert "must be non-negative" in str(exc_info.value)

    def test_negative_root_dispersion_rejected(self, sample_tracking_data):
        """Test that negative root_dispersion is rejected."""
        data = sample_tracking_data.copy()
        data["root_dispersion"] = -0.001
        with pytest.raises(ChronyDataError) as exc_info:
            _validate_tracking(data)
        assert "must be non-negative" in str(exc_info.value)

    def test_negative_update_interval_rejected(self, sample_tracking_data):
        """Test that negative update_interval is rejected."""
        data = sample_tracking_data.copy()
        data["update_interval"] = -1.0
        with pytest.raises(ChronyDataError) as exc_info:
            _validate_tracking(data)
        assert "must be non-negative" in str(exc_info.value)

    def test_negative_offset_allowed(self, sample_tracking_data):
        """Test that negative offset is allowed (valid)."""
        data = sample_tracking_data.copy()
        data["offset"] = -0.001
        _validate_tracking(data)  # Should not raise

    def test_negative_frequency_allowed(self, sample_tracking_data):
        """Test that negative frequency is allowed (valid)."""
        data = sample_tracking_data.copy()
        data["frequency"] = -5.0
        _validate_tracking(data)  # Should not raise

    def test_negative_last_offset_allowed(self, sample_tracking_data):
        """Test that negative last_offset is allowed (valid)."""
        data = sample_tracking_data.copy()
        data["last_offset"] = -0.002
        _validate_tracking(data)  # Should not raise
