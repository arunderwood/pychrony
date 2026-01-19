"""Unit tests for mock configuration dataclasses.

Tests for ChronyStateConfig, SourceConfig, and RTCConfig validation
and helper methods.
"""

from __future__ import annotations

import pytest

from pychrony.models import LeapStatus, SourceState
from tests.mocks.config import ChronyStateConfig, SourceConfig, RTCConfig


class TestChronyStateConfigValidation:
    """Test ChronyStateConfig validation."""

    def test_default_config_is_valid(self) -> None:
        """Default configuration should be valid."""
        config = ChronyStateConfig()
        assert config.stratum == 2

    def test_stratum_zero_is_valid(self) -> None:
        """Stratum 0 (reference clock) should be valid."""
        config = ChronyStateConfig(stratum=0)
        assert config.stratum == 0

    def test_stratum_15_is_valid(self) -> None:
        """Stratum 15 boundary should be valid."""
        config = ChronyStateConfig(stratum=15)
        assert config.stratum == 15

    def test_stratum_16_is_valid_for_unsync(self) -> None:
        """Stratum 16 (unsynchronized) should be valid."""
        config = ChronyStateConfig(stratum=16)
        assert config.stratum == 16

    def test_stratum_negative_rejected(self) -> None:
        """Negative stratum should be rejected."""
        with pytest.raises(ValueError, match="stratum must be 0-16"):
            ChronyStateConfig(stratum=-1)

    def test_stratum_17_rejected(self) -> None:
        """Stratum above 16 should be rejected."""
        with pytest.raises(ValueError, match="stratum must be 0-16"):
            ChronyStateConfig(stratum=17)

    def test_negative_rms_offset_rejected(self) -> None:
        """Negative RMS offset should be rejected."""
        with pytest.raises(ValueError, match="rms_offset must be non-negative"):
            ChronyStateConfig(rms_offset=-0.001)

    def test_negative_skew_rejected(self) -> None:
        """Negative skew should be rejected."""
        with pytest.raises(ValueError, match="skew must be non-negative"):
            ChronyStateConfig(skew=-0.001)

    def test_negative_root_delay_rejected(self) -> None:
        """Negative root delay should be rejected."""
        with pytest.raises(ValueError, match="root_delay must be non-negative"):
            ChronyStateConfig(root_delay=-0.001)

    def test_negative_root_dispersion_rejected(self) -> None:
        """Negative root dispersion should be rejected."""
        with pytest.raises(ValueError, match="root_dispersion must be non-negative"):
            ChronyStateConfig(root_dispersion=-0.001)

    def test_negative_update_interval_rejected(self) -> None:
        """Negative update interval should be rejected."""
        with pytest.raises(ValueError, match="update_interval must be non-negative"):
            ChronyStateConfig(update_interval=-1.0)

    def test_negative_ref_time_rejected(self) -> None:
        """Negative reference time should be rejected."""
        with pytest.raises(ValueError, match="ref_time must be non-negative"):
            ChronyStateConfig(ref_time=-1.0)

    def test_invalid_error_injection_key_rejected(self) -> None:
        """Invalid error injection key should be rejected."""
        with pytest.raises(ValueError, match="Invalid error_injection key"):
            ChronyStateConfig(error_injection={"invalid_function": -1})

    def test_valid_error_injection_keys_accepted(self) -> None:
        """Valid error injection keys should be accepted."""
        config = ChronyStateConfig(
            error_injection={
                "chrony_open_socket": -13,
                "chrony_init_session": -1,
            }
        )
        assert config.error_injection["chrony_open_socket"] == -13


