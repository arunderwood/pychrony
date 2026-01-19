"""Unit tests for leap second mock scenarios.

Tests for leap second INSERT and DELETE states.
"""

from __future__ import annotations

from pychrony.models import LeapStatus
from tests.mocks import (
    patched_chrony_connection,
    ChronyStateConfig,
    SCENARIO_LEAP_INSERT,
    SCENARIO_LEAP_DELETE,
    SCENARIO_NTP_SYNCED,
)


class TestLeapStatusInsert:
    """Test LeapStatus.INSERT scenarios."""

    def test_leap_insert_is_pending(self) -> None:
        """Leap INSERT status should be pending."""
        with patched_chrony_connection(SCENARIO_LEAP_INSERT) as conn:
            tracking = conn.get_tracking()
            assert tracking.is_leap_pending() is True

    def test_leap_insert_status_value(self) -> None:
        """Leap INSERT status should have correct enum value."""
        with patched_chrony_connection(SCENARIO_LEAP_INSERT) as conn:
            tracking = conn.get_tracking()
            assert tracking.leap_status == LeapStatus.INSERT

    def test_custom_leap_insert(self) -> None:
        """Custom config with INSERT leap status."""
        config = ChronyStateConfig(leap_status=LeapStatus.INSERT)
        with patched_chrony_connection(config) as conn:
            tracking = conn.get_tracking()
            assert tracking.leap_status == LeapStatus.INSERT
            assert tracking.is_leap_pending() is True


class TestLeapStatusDelete:
    """Test LeapStatus.DELETE scenarios."""

    def test_leap_delete_is_pending(self) -> None:
        """Leap DELETE status should be pending."""
        with patched_chrony_connection(SCENARIO_LEAP_DELETE) as conn:
            tracking = conn.get_tracking()
            assert tracking.is_leap_pending() is True

    def test_leap_delete_status_value(self) -> None:
        """Leap DELETE status should have correct enum value."""
        with patched_chrony_connection(SCENARIO_LEAP_DELETE) as conn:
            tracking = conn.get_tracking()
            assert tracking.leap_status == LeapStatus.DELETE

    def test_custom_leap_delete(self) -> None:
        """Custom config with DELETE leap status."""
        config = ChronyStateConfig(leap_status=LeapStatus.DELETE)
        with patched_chrony_connection(config) as conn:
            tracking = conn.get_tracking()
            assert tracking.leap_status == LeapStatus.DELETE
            assert tracking.is_leap_pending() is True


class TestLeapStatusNormal:
    """Test LeapStatus.NORMAL scenarios."""

    def test_leap_normal_not_pending(self) -> None:
        """Leap NORMAL status should not be pending."""
        with patched_chrony_connection(SCENARIO_NTP_SYNCED) as conn:
            tracking = conn.get_tracking()
            assert tracking.is_leap_pending() is False

    def test_leap_normal_status_value(self) -> None:
        """Leap NORMAL status should have correct enum value."""
        with patched_chrony_connection(SCENARIO_NTP_SYNCED) as conn:
            tracking = conn.get_tracking()
            assert tracking.leap_status == LeapStatus.NORMAL


class TestLeapStatusUnsync:
    """Test LeapStatus.UNSYNC scenarios."""

    def test_leap_unsync_not_pending(self) -> None:
        """Leap UNSYNC status should not be pending."""
        config = ChronyStateConfig(leap_status=LeapStatus.UNSYNC)
        with patched_chrony_connection(config) as conn:
            tracking = conn.get_tracking()
            assert tracking.is_leap_pending() is False

    def test_leap_unsync_status_value(self) -> None:
        """Leap UNSYNC status should have correct enum value."""
        config = ChronyStateConfig(leap_status=LeapStatus.UNSYNC)
        with patched_chrony_connection(config) as conn:
            tracking = conn.get_tracking()
            assert tracking.leap_status == LeapStatus.UNSYNC


class TestLeapStatusAllValues:
    """Test all LeapStatus enum values."""

    def test_all_leap_status_values(self) -> None:
        """All LeapStatus values should be settable."""
        for status in LeapStatus:
            config = ChronyStateConfig(leap_status=status)
            with patched_chrony_connection(config) as conn:
                tracking = conn.get_tracking()
                assert tracking.leap_status == status
