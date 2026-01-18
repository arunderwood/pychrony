"""Unit tests for field validation in pychrony."""

import pytest

from pychrony.exceptions import ChronyDataError
from pychrony._core._bindings import (
    _validate_finite_float,
    _validate_bounded_int,
    _validate_non_negative_int,
)


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