class TestChronyStateConfigMethods:
    """Test ChronyStateConfig helper methods."""

    def test_is_synchronized_true_when_valid(self) -> None:
        """is_synchronized returns True for valid reference."""
        config = ChronyStateConfig(stratum=2, reference_id=0xC0A80101)
        assert config.is_synchronized() is True

    def test_is_synchronized_false_when_ref_id_zero(self) -> None:
        """is_synchronized returns False when reference_id is 0."""
        config = ChronyStateConfig(stratum=2, reference_id=0)
        assert config.is_synchronized() is False

    def test_is_synchronized_false_when_stratum_16(self) -> None:
        """is_synchronized returns False when stratum is 16."""
        config = ChronyStateConfig(stratum=16, reference_id=0xC0A80101)
        assert config.is_synchronized() is False

    def test_is_leap_pending_insert(self) -> None:
        """is_leap_pending returns True for INSERT."""
        config = ChronyStateConfig(leap_status=LeapStatus.INSERT)
        assert config.is_leap_pending() is True

    def test_is_leap_pending_delete(self) -> None:
        """is_leap_pending returns True for DELETE."""
        config = ChronyStateConfig(leap_status=LeapStatus.DELETE)
        assert config.is_leap_pending() is True

    def test_is_leap_pending_normal(self) -> None:
        """is_leap_pending returns False for NORMAL."""
        config = ChronyStateConfig(leap_status=LeapStatus.NORMAL)
        assert config.is_leap_pending() is False

    def test_is_leap_pending_unsync(self) -> None:
        """is_leap_pending returns False for UNSYNC."""
        config = ChronyStateConfig(leap_status=LeapStatus.UNSYNC)
        assert config.is_leap_pending() is False

    def test_reference_id_name_ip_format(self) -> None:
        """reference_id_name formats IP address correctly."""
        config = ChronyStateConfig(reference_id=0xC0A80101)  # 192.168.1.1
        assert config.reference_id_name() == "192.168.1.1"

    def test_reference_id_name_ascii_format(self) -> None:
        """reference_id_name formats ASCII name correctly."""
        config = ChronyStateConfig(reference_id=0x47505300)  # GPS\0
        assert config.reference_id_name() == "GPS"


class TestSourceConfigValidation:
    """Test SourceConfig validation."""

    def test_default_config_is_valid(self) -> None:
        """Default configuration should be valid."""
        config = SourceConfig()
        assert config.stratum == 2

    def test_stratum_zero_is_valid(self) -> None:
        """Stratum 0 should be valid for refclocks."""
        config = SourceConfig(stratum=0)
        assert config.stratum == 0

    def test_stratum_15_is_valid(self) -> None:
        """Stratum 15 boundary should be valid."""
        config = SourceConfig(stratum=15)
        assert config.stratum == 15

    def test_stratum_16_rejected(self) -> None:
        """Stratum 16 should be rejected for sources."""
        with pytest.raises(ValueError, match="stratum must be 0-15"):
            SourceConfig(stratum=16)

    def test_negative_stratum_rejected(self) -> None:
        """Negative stratum should be rejected."""
        with pytest.raises(ValueError, match="stratum must be 0-15"):
            SourceConfig(stratum=-1)

    def test_reachability_zero_is_valid(self) -> None:
        """Reachability 0 should be valid."""
        config = SourceConfig(reachability=0)
        assert config.reachability == 0

    def test_reachability_255_is_valid(self) -> None:
        """Reachability 255 should be valid."""
        config = SourceConfig(reachability=255)
        assert config.reachability == 255

    def test_reachability_256_rejected(self) -> None:
        """Reachability above 255 should be rejected."""
        with pytest.raises(ValueError, match="reachability must be 0-255"):
            SourceConfig(reachability=256)

    def test_negative_reachability_rejected(self) -> None:
        """Negative reachability should be rejected."""
        with pytest.raises(ValueError, match="reachability must be 0-255"):
            SourceConfig(reachability=-1)

    def test_negative_last_sample_ago_rejected(self) -> None:
        """Negative last_sample_ago should be rejected."""
        with pytest.raises(ValueError, match="last_sample_ago must be non-negative"):
            SourceConfig(last_sample_ago=-1)

    def test_negative_latest_meas_err_rejected(self) -> None:
        """Negative measurement error should be rejected."""
        with pytest.raises(ValueError, match="latest_meas_err must be non-negative"):
            SourceConfig(latest_meas_err=-0.001)

    def test_negative_samples_rejected(self) -> None:
        """Negative samples should be rejected."""
        with pytest.raises(ValueError, match="samples must be non-negative"):
            SourceConfig(samples=-1)

    def test_negative_std_dev_rejected(self) -> None:
        """Negative std_dev should be rejected."""
        with pytest.raises(ValueError, match="std_dev must be non-negative"):
            SourceConfig(std_dev=-0.001)


