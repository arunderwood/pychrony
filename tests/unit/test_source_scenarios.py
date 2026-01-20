"""Unit tests for source mock scenarios.

Tests for REFCLOCK sources and multi-source selection.
"""

from __future__ import annotations

from pychrony.models import SourceState, SourceMode
from tests.mocks import (
    patched_chrony_connection,
    ChronyStateConfig,
    SourceConfig,
    SCENARIO_GPS_REFCLOCK,
    SCENARIO_PPS_REFCLOCK,
    SCENARIO_MULTI_SOURCE,
    SCENARIO_NTP_SYNCED,
)


class TestRefclockMode:
    """Test REFCLOCK source mode."""

    def test_gps_refclock_mode(self) -> None:
        """GPS source should have REFCLOCK mode."""
        with patched_chrony_connection(SCENARIO_GPS_REFCLOCK) as conn:
            sources = conn.get_sources()
            assert len(sources) == 1
            assert sources[0].mode == SourceMode.REFCLOCK

    def test_pps_refclock_mode(self) -> None:
        """PPS source should have REFCLOCK mode."""
        with patched_chrony_connection(SCENARIO_PPS_REFCLOCK) as conn:
            sources = conn.get_sources()
            assert len(sources) == 1
            assert sources[0].mode == SourceMode.REFCLOCK

    def test_custom_refclock_source(self) -> None:
        """Custom REFCLOCK source should work."""
        # For REFCLOCK sources with the mock simulating real libchrony behavior,
        # the address field doesn't exist and the reference_id is used instead.
        # "PHC0" contains a digit so we need explicit reference_id.
        ref_id = int.from_bytes(b"PHC0", "big")
        config = ChronyStateConfig(
            sources=[
                SourceConfig(
                    address="PHC0",  # Used for sourcestats, ignored for sources
                    mode=SourceMode.REFCLOCK,
                    stratum=0,
                    state=SourceState.SELECTED,
                    reference_id=ref_id,
                ),
            ],
        )
        with patched_chrony_connection(config) as conn:
            sources = conn.get_sources()
            assert len(sources) == 1
            assert sources[0].mode == SourceMode.REFCLOCK
            assert sources[0].address == "PHC0"


class TestRefclockAddress:
    """Test REFCLOCK source addresses."""

    def test_gps_address(self) -> None:
        """GPS refclock should have GPS address."""
        with patched_chrony_connection(SCENARIO_GPS_REFCLOCK) as conn:
            sources = conn.get_sources()
            assert sources[0].address == "GPS"

    def test_pps_address(self) -> None:
        """PPS refclock should have PPS address."""
        with patched_chrony_connection(SCENARIO_PPS_REFCLOCK) as conn:
            sources = conn.get_sources()
            assert sources[0].address == "PPS"


class TestRefclockStratum:
    """Test REFCLOCK source stratum."""

    def test_gps_source_stratum_zero(self) -> None:
        """GPS refclock source should have stratum 0."""
        with patched_chrony_connection(SCENARIO_GPS_REFCLOCK) as conn:
            sources = conn.get_sources()
            assert sources[0].stratum == 0

    def test_pps_source_stratum_zero(self) -> None:
        """PPS refclock source should have stratum 0."""
        with patched_chrony_connection(SCENARIO_PPS_REFCLOCK) as conn:
            sources = conn.get_sources()
            assert sources[0].stratum == 0


class TestMultipleSourcesCount:
    """Test multiple sources count."""

    def test_multi_source_count(self) -> None:
        """Multi-source scenario should have correct count."""
        with patched_chrony_connection(SCENARIO_MULTI_SOURCE) as conn:
            sources = conn.get_sources()
            assert len(sources) == 4

    def test_empty_sources(self) -> None:
        """Empty sources list should return empty list."""
        config = ChronyStateConfig(sources=[])
        with patched_chrony_connection(config) as conn:
            sources = conn.get_sources()
            assert len(sources) == 0

    def test_single_source(self) -> None:
        """Single source should work."""
        with patched_chrony_connection(SCENARIO_NTP_SYNCED) as conn:
            sources = conn.get_sources()
            assert len(sources) == 1


