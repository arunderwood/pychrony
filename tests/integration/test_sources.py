"""Integration tests for ChronyConnection.get_sources() with real chronyd.

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


class TestGetSourcesIntegration:
    """Integration tests for get_sources() method."""

    def test_get_sources_returns_list(self):
        """Test that get_sources returns a list."""
        from pychrony import ChronyConnection

        with ChronyConnection() as conn:
            sources = conn.get_sources()
            assert isinstance(sources, list)

    def test_get_sources_returns_source_objects(self):
        """Test that get_sources returns Source objects."""
        from pychrony import ChronyConnection, Source

        with ChronyConnection() as conn:
            sources = conn.get_sources()
            for source in sources:
                assert isinstance(source, Source)

    def test_source_has_valid_stratum(self):
        """Test that returned sources have valid stratum values."""
        from pychrony import ChronyConnection

        with ChronyConnection() as conn:
            sources = conn.get_sources()
            for source in sources:
                assert 0 <= source.stratum <= 15

    def test_source_has_valid_mode(self):
        """Test that returned sources have valid mode values (SourceMode enum)."""
        from pychrony import ChronyConnection, SourceMode

        with ChronyConnection() as conn:
            sources = conn.get_sources()
            for source in sources:
                assert isinstance(source.mode, SourceMode)
                assert source.mode in list(SourceMode)

    def test_source_has_valid_state(self):
        """Test that returned sources have valid state values (SourceState enum)."""
        from pychrony import ChronyConnection, SourceState

        with ChronyConnection() as conn:
            sources = conn.get_sources()
            for source in sources:
                assert isinstance(source.state, SourceState)
                assert source.state in list(SourceState)

    def test_source_has_valid_reachability(self):
        """Test that returned sources have valid reachability values."""
        from pychrony import ChronyConnection

        with ChronyConnection() as conn:
            sources = conn.get_sources()
            for source in sources:
                assert 0 <= source.reachability <= 255

    def test_source_has_non_negative_last_sample_ago(self):
        """Test that last_sample_ago is non-negative."""
        from pychrony import ChronyConnection

        with ChronyConnection() as conn:
            sources = conn.get_sources()
            for source in sources:
                assert source.last_sample_ago >= 0

    def test_source_has_non_negative_latest_meas_err(self):
        """Test that latest_meas_err is non-negative."""
        from pychrony import ChronyConnection

        with ChronyConnection() as conn:
            sources = conn.get_sources()
            for source in sources:
                assert source.latest_meas_err >= 0

    def test_get_sources_with_custom_socket_path(self):
        """Test get_sources with explicit socket path."""
        from pychrony import ChronyConnection, ChronyConnectionError

        # Test with default paths (one should work in Docker)
        try:
            with ChronyConnection("/run/chrony/chronyd.sock") as conn:
                sources = conn.get_sources()
                assert isinstance(sources, list)
        except ChronyConnectionError:
            # Try alternate path
            with ChronyConnection("/var/run/chrony/chronyd.sock") as conn:
                sources = conn.get_sources()
                assert isinstance(sources, list)

    def test_get_sources_multiple_calls_same_connection(self):
        """Test that multiple get_sources calls reuse same connection."""
        from pychrony import ChronyConnection

        with ChronyConnection() as conn:
            sources1 = conn.get_sources()
            sources2 = conn.get_sources()
            sources3 = conn.get_sources()

            # All should return lists
            assert isinstance(sources1, list)
            assert isinstance(sources2, list)
            assert isinstance(sources3, list)

    def test_source_mode_name_via_enum(self):
        """Test that mode.name returns the enum name."""
        from pychrony import ChronyConnection

        with ChronyConnection() as conn:
            sources = conn.get_sources()
            for source in sources:
                # Enum .name returns uppercase string
                mode_name = source.mode.name
                assert mode_name in ["CLIENT", "PEER", "REFCLOCK"]

    def test_source_state_name_via_enum(self):
        """Test that state.name returns the enum name."""
        from pychrony import ChronyConnection

        valid_states = [
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
                # Enum .name returns uppercase string
                state_name = source.state.name
                assert state_name in valid_states

    def test_source_is_reachable_method(self):
        """Test that is_reachable method works correctly."""
        from pychrony import ChronyConnection

        with ChronyConnection() as conn:
            sources = conn.get_sources()
            for source in sources:
                # is_reachable should return True if reachability > 0
                assert source.is_reachable() == (source.reachability > 0)

    def test_source_is_selected_method(self):
        """Test that is_selected method works correctly."""
        from pychrony import ChronyConnection, SourceState

        with ChronyConnection() as conn:
            sources = conn.get_sources()
            for source in sources:
                # is_selected should return True if state is SELECTED
                assert source.is_selected() == (source.state == SourceState.SELECTED)
