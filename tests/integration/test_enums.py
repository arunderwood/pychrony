"""Integration tests for enum types with real chronyd.

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


class TestSourceStateIntegration:
    """Integration tests for SourceState enum values from real chronyd (T015)."""

    def test_source_state_is_enum_instance(self):
        """Test that source.state is a SourceState enum instance."""
        from pychrony import ChronyConnection, SourceState

        with ChronyConnection() as conn:
            sources = conn.get_sources()
            for source in sources:
                assert isinstance(source.state, SourceState)

    def test_source_state_in_valid_members(self):
        """Test that source.state is a valid SourceState member."""
        from pychrony import ChronyConnection, SourceState

        with ChronyConnection() as conn:
            sources = conn.get_sources()
            valid_states = list(SourceState)
            for source in sources:
                assert source.state in valid_states

    def test_source_state_name_is_string(self):
        """Test that source.state.name returns a valid string."""
        from pychrony import ChronyConnection

        valid_names = [
            "SELECTED",
            "NONSELECTABLE",
            "FALSETICKER",
            "JITTERY",
            "UNSELECTED",
            "SELECTABLE",
        ]

        with ChronyConnection() as conn:
            sources = conn.get_sources()
            for source in sources:
                assert source.state.name in valid_names

    def test_source_state_value_is_int(self):
        """Test that source.state.value returns an integer."""
        from pychrony import ChronyConnection

        with ChronyConnection() as conn:
            sources = conn.get_sources()
            for source in sources:
                assert isinstance(source.state.value, int)
                assert 0 <= source.state.value <= 5


class TestLeapStatusIntegration:
    """Integration tests for LeapStatus enum values from real chronyd (T024)."""

    def test_leap_status_is_enum_instance(self):
        """Test that tracking.leap_status is a LeapStatus enum instance."""
        from pychrony import ChronyConnection, LeapStatus

        with ChronyConnection() as conn:
            status = conn.get_tracking()
            assert isinstance(status.leap_status, LeapStatus)

    def test_leap_status_in_valid_members(self):
        """Test that tracking.leap_status is a valid LeapStatus member."""
        from pychrony import ChronyConnection, LeapStatus

        with ChronyConnection() as conn:
            status = conn.get_tracking()
            valid_statuses = list(LeapStatus)
            assert status.leap_status in valid_statuses

    def test_leap_status_name_is_string(self):
        """Test that tracking.leap_status.name returns a valid string."""
        from pychrony import ChronyConnection

        with ChronyConnection() as conn:
            status = conn.get_tracking()
            valid_names = ["NORMAL", "INSERT", "DELETE", "UNSYNC"]
            assert status.leap_status.name in valid_names

    def test_leap_status_value_is_int(self):
        """Test that tracking.leap_status.value returns an integer."""
        from pychrony import ChronyConnection

        with ChronyConnection() as conn:
            status = conn.get_tracking()
            assert isinstance(status.leap_status.value, int)
            assert 0 <= status.leap_status.value <= 3


class TestSourceModeIntegration:
    """Integration tests for SourceMode enum values from real chronyd (T033)."""

    def test_source_mode_is_enum_instance(self):
        """Test that source.mode is a SourceMode enum instance."""
        from pychrony import ChronyConnection, SourceMode

        with ChronyConnection() as conn:
            sources = conn.get_sources()
            for source in sources:
                assert isinstance(source.mode, SourceMode)

    def test_source_mode_in_valid_members(self):
        """Test that source.mode is a valid SourceMode member."""
        from pychrony import ChronyConnection, SourceMode

        with ChronyConnection() as conn:
            sources = conn.get_sources()
            valid_modes = list(SourceMode)
            for source in sources:
                assert source.mode in valid_modes

    def test_source_mode_name_is_string(self):
        """Test that source.mode.name returns a valid string."""
        from pychrony import ChronyConnection

        with ChronyConnection() as conn:
            sources = conn.get_sources()
            valid_names = ["CLIENT", "PEER", "REFCLOCK"]
            for source in sources:
                assert source.mode.name in valid_names

    def test_source_mode_value_is_int(self):
        """Test that source.mode.value returns an integer."""
        from pychrony import ChronyConnection

        with ChronyConnection() as conn:
            sources = conn.get_sources()
            for source in sources:
                assert isinstance(source.mode.value, int)
                assert 0 <= source.mode.value <= 2
