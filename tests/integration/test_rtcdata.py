"""Integration tests for get_rtc_data() with real chronyd.

These tests require a running chronyd daemon and libchrony installed.
They should be run inside the Docker test container.

Note: RTC tracking may not be available in all environments (especially VMs).
Tests handle this gracefully by checking for None return value.
"""

import importlib.util

import pytest

# Check if CFFI bindings are available
HAS_CFFI_BINDINGS = (
    importlib.util.find_spec("pychrony._core._cffi_bindings") is not None
)

pytestmark = pytest.mark.skipif(
    not HAS_CFFI_BINDINGS, reason="CFFI bindings not compiled (requires libchrony)"
)


class TestGetRtcDataIntegration:
    """Integration tests for get_rtc_data() function."""

    def test_get_rtc_data_returns_rtcdata_or_none(self):
        """Test that get_rtc_data returns RTCData or None."""
        from pychrony import get_rtc_data, RTCData

        rtc = get_rtc_data()
        # RTC tracking may not be available in all environments
        assert rtc is None or isinstance(rtc, RTCData)

    def test_get_rtc_data_with_custom_socket_path(self):
        """Test get_rtc_data with explicit socket path."""
        from pychrony import get_rtc_data, RTCData, ChronyConnectionError

        # Try primary socket path
        try:
            rtc = get_rtc_data(socket_path="/run/chrony/chronyd.sock")
            # Success - RTC data returned or None (RTC not configured)
            assert rtc is None or isinstance(rtc, RTCData)
            return
        except ChronyConnectionError:
            pass  # Try alternate path

        # Try alternate socket path
        rtc = get_rtc_data(socket_path="/var/run/chrony/chronyd.sock")
        # RTC data returned or None (RTC not configured)
        assert rtc is None or isinstance(rtc, RTCData)


class TestRtcDataValidation:
    """Tests for RTCData field validation (only run if RTC available)."""

    @pytest.fixture
    def rtc_data_if_available(self):
        """Get RTC data if available, skip test otherwise."""
        from pychrony import get_rtc_data

        rtc = get_rtc_data()
        if rtc is None:
            pytest.skip("RTC tracking not available")
        return rtc

    def test_rtcdata_has_non_negative_ref_time(self, rtc_data_if_available):
        """Test that ref_time is non-negative."""
        assert rtc_data_if_available.ref_time >= 0

    def test_rtcdata_has_non_negative_samples(self, rtc_data_if_available):
        """Test that samples is non-negative."""
        assert rtc_data_if_available.samples >= 0

    def test_rtcdata_has_non_negative_runs(self, rtc_data_if_available):
        """Test that runs is non-negative."""
        assert rtc_data_if_available.runs >= 0

    def test_rtcdata_has_non_negative_span(self, rtc_data_if_available):
        """Test that span is non-negative."""
        assert rtc_data_if_available.span >= 0

    def test_rtcdata_is_calibrated_method(self, rtc_data_if_available):
        """Test that is_calibrated method works correctly."""
        # is_calibrated should return True if samples > 0
        assert rtc_data_if_available.is_calibrated() == (
            rtc_data_if_available.samples > 0
        )
