"""Pre-built scenario configurations for common testing needs.

This module provides ready-to-use ChronyStateConfig instances covering
the most common testing scenarios.
"""

from __future__ import annotations

from pychrony.models import LeapStatus, SourceState, SourceMode
from tests.mocks.config import ChronyStateConfig, SourceConfig, RTCConfig


__all__ = [
    "SCENARIO_NTP_SYNCED",
    "SCENARIO_UNSYNC",
    "SCENARIO_LEAP_INSERT",
    "SCENARIO_LEAP_DELETE",
    "SCENARIO_GPS_REFCLOCK",
    "SCENARIO_PPS_REFCLOCK",
    "SCENARIO_RTC_AVAILABLE",
    "SCENARIO_RTC_UNAVAILABLE",
    "SCENARIO_MULTI_SOURCE",
]


# =============================================================================
# Standard NTP Scenarios
# =============================================================================

SCENARIO_NTP_SYNCED = ChronyStateConfig(
    stratum=2,
    reference_id=0xC0A80164,  # 192.168.1.100
    reference_ip="192.168.1.100",
    leap_status=LeapStatus.NORMAL,
    ref_time=1705320000.123456789,
    offset=0.000123456,
    last_offset=0.000111222,
    rms_offset=0.000100000,
    frequency=1.234,
    residual_freq=0.001,
    skew=0.005,
    root_delay=0.001234,
    root_dispersion=0.002345,
    update_interval=64.0,
    sources=[
        SourceConfig(
            address="192.168.1.100",
            poll=6,
            stratum=1,
            state=SourceState.SELECTED,
            mode=SourceMode.CLIENT,
            reachability=255,
            last_sample_ago=32,
            orig_latest_meas=0.000123456,
            latest_meas=0.000123456,
            latest_meas_err=0.000010000,
        ),
    ],
)
"""Standard synchronized NTP state with one selected source."""


SCENARIO_UNSYNC = ChronyStateConfig(
    stratum=0,
    reference_id=0,
    reference_ip="",
    leap_status=LeapStatus.UNSYNC,
    ref_time=0.0,
    offset=0.0,
    last_offset=0.0,
    rms_offset=0.0,
    frequency=0.0,
    residual_freq=0.0,
    skew=0.0,
    root_delay=0.0,
    root_dispersion=0.0,
    update_interval=0.0,
    sources=[],
)
"""Unsynchronized state (reference_id=0, no sources).

Note: Production code validates stratum 0-15. Unsynchronized state is indicated
by reference_id=0 rather than stratum=16. The is_synchronized() method checks
for reference_id != 0 AND stratum < 16.
"""


# =============================================================================
# Leap Second Scenarios
# =============================================================================

SCENARIO_LEAP_INSERT = ChronyStateConfig(
    stratum=2,
    reference_id=0xC0A80164,
    reference_ip="192.168.1.100",
    leap_status=LeapStatus.INSERT,
    ref_time=1705320000.123456789,
    offset=0.000123456,
    last_offset=0.000111222,
    rms_offset=0.000100000,
    frequency=1.234,
    residual_freq=0.001,
    skew=0.005,
    root_delay=0.001234,
    root_dispersion=0.002345,
    update_interval=64.0,
    sources=[
        SourceConfig(
            address="192.168.1.100",
            poll=6,
            stratum=1,
            state=SourceState.SELECTED,
            mode=SourceMode.CLIENT,
            reachability=255,
        ),
    ],
)
"""Leap second insertion pending (June 30 or December 31)."""


SCENARIO_LEAP_DELETE = ChronyStateConfig(
    stratum=2,
    reference_id=0xC0A80164,
    reference_ip="192.168.1.100",
    leap_status=LeapStatus.DELETE,
    ref_time=1705320000.123456789,
    offset=0.000123456,
    last_offset=0.000111222,
    rms_offset=0.000100000,
    frequency=1.234,
    residual_freq=0.001,
    skew=0.005,
    root_delay=0.001234,
    root_dispersion=0.002345,
    update_interval=64.0,
    sources=[
        SourceConfig(
            address="192.168.1.100",
            poll=6,
            stratum=1,
            state=SourceState.SELECTED,
            mode=SourceMode.CLIENT,
            reachability=255,
        ),
    ],
)
"""Leap second deletion pending (theoretical, never used in practice)."""


# =============================================================================
# Reference Clock Scenarios
# =============================================================================

# GPS reference ID: "GPS" as ASCII (0x47505300)
_GPS_REF_ID = 0x47505300

SCENARIO_GPS_REFCLOCK = ChronyStateConfig(
    stratum=1,
    reference_id=_GPS_REF_ID,
    reference_ip="GPS",
    leap_status=LeapStatus.NORMAL,
    ref_time=1705320000.123456789,
    offset=0.000001234,
    last_offset=0.000001111,
    rms_offset=0.000001000,
    frequency=0.123,
    residual_freq=0.0001,
    skew=0.0005,
    root_delay=0.0,
    root_dispersion=0.000001,
    update_interval=1.0,
    sources=[
        SourceConfig(
            address="GPS",
            reference_id=_GPS_REF_ID,
            poll=4,
            stratum=0,
            state=SourceState.SELECTED,
            mode=SourceMode.REFCLOCK,
            reachability=255,
            last_sample_ago=1,
            orig_latest_meas=0.000001234,
            latest_meas=0.000001234,
            latest_meas_err=0.000000100,
        ),
    ],
)
"""GPS reference clock at stratum 1."""