class TestSourceSelection:
    """Test source selection filtering."""

    def test_exactly_one_selected(self) -> None:
        """Only one source should be selected."""
        with patched_chrony_connection(SCENARIO_MULTI_SOURCE) as conn:
            sources = conn.get_sources()
            selected = [s for s in sources if s.is_selected()]
            assert len(selected) == 1

    def test_selected_source_state(self) -> None:
        """Selected source should have SELECTED state."""
        with patched_chrony_connection(SCENARIO_MULTI_SOURCE) as conn:
            sources = conn.get_sources()
            selected = [s for s in sources if s.is_selected()]
            assert selected[0].state == SourceState.SELECTED


class TestSourceStates:
    """Test different source states."""

    def test_falseticker_state(self) -> None:
        """Falseticker source should have FALSETICKER state."""
        with patched_chrony_connection(SCENARIO_MULTI_SOURCE) as conn:
            sources = conn.get_sources()
            falsetickers = [s for s in sources if s.state == SourceState.FALSETICKER]
            assert len(falsetickers) == 1

    def test_selectable_state(self) -> None:
        """Selectable source should have SELECTABLE state."""
        with patched_chrony_connection(SCENARIO_MULTI_SOURCE) as conn:
            sources = conn.get_sources()
            selectable = [s for s in sources if s.state == SourceState.SELECTABLE]
            assert len(selectable) == 1

    def test_unselected_state(self) -> None:
        """Unselected source should have UNSELECTED state."""
        with patched_chrony_connection(SCENARIO_MULTI_SOURCE) as conn:
            sources = conn.get_sources()
            unselected = [s for s in sources if s.state == SourceState.UNSELECTED]
            assert len(unselected) == 1


class TestSourceReachability:
    """Test source reachability."""

    def test_reachable_source(self) -> None:
        """Source with reachability > 0 should be reachable."""
        with patched_chrony_connection(SCENARIO_NTP_SYNCED) as conn:
            sources = conn.get_sources()
            assert sources[0].is_reachable() is True
            assert sources[0].reachability == 255

    def test_unreachable_source(self) -> None:
        """Source with reachability == 0 should not be reachable."""
        with patched_chrony_connection(SCENARIO_MULTI_SOURCE) as conn:
            sources = conn.get_sources()
            unreachable = [s for s in sources if not s.is_reachable()]
            assert len(unreachable) == 1
            assert unreachable[0].reachability == 0

    def test_custom_reachability_values(self) -> None:
        """Custom reachability values should work."""
        config = ChronyStateConfig(
            sources=[
                SourceConfig(reachability=0),
                SourceConfig(address="192.168.1.2", reachability=128),
                SourceConfig(address="192.168.1.3", reachability=255),
            ],
        )
        with patched_chrony_connection(config) as conn:
            sources = conn.get_sources()
            assert sources[0].reachability == 0
            assert sources[0].is_reachable() is False
            assert sources[1].reachability == 128
            assert sources[1].is_reachable() is True
            assert sources[2].reachability == 255
            assert sources[2].is_reachable() is True


class TestSourceStats:
    """Test source statistics."""

    def test_source_stats_count_matches(self) -> None:
        """Source stats count should match source count."""
        with patched_chrony_connection(SCENARIO_MULTI_SOURCE) as conn:
            sources = conn.get_sources()
            stats = conn.get_source_stats()
            assert len(stats) == len(sources)

    def test_source_stats_addresses_match(self) -> None:
        """Source stats addresses should match source addresses."""
        with patched_chrony_connection(SCENARIO_MULTI_SOURCE) as conn:
            sources = conn.get_sources()
            stats = conn.get_source_stats()
            source_addrs = {s.address for s in sources}
            stats_addrs = {s.address for s in stats}
            assert source_addrs == stats_addrs

    def test_source_stats_fields(self) -> None:
        """Source stats should have correct field values."""
        config = ChronyStateConfig(
            sources=[
                SourceConfig(
                    address="192.168.1.100",
                    samples=15,
                    runs=5,
                    span=1024,
                    std_dev=0.0001,
                ),
            ],
        )
        with patched_chrony_connection(config) as conn:
            stats = conn.get_source_stats()
            assert len(stats) == 1
            assert stats[0].samples == 15
            assert stats[0].runs == 5
            assert stats[0].span == 1024
            assert stats[0].std_dev == 0.0001


