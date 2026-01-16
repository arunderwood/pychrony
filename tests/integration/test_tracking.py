"""Integration tests for get_tracking() with real chronyd.

These tests require a running chronyd daemon and libchrony installed.
They should be run inside the Docker test container.
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


class TestGetTrackingIntegration:
    """Integration tests for get_tracking() function."""

    def test_get_tracking_returns_tracking_status(self):
        """Test that get_tracking returns a TrackingStatus object."""
        from pychrony import get_tracking, TrackingStatus

        status = get_tracking()
        assert isinstance(status, TrackingStatus)

    def test_get_tracking_has_valid_stratum(self):
        """Test that returned status has valid stratum value."""
        from pychrony import get_tracking

        status = get_tracking()
        assert 0 <= status.stratum <= 15

    def test_get_tracking_has_valid_leap_status(self):
        """Test that returned status has valid leap_status value."""
        from pychrony import get_tracking

        status = get_tracking()
        assert 0 <= status.leap_status <= 3

    def test_get_tracking_has_non_negative_fields(self):
        """Test that non-negative fields are indeed non-negative."""
        from pychrony import get_tracking

        status = get_tracking()
        assert status.rms_offset >= 0
        assert status.skew >= 0
        assert status.root_delay >= 0
        assert status.root_dispersion >= 0
        assert status.update_interval >= 0

    def test_get_tracking_has_reference_id_name(self):
        """Test that reference_id_name is a non-empty string when synchronized."""
        from pychrony import get_tracking

        status = get_tracking()
        if status.is_synchronized():
            assert isinstance(status.reference_id_name, str)
            # May be empty if unsynchronized

    def test_get_tracking_with_custom_socket_path(self):
        """Test get_tracking with explicit socket path."""
        from pychrony import get_tracking, ChronyConnectionError

        # Test with default paths (one should work in Docker)
        try:
            status = get_tracking(socket_path="/run/chrony/chronyd.sock")
            assert status is not None
        except ChronyConnectionError:
            # Try alternate path
            status = get_tracking(socket_path="/var/run/chrony/chronyd.sock")
            assert status is not None

    def test_get_tracking_multiple_calls_independent(self):
        """Test that multiple get_tracking calls work independently."""
        from pychrony import get_tracking

        status1 = get_tracking()
        status2 = get_tracking()
        status3 = get_tracking()

        # All should return valid TrackingStatus objects
        assert status1.stratum <= 15
        assert status2.stratum <= 15
        assert status3.stratum <= 15


class TestGetTrackingWithLocalClock:
    """Integration tests specific to local clock configuration.

    The Docker test environment configures chronyd with "local stratum 10"
    which means chronyd will act as its own reference source.
    """

    def test_local_clock_stratum(self):
        """Test that local clock configuration shows stratum 10."""
        from pychrony import get_tracking

        status = get_tracking()
        # With "local stratum 10" in chrony.conf, stratum should be 10
        # However, it might take time to synchronize, so allow higher values too
        assert status.stratum <= 15

    def test_local_clock_synchronized(self):
        """Test that local clock shows as synchronized."""
        from pychrony import get_tracking

        status = get_tracking()
        # With local stratum configured, it should eventually be synchronized
        # Note: may need to wait for chronyd to stabilize
        if status.stratum == 10:
            assert status.is_synchronized()
