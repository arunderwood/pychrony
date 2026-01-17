"""Integration tests for get_source_stats() with real chronyd.

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


class TestGetSourceStatsIntegration:
    """Integration tests for get_source_stats() function."""

    def test_get_source_stats_returns_list(self):
        """Test that get_source_stats returns a list."""
        from pychrony import get_source_stats

        stats = get_source_stats()
        assert isinstance(stats, list)

    def test_get_source_stats_returns_sourcestats_objects(self):
        """Test that get_source_stats returns SourceStats objects."""
        from pychrony import get_source_stats, SourceStats

        stats = get_source_stats()
        for stat in stats:
            assert isinstance(stat, SourceStats)

    def test_sourcestats_has_non_negative_samples(self):
        """Test that samples is non-negative."""
        from pychrony import get_source_stats

        stats = get_source_stats()
        for stat in stats:
            assert stat.samples >= 0

    def test_sourcestats_has_non_negative_runs(self):
        """Test that runs is non-negative."""
        from pychrony import get_source_stats

        stats = get_source_stats()
        for stat in stats:
            assert stat.runs >= 0

    def test_sourcestats_has_non_negative_span(self):
        """Test that span is non-negative."""
        from pychrony import get_source_stats

        stats = get_source_stats()
        for stat in stats:
            assert stat.span >= 0

    def test_sourcestats_has_non_negative_std_dev(self):
        """Test that std_dev is non-negative."""
        from pychrony import get_source_stats

        stats = get_source_stats()
        for stat in stats:
            assert stat.std_dev >= 0

    def test_sourcestats_has_non_negative_skew(self):
        """Test that skew is non-negative."""
        from pychrony import get_source_stats

        stats = get_source_stats()
        for stat in stats:
            assert stat.skew >= 0

    def test_sourcestats_has_non_negative_offset_err(self):
        """Test that offset_err is non-negative."""
        from pychrony import get_source_stats

        stats = get_source_stats()
        for stat in stats:
            assert stat.offset_err >= 0

    def test_get_source_stats_with_custom_socket_path(self):
        """Test get_source_stats with explicit socket path."""
        from pychrony import get_source_stats, ChronyConnectionError

        # Test with default paths (one should work in Docker)
        try:
            stats = get_source_stats(socket_path="/run/chrony/chronyd.sock")
            assert isinstance(stats, list)
        except ChronyConnectionError:
            # Try alternate path
            stats = get_source_stats(socket_path="/var/run/chrony/chronyd.sock")
            assert isinstance(stats, list)

    def test_get_source_stats_multiple_calls_independent(self):
        """Test that multiple get_source_stats calls work independently."""
        from pychrony import get_source_stats

        stats1 = get_source_stats()
        stats2 = get_source_stats()
        stats3 = get_source_stats()

        # All should return lists
        assert isinstance(stats1, list)
        assert isinstance(stats2, list)
        assert isinstance(stats3, list)

    def test_sourcestats_has_sufficient_samples_method(self):
        """Test that has_sufficient_samples method works correctly."""
        from pychrony import get_source_stats

        stats = get_source_stats()
        for stat in stats:
            # has_sufficient_samples should return True if samples >= minimum
            assert stat.has_sufficient_samples() == (stat.samples >= 4)
            assert stat.has_sufficient_samples(minimum=0) is True


class TestSourceStatsCorrelation:
    """Tests for correlating sources with their stats."""

    def test_sources_and_stats_same_count(self):
        """Test that sources and stats have same count."""
        from pychrony import get_sources, get_source_stats

        sources = get_sources()
        stats = get_source_stats()

        # Should have same number of entries
        assert len(sources) == len(stats)

    def test_sources_and_stats_correlate_by_address(self):
        """Test that sources and stats can be correlated by address."""
        from pychrony import get_sources, get_source_stats

        sources = get_sources()
        stats = get_source_stats()

        # Build lookup by address
        source_addresses = {s.address for s in sources}
        stats_addresses = {s.address for s in stats if s.address}

        # All stats with addresses should match source addresses
        if stats_addresses:
            assert stats_addresses.issubset(source_addresses), (
                f"Stats addresses {stats_addresses} not found in sources {source_addresses}"
            )
