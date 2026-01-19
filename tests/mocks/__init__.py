"""Protocol-level test mock infrastructure for pychrony.

This package provides mock infrastructure for testing pychrony without
requiring chronyd, hardware (RTC), or special system states (leap seconds).

Public API:
    Configuration dataclasses:
        - ChronyStateConfig: Root configuration for mock state
        - SourceConfig: Configuration for a single time source
        - RTCConfig: Configuration for RTC data

    Pre-built scenarios:
        - SCENARIO_NTP_SYNCED: Standard synchronized state
        - SCENARIO_UNSYNC: Unsynchronized (stratum 16)
        - SCENARIO_LEAP_INSERT: Leap second insertion pending
        - SCENARIO_LEAP_DELETE: Leap second deletion pending
        - SCENARIO_GPS_REFCLOCK: GPS reference clock at stratum 1
        - SCENARIO_PPS_REFCLOCK: PPS reference clock
        - SCENARIO_RTC_AVAILABLE: RTC configured and calibrated
        - SCENARIO_RTC_UNAVAILABLE: RTC not configured
        - SCENARIO_MULTI_SOURCE: Multiple sources with different states

    Context manager:
        - patched_chrony_connection: Patch CFFI bindings with mock

Error Injection:
    The error_injection dict in ChronyStateConfig maps operation names to
    error codes. Supported operations:
        - "chrony_open_socket": Connection error (-13 for EACCES)
        - "chrony_init_session": Session initialization error
        - "chrony_request_report_number_records": Report request error
        - "chrony_process_response": Response processing error
        - "chrony_request_record": Record request error

Example:
    from tests.mocks import patched_chrony_connection, SCENARIO_LEAP_INSERT

    def test_leap_pending():
        with patched_chrony_connection(SCENARIO_LEAP_INSERT) as conn:
            status = conn.get_tracking()
            assert status.is_leap_pending()
"""

from tests.mocks.config import ChronyStateConfig, SourceConfig, RTCConfig
from tests.mocks.context import patched_chrony_connection
from tests.mocks.scenarios import (
    SCENARIO_NTP_SYNCED,
    SCENARIO_UNSYNC,
    SCENARIO_LEAP_INSERT,
    SCENARIO_LEAP_DELETE,
    SCENARIO_GPS_REFCLOCK,
    SCENARIO_PPS_REFCLOCK,
    SCENARIO_RTC_AVAILABLE,
    SCENARIO_RTC_UNAVAILABLE,
    SCENARIO_MULTI_SOURCE,
)

__all__ = [
    # Configuration dataclasses
    "ChronyStateConfig",
    "SourceConfig",
    "RTCConfig",
    # Pre-built scenarios
    "SCENARIO_NTP_SYNCED",
    "SCENARIO_UNSYNC",
    "SCENARIO_LEAP_INSERT",
    "SCENARIO_LEAP_DELETE",
    "SCENARIO_GPS_REFCLOCK",
    "SCENARIO_PPS_REFCLOCK",
    "SCENARIO_RTC_AVAILABLE",
    "SCENARIO_RTC_UNAVAILABLE",
    "SCENARIO_MULTI_SOURCE",
    # Context manager
    "patched_chrony_connection",
]
