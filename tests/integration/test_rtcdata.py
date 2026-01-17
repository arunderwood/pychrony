"""Integration tests for get_rtc_data() with real chronyd.

These tests require a running chronyd daemon and libchrony installed.
They should be run inside the Docker test container.

Note: RTC tracking may not be available in all environments (especially VMs).
Tests handle this gracefully by expecting ChronyDataError.
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

    def test_get_rtc_data_returns_rtcdata_or_raises(self):
        """Test that get_rtc_data returns RTCData or raises ChronyDataError."""
        from pychrony import get_rtc_data, RTCData, ChronyDataError

        try:
            rtc = get_rtc_data()
            assert isinstance(rtc, RTCData)
        except ChronyDataError as e:
            # RTC tracking not available is expected in many environments
            assert "RTC tracking is not available" in str(e)

    def test_get_rtc_data_with_custom_socket_path(self):
        """Test get_rtc_data with explicit socket path."""
        from pychrony import get_rtc_data, ChronyConnectionError, ChronyDataError

        # Try primary socket path
        try:
            rtc = get_rtc_data(socket_path="/run/chrony/chronyd.sock")
            # Success - RTC data returned
            assert rtc is not None
            return
        except ChronyConnectionError:
            pass  # Try alternate path
        except ChronyDataError as e:
            # RTC not available - this is acceptable
            assert "RTC tracking is not available" in str(e)
            return

        # Try alternate socket path
        try:
            rtc = get_rtc_data(socket_path="/var/run/chrony/chronyd.sock")
            assert rtc is not None
        except ChronyDataError as e:
            # RTC not available - this is acceptable
            assert "RTC tracking is not available" in str(e)


class TestRtcDataValidation:
    """Tests for RTCData field validation (only run if RTC available)."""

    @pytest.fixture
    def rtc_data_if_available(self):
        """Get RTC data if available, skip test otherwise."""
        from pychrony import get_rtc_data, ChronyDataError

        try:
            return get_rtc_data()
        except ChronyDataError:
            pytest.skip("RTC tracking not available")

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
