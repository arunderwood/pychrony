"""Unit tests for mock scenarios and context manager.

Tests for patched_chrony_connection and scenario presets.
"""

from __future__ import annotations

import pytest

from pychrony import ChronyConnection
from pychrony.models import LeapStatus, SourceState, SourceMode
from tests.mocks import (
    patched_chrony_connection,
    ChronyStateConfig,
    SCENARIO_NTP_SYNCED,
    SCENARIO_UNSYNC,
    SCENARIO_LEAP_INSERT,
    SCENARIO_LEAP_DELETE,
    SCENARIO_GPS_REFCLOCK,
    SCENARIO_PPS_REFCLOCK,
    SCENARIO_MULTI_SOURCE,
)


class TestPatchedChronyConnection:
    """Test patched_chrony_connection context manager."""

    def test_yields_working_connection(self) -> None:
        """Context manager should yield a working ChronyConnection."""
        with patched_chrony_connection() as conn:
            assert isinstance(conn, ChronyConnection)
            tracking = conn.get_tracking()
            assert tracking is not None

    def test_default_uses_ntp_synced_scenario(self) -> None:
        """Default configuration uses SCENARIO_NTP_SYNCED."""
        with patched_chrony_connection() as conn:
            tracking = conn.get_tracking()
            assert tracking.stratum == SCENARIO_NTP_SYNCED.stratum
            assert tracking.is_synchronized() is True

    def test_custom_config_returns_custom_values(self) -> None:
        """Custom configuration returns custom values."""
        config = ChronyStateConfig(
            stratum=3,
            offset=0.001234,
            reference_id=0x12345678,
        )
        with patched_chrony_connection(config) as conn:
            tracking = conn.get_tracking()
            assert tracking.stratum == 3
            assert tracking.offset == 0.001234

    def test_restores_bindings_on_normal_exit(self) -> None:
        """Bindings are restored after normal exit."""
        from pychrony._core import _bindings

        original_lib = _bindings._lib

        with patched_chrony_connection():
            # Inside context, _lib is mocked
            pass

        # After context, should be restored
        # Note: This may be None if CFFI bindings not compiled
        assert _bindings._lib is original_lib

    def test_restores_bindings_on_exception(self) -> None:
        """Bindings are restored even after exception."""
        from pychrony._core import _bindings

        original_lib = _bindings._lib

        with pytest.raises(ValueError):
            with patched_chrony_connection():
                raise ValueError("Test exception")

        assert _bindings._lib is original_lib


class TestScenarioNtpSynced:
    """Test SCENARIO_NTP_SYNCED preset."""

    def test_is_synchronized(self) -> None:
        """NTP synced scenario should be synchronized."""
        with patched_chrony_connection(SCENARIO_NTP_SYNCED) as conn:
            tracking = conn.get_tracking()
            assert tracking.is_synchronized() is True

    def test_stratum_is_two(self) -> None:
        """NTP synced scenario should have stratum 2."""
        with patched_chrony_connection(SCENARIO_NTP_SYNCED) as conn:
            tracking = conn.get_tracking()
            assert tracking.stratum == 2

    def test_leap_status_is_normal(self) -> None:
        """NTP synced scenario should have normal leap status."""
        with patched_chrony_connection(SCENARIO_NTP_SYNCED) as conn:
            tracking = conn.get_tracking()
            assert tracking.leap_status == LeapStatus.NORMAL

    def test_has_one_source(self) -> None:
        """NTP synced scenario should have one source."""
        with patched_chrony_connection(SCENARIO_NTP_SYNCED) as conn:
            sources = conn.get_sources()
            assert len(sources) == 1

    def test_source_is_selected(self) -> None:
        """NTP synced scenario source should be selected."""
        with patched_chrony_connection(SCENARIO_NTP_SYNCED) as conn:
            sources = conn.get_sources()
            assert sources[0].state == SourceState.SELECTED
            assert sources[0].is_selected() is True


class TestScenarioUnsync:
    """Test SCENARIO_UNSYNC preset."""

    def test_is_not_synchronized(self) -> None:
        """Unsync scenario should not be synchronized."""
        with patched_chrony_connection(SCENARIO_UNSYNC) as conn:
            tracking = conn.get_tracking()
            assert tracking.is_synchronized() is False

    def test_reference_id_is_zero(self) -> None:
        """Unsync scenario should have reference_id 0."""
        with patched_chrony_connection(SCENARIO_UNSYNC) as conn:
            tracking = conn.get_tracking()
            assert tracking.reference_id == 0

    def test_leap_status_is_unsync(self) -> None:
        """Unsync scenario should have UNSYNC leap status."""
        with patched_chrony_connection(SCENARIO_UNSYNC) as conn:
            tracking = conn.get_tracking()
            assert tracking.leap_status == LeapStatus.UNSYNC

    def test_has_no_sources(self) -> None:
        """Unsync scenario should have no sources."""
        with patched_chrony_connection(SCENARIO_UNSYNC) as conn:
            sources = conn.get_sources()
            assert len(sources) == 0


class TestScenarioLeapInsert:
    """Test SCENARIO_LEAP_INSERT preset."""

    def test_leap_status_is_insert(self) -> None:
        """Leap insert scenario should have INSERT leap status."""
        with patched_chrony_connection(SCENARIO_LEAP_INSERT) as conn:
            tracking = conn.get_tracking()
            assert tracking.leap_status == LeapStatus.INSERT

    def test_is_leap_pending(self) -> None:
        """Leap insert scenario should have leap pending."""
        with patched_chrony_connection(SCENARIO_LEAP_INSERT) as conn:
            tracking = conn.get_tracking()
            assert tracking.is_leap_pending() is True