class TestClientMode:
    """Test CLIENT source mode."""

    def test_ntp_synced_is_client(self) -> None:
        """NTP synced source should be CLIENT mode."""
        with patched_chrony_connection(SCENARIO_NTP_SYNCED) as conn:
            sources = conn.get_sources()
            assert sources[0].mode == SourceMode.CLIENT


class TestRefclockAddressFromReferenceId:
    """Test reference clock address derived from reference ID.

    In libchrony 0.2, the sources report uses TYPE_ADDRESS_OR_UINT32_IN_ADDRESS
    which exposes either "address" (NTP sources) or "reference ID" (refclocks).
    The code checks mode to determine which field to fetch.

    This tests that REFCLOCK sources correctly derive their address from the
    reference ID field.
    """

    def test_refclock_derives_address_from_reference_id(self) -> None:
        """REFCLOCK source should derive address from reference ID."""
        config = ChronyStateConfig(
            sources=[
                SourceConfig(
                    address="GPS",  # This will be ignored by mock for REFCLOCK
                    mode=SourceMode.REFCLOCK,
                    stratum=0,
                    state=SourceState.SELECTED,
                ),
            ],
        )
        with patched_chrony_connection(config) as conn:
            sources = conn.get_sources()
            assert len(sources) == 1
            # The address should be derived from the reference_id
            # which is computed from "GPS" -> 0x47505300 -> "GPS"
            assert sources[0].address == "GPS"
            assert sources[0].mode == SourceMode.REFCLOCK

    def test_mixed_ntp_and_refclock_sources(self) -> None:
        """Mix of NTP and REFCLOCK sources should work correctly."""
        config = ChronyStateConfig(
            sources=[
                SourceConfig(
                    address="192.168.1.1",
                    mode=SourceMode.CLIENT,
                    state=SourceState.SELECTABLE,
                ),
                SourceConfig(
                    address="PPS",
                    mode=SourceMode.REFCLOCK,
                    stratum=0,
                    state=SourceState.SELECTED,
                ),
                SourceConfig(
                    address="10.0.0.1",
                    mode=SourceMode.CLIENT,
                    state=SourceState.SELECTABLE,
                ),
            ],
        )
        with patched_chrony_connection(config) as conn:
            sources = conn.get_sources()
            assert len(sources) == 3
            # NTP source gets address directly
            assert sources[0].address == "192.168.1.1"
            assert sources[0].mode == SourceMode.CLIENT
            # REFCLOCK source gets address from reference ID
            assert sources[1].address == "PPS"
            assert sources[1].mode == SourceMode.REFCLOCK
            # Second NTP source gets address directly
            assert sources[2].address == "10.0.0.1"
            assert sources[2].mode == SourceMode.CLIENT

    def test_refclock_with_custom_reference_id(self) -> None:
        """REFCLOCK with explicit reference_id should use that value."""
        # Reference ID 0x50484330 = "PHC0" in ASCII
        ref_id = int.from_bytes(b"PHC0", "big")
        config = ChronyStateConfig(
            sources=[
                SourceConfig(
                    address="ignored",
                    mode=SourceMode.REFCLOCK,
                    stratum=0,
                    state=SourceState.SELECTED,
                    reference_id=ref_id,
                ),
            ],
        )
        with patched_chrony_connection(config) as conn:
            sources = conn.get_sources()
            assert len(sources) == 1
            assert sources[0].address == "PHC0"
            assert sources[0].mode == SourceMode.REFCLOCK
