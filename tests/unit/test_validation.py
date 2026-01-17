"""Unit tests for field validation in pychrony."""

import pytest

from pychrony.exceptions import ChronyDataError
from pychrony._core._bindings import (
    _validate_tracking,
    _validate_finite_float,
    _validate_bounded_int,
    _validate_non_negative_int,
    _validate_source,
    _validate_sourcestats,
    _validate_rtc,
)


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

    # Note: leap_status validation is now handled by enum conversion
    # in _extract_tracking_fields, not in _validate_tracking

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


class TestValidateFiniteFloat:
    """Tests for _validate_finite_float() function."""

    def test_valid_float_passes(self):
        """Test that a valid float passes validation."""
        _validate_finite_float(1.234, "test_field")  # Should not raise

    def test_nan_rejected(self):
        """Test that NaN is rejected."""
        with pytest.raises(ChronyDataError) as exc_info:
            _validate_finite_float(float("nan"), "test_field")
        assert "Invalid test_field" in str(exc_info.value)

    def test_inf_rejected(self):
        """Test that positive infinity is rejected."""
        with pytest.raises(ChronyDataError) as exc_info:
            _validate_finite_float(float("inf"), "test_field")
        assert "Invalid test_field" in str(exc_info.value)

    def test_neg_inf_rejected(self):
        """Test that negative infinity is rejected."""
        with pytest.raises(ChronyDataError) as exc_info:
            _validate_finite_float(float("-inf"), "test_field")
        assert "Invalid test_field" in str(exc_info.value)

    def test_zero_passes(self):
        """Test that zero passes validation."""
        _validate_finite_float(0.0, "test_field")  # Should not raise

    def test_negative_float_passes(self):
        """Test that negative floats pass validation."""
        _validate_finite_float(-1.234, "test_field")  # Should not raise


class TestValidateBoundedInt:
    """Tests for _validate_bounded_int() function."""

    def test_valid_in_bounds_passes(self):
        """Test that a value within bounds passes validation."""
        _validate_bounded_int(5, "test_field", 0, 10)  # Should not raise

    def test_at_lower_bound_passes(self):
        """Test that a value at lower bound passes validation."""
        _validate_bounded_int(0, "test_field", 0, 10)  # Should not raise

    def test_at_upper_bound_passes(self):
        """Test that a value at upper bound passes validation."""
        _validate_bounded_int(10, "test_field", 0, 10)  # Should not raise

    def test_below_lower_bound_rejected(self):
        """Test that a value below lower bound is rejected."""
        with pytest.raises(ChronyDataError) as exc_info:
            _validate_bounded_int(-1, "test_field", 0, 10)
        assert "Invalid test_field" in str(exc_info.value)

    def test_above_upper_bound_rejected(self):
        """Test that a value above upper bound is rejected."""
        with pytest.raises(ChronyDataError) as exc_info:
            _validate_bounded_int(11, "test_field", 0, 10)
        assert "Invalid test_field" in str(exc_info.value)


class TestValidateNonNegativeInt:
    """Tests for _validate_non_negative_int() function."""

    def test_positive_passes(self):
        """Test that a positive integer passes validation."""
        _validate_non_negative_int(5, "test_field")  # Should not raise

    def test_zero_passes(self):
        """Test that zero passes validation."""
        _validate_non_negative_int(0, "test_field")  # Should not raise

    def test_negative_rejected(self):
        """Test that a negative integer is rejected."""
        with pytest.raises(ChronyDataError) as exc_info:
            _validate_non_negative_int(-1, "test_field")
        assert "must be non-negative" in str(exc_info.value)


class TestValidateSource:
    """Tests for _validate_source() function."""

    def test_valid_data_passes(self, sample_source_data):
        """Test that valid source data passes validation."""
        _validate_source(sample_source_data)  # Should not raise

    # Note: mode and state validation is now handled by enum conversion
    # in _get_source_from_record, not in _validate_source

    def test_invalid_stratum_rejected(self, sample_source_data):
        """Test that invalid stratum is rejected."""
        data = sample_source_data.copy()
        data["stratum"] = 16  # Invalid (only 0-15 valid)
        with pytest.raises(ChronyDataError) as exc_info:
            _validate_source(data)
        assert "Invalid stratum" in str(exc_info.value)

    def test_invalid_reachability_rejected(self, sample_source_data):
        """Test that invalid reachability is rejected."""
        data = sample_source_data.copy()
        data["reachability"] = 256  # Invalid (only 0-255 valid)
        with pytest.raises(ChronyDataError) as exc_info:
            _validate_source(data)
        assert "Invalid reachability" in str(exc_info.value)

    def test_negative_last_sample_ago_rejected(self, sample_source_data):
        """Test that negative last_sample_ago is rejected."""
        data = sample_source_data.copy()
        data["last_sample_ago"] = -1
        with pytest.raises(ChronyDataError) as exc_info:
            _validate_source(data)
        assert "must be non-negative" in str(exc_info.value)

    def test_nan_latest_meas_rejected(self, sample_source_data):
        """Test that NaN latest_meas is rejected."""
        data = sample_source_data.copy()
        data["latest_meas"] = float("nan")
        with pytest.raises(ChronyDataError) as exc_info:
            _validate_source(data)
        assert "Invalid latest_meas" in str(exc_info.value)

    def test_negative_latest_meas_err_rejected(self, sample_source_data):
        """Test that negative latest_meas_err is rejected."""
        data = sample_source_data.copy()
        data["latest_meas_err"] = -0.001
        with pytest.raises(ChronyDataError) as exc_info:
            _validate_source(data)
        assert "must be non-negative" in str(exc_info.value)