class TestScenarioLeapDelete:
    """Test SCENARIO_LEAP_DELETE preset."""

    def test_leap_status_is_delete(self) -> None:
        """Leap delete scenario should have DELETE leap status."""
        with patched_chrony_connection(SCENARIO_LEAP_DELETE) as conn:
            tracking = conn.get_tracking()
            assert tracking.leap_status == LeapStatus.DELETE

    def test_is_leap_pending(self) -> None:
        """Leap delete scenario should have leap pending."""
        with patched_chrony_connection(SCENARIO_LEAP_DELETE) as conn:
            tracking = conn.get_tracking()
            assert tracking.is_leap_pending() is True


class TestScenarioGpsRefclock:
    """Test SCENARIO_GPS_REFCLOCK preset."""

    def test_stratum_is_one(self) -> None:
        """GPS refclock scenario should have stratum 1."""
        with patched_chrony_connection(SCENARIO_GPS_REFCLOCK) as conn:
            tracking = conn.get_tracking()
            assert tracking.stratum == 1

    def test_source_is_refclock(self) -> None:
        """GPS refclock scenario source should be REFCLOCK mode."""
        with patched_chrony_connection(SCENARIO_GPS_REFCLOCK) as conn:
            sources = conn.get_sources()
            assert len(sources) == 1
            assert sources[0].mode == SourceMode.REFCLOCK

    def test_source_address_is_gps(self) -> None:
        """GPS refclock scenario source should have GPS address."""
        with patched_chrony_connection(SCENARIO_GPS_REFCLOCK) as conn:
            sources = conn.get_sources()
            assert sources[0].address == "GPS"

    def test_source_stratum_is_zero(self) -> None:
        """GPS refclock source should have stratum 0."""
        with patched_chrony_connection(SCENARIO_GPS_REFCLOCK) as conn:
            sources = conn.get_sources()
            assert sources[0].stratum == 0


class TestScenarioPpsRefclock:
    """Test SCENARIO_PPS_REFCLOCK preset."""

    def test_stratum_is_one(self) -> None:
        """PPS refclock scenario should have stratum 1."""
        with patched_chrony_connection(SCENARIO_PPS_REFCLOCK) as conn:
            tracking = conn.get_tracking()
            assert tracking.stratum == 1

    def test_source_is_refclock(self) -> None:
        """PPS refclock scenario source should be REFCLOCK mode."""
        with patched_chrony_connection(SCENARIO_PPS_REFCLOCK) as conn:
            sources = conn.get_sources()
            assert len(sources) == 1
            assert sources[0].mode == SourceMode.REFCLOCK

    def test_source_address_is_pps(self) -> None:
        """PPS refclock scenario source should have PPS address."""
        with patched_chrony_connection(SCENARIO_PPS_REFCLOCK) as conn:
            sources = conn.get_sources()
            assert sources[0].address == "PPS"


class TestScenarioMultiSource:
    """Test SCENARIO_MULTI_SOURCE preset."""

    def test_has_four_sources(self) -> None:
        """Multi-source scenario should have four sources."""
        with patched_chrony_connection(SCENARIO_MULTI_SOURCE) as conn:
            sources = conn.get_sources()
            assert len(sources) == 4

    def test_exactly_one_selected(self) -> None:
        """Multi-source scenario should have exactly one selected source."""
        with patched_chrony_connection(SCENARIO_MULTI_SOURCE) as conn:
            sources = conn.get_sources()
            selected = [s for s in sources if s.is_selected()]
            assert len(selected) == 1

    def test_has_falseticker(self) -> None:
        """Multi-source scenario should have a falseticker."""
        with patched_chrony_connection(SCENARIO_MULTI_SOURCE) as conn:
            sources = conn.get_sources()
            falsetickers = [s for s in sources if s.state == SourceState.FALSETICKER]
            assert len(falsetickers) == 1

    def test_has_unreachable_source(self) -> None:
        """Multi-source scenario should have an unreachable source."""
        with patched_chrony_connection(SCENARIO_MULTI_SOURCE) as conn:
            sources = conn.get_sources()
            unreachable = [s for s in sources if not s.is_reachable()]
            assert len(unreachable) == 1

    def test_source_stats_match_sources(self) -> None:
        """Source stats count should match source count."""
        with patched_chrony_connection(SCENARIO_MULTI_SOURCE) as conn:
            sources = conn.get_sources()
            stats = conn.get_source_stats()
            assert len(stats) == len(sources)


class TestSyncStateTransitions:
    """Test synchronization state scenarios."""

    def test_stratum_zero_is_synchronized(self) -> None:
        """Stratum 0 (reference clock) should be synchronized."""
        config = ChronyStateConfig(stratum=0, reference_id=0x47505300)  # GPS
        with patched_chrony_connection(config) as conn:
            tracking = conn.get_tracking()
            assert tracking.is_synchronized() is True

    def test_stratum_fifteen_boundary(self) -> None:
        """Stratum 15 boundary should be synchronized."""
        config = ChronyStateConfig(stratum=15, reference_id=0xC0A80101)
        with patched_chrony_connection(config) as conn:
            tracking = conn.get_tracking()
            assert tracking.is_synchronized() is True

    def test_reference_id_zero_via_scenario(self) -> None:
        """Reference ID 0 via SCENARIO_UNSYNC should not be synchronized."""
        with patched_chrony_connection(SCENARIO_UNSYNC) as conn:
            tracking = conn.get_tracking()
            assert tracking.is_synchronized() is False

    def test_reference_id_zero_not_synchronized(self) -> None:
        """Reference ID 0 should not be synchronized."""
        config = ChronyStateConfig(stratum=2, reference_id=0)
        with patched_chrony_connection(config) as conn:
            tracking = conn.get_tracking()
            assert tracking.is_synchronized() is False