# PPS reference ID: "PPS" as ASCII (0x50505300)
_PPS_REF_ID = 0x50505300

SCENARIO_PPS_REFCLOCK = ChronyStateConfig(
    stratum=1,
    reference_id=_PPS_REF_ID,
    reference_ip="PPS",
    leap_status=LeapStatus.NORMAL,
    ref_time=1705320000.123456789,
    offset=0.000000123,
    last_offset=0.000000111,
    rms_offset=0.000000100,
    frequency=0.012,
    residual_freq=0.00001,
    skew=0.00005,
    root_delay=0.0,
    root_dispersion=0.0000001,
    update_interval=1.0,
    sources=[
        SourceConfig(
            address="PPS",
            reference_id=_PPS_REF_ID,
            poll=4,
            stratum=0,
            state=SourceState.SELECTED,
            mode=SourceMode.REFCLOCK,
            reachability=255,
            last_sample_ago=1,
            orig_latest_meas=0.000000123,
            latest_meas=0.000000123,
            latest_meas_err=0.000000010,
        ),
    ],
)
"""PPS (Pulse Per Second) reference clock at stratum 1."""


# =============================================================================
# RTC Scenarios
# =============================================================================

SCENARIO_RTC_AVAILABLE = ChronyStateConfig(
    stratum=2,
    reference_id=0xC0A80164,
    reference_ip="192.168.1.100",
    leap_status=LeapStatus.NORMAL,
    ref_time=1705320000.123456789,
    offset=0.000123456,
    last_offset=0.000111222,
    rms_offset=0.000100000,
    frequency=1.234,
    residual_freq=0.001,
    skew=0.005,
    root_delay=0.001234,
    root_dispersion=0.002345,
    update_interval=64.0,
    sources=[
        SourceConfig(
            address="192.168.1.100",
            poll=6,
            stratum=1,
            state=SourceState.SELECTED,
            mode=SourceMode.CLIENT,
            reachability=255,
        ),
    ],
    rtc=RTCConfig(
        available=True,
        ref_time=1705320000.123456789,
        samples=10,
        runs=4,
        span=86400,
        offset=0.123456,
        freq_offset=-1.234,
    ),
)
"""NTP synchronized with RTC configured and calibrated."""


SCENARIO_RTC_UNAVAILABLE = ChronyStateConfig(
    stratum=2,
    reference_id=0xC0A80164,
    reference_ip="192.168.1.100",
    leap_status=LeapStatus.NORMAL,
    ref_time=1705320000.123456789,
    offset=0.000123456,
    last_offset=0.000111222,
    rms_offset=0.000100000,
    frequency=1.234,
    residual_freq=0.001,
    skew=0.005,
    root_delay=0.001234,
    root_dispersion=0.002345,
    update_interval=64.0,
    sources=[
        SourceConfig(
            address="192.168.1.100",
            poll=6,
            stratum=1,
            state=SourceState.SELECTED,
            mode=SourceMode.CLIENT,
            reachability=255,
        ),
    ],
    rtc=None,
)
"""NTP synchronized without RTC (no hardware or not configured)."""


# =============================================================================
# Multi-Source Scenarios
# =============================================================================

SCENARIO_MULTI_SOURCE = ChronyStateConfig(
    stratum=2,
    reference_id=0xC0A80164,  # 192.168.1.100
    reference_ip="192.168.1.100",
    leap_status=LeapStatus.NORMAL,
    ref_time=1705320000.123456789,
    offset=0.000123456,
    last_offset=0.000111222,
    rms_offset=0.000100000,
    frequency=1.234,
    residual_freq=0.001,
    skew=0.005,
    root_delay=0.001234,
    root_dispersion=0.002345,
    update_interval=64.0,
    sources=[
        # Selected source (best)
        SourceConfig(
            address="192.168.1.100",
            poll=6,
            stratum=1,
            state=SourceState.SELECTED,
            mode=SourceMode.CLIENT,
            reachability=255,
            last_sample_ago=32,
            orig_latest_meas=0.000123456,
            latest_meas=0.000123456,
            latest_meas_err=0.000010000,
        ),
        # Selectable source (good backup)
        SourceConfig(
            address="192.168.1.101",
            poll=6,
            stratum=2,
            state=SourceState.SELECTABLE,
            mode=SourceMode.CLIENT,
            reachability=255,
            last_sample_ago=64,
            orig_latest_meas=0.000234567,
            latest_meas=0.000234567,
            latest_meas_err=0.000020000,
        ),
        # Unselected source (unreachable)
        SourceConfig(
            address="192.168.1.102",
            poll=6,
            stratum=2,
            state=SourceState.UNSELECTED,
            mode=SourceMode.CLIENT,
            reachability=0,
            last_sample_ago=3600,
            orig_latest_meas=0.0,
            latest_meas=0.0,
            latest_meas_err=0.0,
        ),
        # Falseticker (detected as bad)
        SourceConfig(
            address="192.168.1.103",
            poll=6,
            stratum=2,
            state=SourceState.FALSETICKER,
            mode=SourceMode.CLIENT,
            reachability=255,
            last_sample_ago=32,
            orig_latest_meas=1.234567890,  # Large offset
            latest_meas=1.234567890,
            latest_meas_err=0.100000000,
        ),
    ],
)
"""Multiple sources with different selection states."""