class TestSourceConfigMethods:
    """Test SourceConfig helper methods."""

    def test_is_reachable_true_when_positive(self) -> None:
        """is_reachable returns True when reachability > 0."""
        config = SourceConfig(reachability=255)
        assert config.is_reachable() is True

    def test_is_reachable_false_when_zero(self) -> None:
        """is_reachable returns False when reachability == 0."""
        config = SourceConfig(reachability=0)
        assert config.is_reachable() is False

    def test_is_selected_true_when_selected(self) -> None:
        """is_selected returns True for SELECTED state."""
        config = SourceConfig(state=SourceState.SELECTED)
        assert config.is_selected() is True

    def test_is_selected_false_when_not_selected(self) -> None:
        """is_selected returns False for non-SELECTED states."""
        config = SourceConfig(state=SourceState.SELECTABLE)
        assert config.is_selected() is False

    def test_compute_reference_id_ipv4(self) -> None:
        """compute_reference_id handles IPv4 addresses."""
        config = SourceConfig(address="192.168.1.100")
        ref_id = config.compute_reference_id()
        assert ref_id == 0xC0A80164  # 192.168.1.100 as uint32

    def test_compute_reference_id_refclock(self) -> None:
        """compute_reference_id handles refclock names."""
        config = SourceConfig(address="GPS")
        ref_id = config.compute_reference_id()
        assert ref_id == 0x47505300  # GPS\0 as uint32

    def test_compute_reference_id_override(self) -> None:
        """compute_reference_id uses override when set."""
        config = SourceConfig(address="192.168.1.100", reference_id=0x12345678)
        ref_id = config.compute_reference_id()
        assert ref_id == 0x12345678


class TestRTCConfigValidation:
    """Test RTCConfig validation."""

    def test_default_config_is_valid(self) -> None:
        """Default configuration should be valid."""
        config = RTCConfig()
        assert config.samples == 10

    def test_negative_samples_rejected(self) -> None:
        """Negative samples should be rejected."""
        with pytest.raises(ValueError, match="samples must be non-negative"):
            RTCConfig(samples=-1)

    def test_negative_runs_rejected(self) -> None:
        """Negative runs should be rejected."""
        with pytest.raises(ValueError, match="runs must be non-negative"):
            RTCConfig(runs=-1)

    def test_negative_span_rejected(self) -> None:
        """Negative span should be rejected."""
        with pytest.raises(ValueError, match="span must be non-negative"):
            RTCConfig(span=-1)

    def test_negative_ref_time_rejected(self) -> None:
        """Negative ref_time should be rejected."""
        with pytest.raises(ValueError, match="ref_time must be non-negative"):
            RTCConfig(ref_time=-1.0)

    def test_zero_samples_is_valid(self) -> None:
        """Zero samples should be valid (uncalibrated)."""
        config = RTCConfig(samples=0)
        assert config.samples == 0


class TestRTCConfigMethods:
    """Test RTCConfig helper methods."""

    def test_is_calibrated_true_when_samples_positive(self) -> None:
        """is_calibrated returns True when samples > 0."""
        config = RTCConfig(samples=10)
        assert config.is_calibrated() is True

    def test_is_calibrated_false_when_samples_zero(self) -> None:
        """is_calibrated returns False when samples == 0."""
        config = RTCConfig(samples=0)
        assert config.is_calibrated() is False
