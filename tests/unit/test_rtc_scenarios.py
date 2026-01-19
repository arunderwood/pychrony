"""Unit tests for RTC mock scenarios.

Tests for RTC availability and calibration states.
"""

from __future__ import annotations

from tests.mocks import (
    patched_chrony_connection,
    ChronyStateConfig,
    RTCConfig,
    SCENARIO_RTC_AVAILABLE,
    SCENARIO_RTC_UNAVAILABLE,
)


class TestRtcAvailableScenario:
    """Test SCENARIO_RTC_AVAILABLE preset."""

    def test_rtc_data_is_not_none(self) -> None:
        """RTC available scenario should return RTC data."""
        with patched_chrony_connection(SCENARIO_RTC_AVAILABLE) as conn:
            rtc = conn.get_rtc_data()
            assert rtc is not None

    def test_rtc_is_calibrated(self) -> None:
        """RTC available scenario should be calibrated."""
        with patched_chrony_connection(SCENARIO_RTC_AVAILABLE) as conn:
            rtc = conn.get_rtc_data()
            assert rtc is not None
            assert rtc.is_calibrated() is True

    def test_rtc_samples_positive(self) -> None:
        """RTC available scenario should have positive samples."""
        with patched_chrony_connection(SCENARIO_RTC_AVAILABLE) as conn:
            rtc = conn.get_rtc_data()
            assert rtc is not None
            assert rtc.samples > 0


class TestRtcUnavailableScenario:
    """Test SCENARIO_RTC_UNAVAILABLE preset."""

    def test_rtc_data_is_none(self) -> None:
        """RTC unavailable scenario should return None."""
        with patched_chrony_connection(SCENARIO_RTC_UNAVAILABLE) as conn:
            rtc = conn.get_rtc_data()
            assert rtc is None


class TestRtcConfigNone:
    """Test RTC when config.rtc is None."""

    def test_rtc_none_returns_none(self) -> None:
        """When rtc config is None, get_rtc_data returns None."""
        config = ChronyStateConfig(rtc=None)
        with patched_chrony_connection(config) as conn:
            rtc = conn.get_rtc_data()
            assert rtc is None


class TestRtcConfigUnavailable:
    """Test RTC when config.rtc.available is False."""

    def test_rtc_unavailable_returns_none(self) -> None:
        """When rtc.available is False, get_rtc_data returns None."""
        config = ChronyStateConfig(
            rtc=RTCConfig(available=False),
        )
        with patched_chrony_connection(config) as conn:
            rtc = conn.get_rtc_data()
            assert rtc is None


class TestRtcUncalibrated:
    """Test RTC with zero samples (uncalibrated)."""

    def test_rtc_samples_zero_not_calibrated(self) -> None:
        """RTC with samples=0 should not be calibrated."""
        config = ChronyStateConfig(
            rtc=RTCConfig(available=True, samples=0),
        )
        with patched_chrony_connection(config) as conn:
            rtc = conn.get_rtc_data()
            assert rtc is not None
            assert rtc.is_calibrated() is False
            assert rtc.samples == 0


class TestRtcFieldValues:
    """Test RTC field values are correctly returned."""

    def test_rtc_samples_value(self) -> None:
        """RTC samples should match config."""
        config = ChronyStateConfig(
            rtc=RTCConfig(available=True, samples=15),
        )
        with patched_chrony_connection(config) as conn:
            rtc = conn.get_rtc_data()
            assert rtc is not None
            assert rtc.samples == 15

    def test_rtc_runs_value(self) -> None:
        """RTC runs should match config."""
        config = ChronyStateConfig(
            rtc=RTCConfig(available=True, runs=5),
        )
        with patched_chrony_connection(config) as conn:
            rtc = conn.get_rtc_data()
            assert rtc is not None
            assert rtc.runs == 5

    def test_rtc_span_value(self) -> None:
        """RTC span should match config."""
        config = ChronyStateConfig(
            rtc=RTCConfig(available=True, span=43200),
        )
        with patched_chrony_connection(config) as conn:
            rtc = conn.get_rtc_data()
            assert rtc is not None
            assert rtc.span == 43200

    def test_rtc_offset_value(self) -> None:
        """RTC offset should match config."""
        config = ChronyStateConfig(
            rtc=RTCConfig(available=True, offset=0.5),
        )
        with patched_chrony_connection(config) as conn:
            rtc = conn.get_rtc_data()
            assert rtc is not None
            assert rtc.offset == 0.5

    def test_rtc_freq_offset_value(self) -> None:
        """RTC frequency offset should match config."""
        config = ChronyStateConfig(
            rtc=RTCConfig(available=True, freq_offset=-2.5),
        )
        with patched_chrony_connection(config) as conn:
            rtc = conn.get_rtc_data()
            assert rtc is not None
            assert rtc.freq_offset == -2.5