class TestValidateSourcestats:
    """Tests for _validate_sourcestats() function."""

    def test_valid_data_passes(self, sample_sourcestats_data):
        """Test that valid sourcestats data passes validation."""
        _validate_sourcestats(sample_sourcestats_data)  # Should not raise

    def test_negative_samples_rejected(self, sample_sourcestats_data):
        """Test that negative samples is rejected."""
        data = sample_sourcestats_data.copy()
        data["samples"] = -1
        with pytest.raises(ChronyDataError) as exc_info:
            _validate_sourcestats(data)
        assert "must be non-negative" in str(exc_info.value)

    def test_negative_runs_rejected(self, sample_sourcestats_data):
        """Test that negative runs is rejected."""
        data = sample_sourcestats_data.copy()
        data["runs"] = -1
        with pytest.raises(ChronyDataError) as exc_info:
            _validate_sourcestats(data)
        assert "must be non-negative" in str(exc_info.value)

    def test_negative_span_rejected(self, sample_sourcestats_data):
        """Test that negative span is rejected."""
        data = sample_sourcestats_data.copy()
        data["span"] = -1
        with pytest.raises(ChronyDataError) as exc_info:
            _validate_sourcestats(data)
        assert "must be non-negative" in str(exc_info.value)

    def test_nan_offset_rejected(self, sample_sourcestats_data):
        """Test that NaN offset is rejected."""
        data = sample_sourcestats_data.copy()
        data["offset"] = float("nan")
        with pytest.raises(ChronyDataError) as exc_info:
            _validate_sourcestats(data)
        assert "Invalid offset" in str(exc_info.value)

    def test_negative_std_dev_rejected(self, sample_sourcestats_data):
        """Test that negative std_dev is rejected."""
        data = sample_sourcestats_data.copy()
        data["std_dev"] = -0.001
        with pytest.raises(ChronyDataError) as exc_info:
            _validate_sourcestats(data)
        assert "must be non-negative" in str(exc_info.value)

    def test_negative_skew_rejected(self, sample_sourcestats_data):
        """Test that negative skew is rejected."""
        data = sample_sourcestats_data.copy()
        data["skew"] = -0.001
        with pytest.raises(ChronyDataError) as exc_info:
            _validate_sourcestats(data)
        assert "must be non-negative" in str(exc_info.value)

    def test_negative_offset_err_rejected(self, sample_sourcestats_data):
        """Test that negative offset_err is rejected."""
        data = sample_sourcestats_data.copy()
        data["offset_err"] = -0.001
        with pytest.raises(ChronyDataError) as exc_info:
            _validate_sourcestats(data)
        assert "must be non-negative" in str(exc_info.value)

    def test_negative_offset_allowed(self, sample_sourcestats_data):
        """Test that negative offset is allowed (valid)."""
        data = sample_sourcestats_data.copy()
        data["offset"] = -0.001
        _validate_sourcestats(data)  # Should not raise

    def test_negative_resid_freq_allowed(self, sample_sourcestats_data):
        """Test that negative resid_freq is allowed (valid)."""
        data = sample_sourcestats_data.copy()
        data["resid_freq"] = -1.0
        _validate_sourcestats(data)  # Should not raise


class TestValidateRtc:
    """Tests for _validate_rtc() function."""

    def test_valid_data_passes(self, sample_rtcdata):
        """Test that valid RTC data passes validation."""
        _validate_rtc(sample_rtcdata)  # Should not raise

    def test_negative_samples_rejected(self, sample_rtcdata):
        """Test that negative samples is rejected."""
        data = sample_rtcdata.copy()
        data["samples"] = -1
        with pytest.raises(ChronyDataError) as exc_info:
            _validate_rtc(data)
        assert "must be non-negative" in str(exc_info.value)

    def test_negative_runs_rejected(self, sample_rtcdata):
        """Test that negative runs is rejected."""
        data = sample_rtcdata.copy()
        data["runs"] = -1
        with pytest.raises(ChronyDataError) as exc_info:
            _validate_rtc(data)
        assert "must be non-negative" in str(exc_info.value)

    def test_negative_span_rejected(self, sample_rtcdata):
        """Test that negative span is rejected."""
        data = sample_rtcdata.copy()
        data["span"] = -1
        with pytest.raises(ChronyDataError) as exc_info:
            _validate_rtc(data)
        assert "must be non-negative" in str(exc_info.value)

    def test_nan_offset_rejected(self, sample_rtcdata):
        """Test that NaN offset is rejected."""
        data = sample_rtcdata.copy()
        data["offset"] = float("nan")
        with pytest.raises(ChronyDataError) as exc_info:
            _validate_rtc(data)
        assert "Invalid offset" in str(exc_info.value)

    def test_negative_ref_time_rejected(self, sample_rtcdata):
        """Test that negative ref_time is rejected."""
        data = sample_rtcdata.copy()
        data["ref_time"] = -1.0
        with pytest.raises(ChronyDataError) as exc_info:
            _validate_rtc(data)
        assert "must be non-negative" in str(exc_info.value)

    def test_negative_offset_allowed(self, sample_rtcdata):
        """Test that negative offset is allowed (valid)."""
        data = sample_rtcdata.copy()
        data["offset"] = -0.123
        _validate_rtc(data)  # Should not raise

    def test_negative_freq_offset_allowed(self, sample_rtcdata):
        """Test that negative freq_offset is allowed (valid)."""
        data = sample_rtcdata.copy()
        data["freq_offset"] = -2.0
        _validate_rtc(data)  # Should not raise
