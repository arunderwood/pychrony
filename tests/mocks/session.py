"""Mock session infrastructure for simulating chrony CFFI bindings.

This module provides MockChronySession which creates mock _lib and _ffi
objects that simulate the behavior of the real CFFI bindings.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from pychrony._core._fields import (
    FieldType,
    TRACKING_FIELDS,
    SOURCE_FIELDS,
    SOURCESTATS_FIELDS,
    RTC_FIELDS,
)

if TYPE_CHECKING:
    from tests.mocks.config import ChronyStateConfig


__all__ = [
    "MockTimespec",
    "MockFFI",
    "MockLib",
    "MockChronySession",
]


@dataclass
class MockTimespec:
    """Mock struct timespec for CFFI simulation.

    Attributes:
        tv_sec: Seconds component
        tv_nsec: Nanoseconds component (0-999999999)
    """

    tv_sec: int
    tv_nsec: int

    @classmethod
    def from_float(cls, timestamp: float) -> MockTimespec:
        """Create MockTimespec from a floating-point timestamp.

        Args:
            timestamp: Seconds since epoch (float)

        Returns:
            MockTimespec with separated seconds and nanoseconds
        """
        tv_sec = int(timestamp)
        tv_nsec = int((timestamp - tv_sec) * 1_000_000_000)
        return cls(tv_sec=tv_sec, tv_nsec=tv_nsec)


class MockPointer:
    """Mock CFFI pointer supporting [0] indexing."""

    def __init__(self, value: Any = None) -> None:
        self._value = value

    def __getitem__(self, index: int) -> Any:
        if index != 0:
            raise IndexError("Mock pointer only supports index 0")
        return self._value

    def __setitem__(self, index: int, value: Any) -> None:
        if index != 0:
            raise IndexError("Mock pointer only supports index 0")
        self._value = value


class MockFFI:
    """Mock CFFI ffi object with required methods.

    Provides ffi.NULL, ffi.new(), and ffi.string() methods
    for compatibility with _bindings.py.
    """

    NULL = None

    def new(self, type_string: str) -> MockPointer:
        """Create a new mock pointer.

        Args:
            type_string: CFFI type string (e.g., "chrony_session **")

        Returns:
            MockPointer supporting [0] indexing
        """
        return MockPointer()

    def string(self, char_ptr: Any) -> bytes:
        """Convert char* to bytes.

        Args:
            char_ptr: Character pointer (string or bytes in mock)

        Returns:
            Bytes representation
        """
        if char_ptr is None:
            return b""
        if isinstance(char_ptr, str):
            return char_ptr.encode("utf-8")
        if isinstance(char_ptr, bytes):
            return char_ptr
        return str(char_ptr).encode("utf-8")


class MockLib:
    """Mock CFFI lib object simulating chrony library functions.

    All 15 CFFI functions used by _bindings.py are implemented here.
    """

    def __init__(self, session: MockChronySession) -> None:
        self._session = session

    def chrony_open_socket(self, address: Any) -> int:
        """Mock chrony_open_socket."""
        error = self._session.config.error_injection.get("chrony_open_socket")
        if error is not None:
            return error
        return 5  # Valid file descriptor

    def chrony_close_socket(self, fd: int) -> None:
        """Mock chrony_close_socket."""
        pass

    def chrony_init_session(self, session_ptr: MockPointer, fd: int) -> int:
        """Mock chrony_init_session."""
        error = self._session.config.error_injection.get("chrony_init_session")
        if error is not None:
            return error
        # Set the session pointer value
        session_ptr[0] = self._session
        return 0

    def chrony_deinit_session(self, session: Any) -> None:
        """Mock chrony_deinit_session."""
        pass

    def chrony_request_report_number_records(
        self, session: Any, report_name: bytes
    ) -> int:
        """Mock chrony_request_report_number_records."""
        error = self._session.config.error_injection.get(
            "chrony_request_report_number_records"
        )
        if error is not None:
            return error

        self._session.current_report = report_name.decode("utf-8")
        self._session.pending_responses = 1
        return 0

    def chrony_needs_response(self, session: Any) -> bool:
        """Mock chrony_needs_response."""
        return self._session.pending_responses > 0

    def chrony_process_response(self, session: Any) -> int:
        """Mock chrony_process_response."""
        error = self._session.config.error_injection.get("chrony_process_response")
        if error is not None:
            return error

        if self._session.pending_responses > 0:
            self._session.pending_responses -= 1
        return 0

    def chrony_get_report_number_records(self, session: Any) -> int:
        """Mock chrony_get_report_number_records."""
        report = self._session.current_report
        config = self._session.config

        if report == "tracking":
            return 1
        elif report == "sources":
            return len(config.sources)
        elif report == "sourcestats":
            return len(config.sources)
        elif report == "rtcdata":
            if config.rtc is not None and config.rtc.available:
                return 1
            return 0
        return 0

    def chrony_request_record(
        self, session: Any, report_name: bytes, index: int
    ) -> int:
        """Mock chrony_request_record."""
        error = self._session.config.error_injection.get("chrony_request_record")
        if error is not None:
            return error

        self._session.current_record_index = index
        self._session.pending_responses = 1
        return 0

    def chrony_get_field_index(self, session: Any, field_name: bytes) -> int:
        """Mock chrony_get_field_index."""
        # Enforce protocol: response must be processed before field access
        if self._session.pending_responses > 0:
            return -1

        name = field_name.decode("utf-8")
        report = self._session.current_report

        # Get field registry for current report
        if report == "tracking":
            fields = TRACKING_FIELDS
        elif report == "sources":
            fields = SOURCE_FIELDS
        elif report == "sourcestats":
            fields = SOURCESTATS_FIELDS
        elif report == "rtcdata":
            fields = RTC_FIELDS
        else:
            return -1

        # Return index if field exists
        if name in fields:
            return list(fields.keys()).index(name)
        return -1

    def chrony_get_field_float(self, session: Any, index: int) -> float:
        """Mock chrony_get_field_float."""
        return self._session.get_field_value(index, FieldType.FLOAT)

    def chrony_get_field_uinteger(self, session: Any, index: int) -> int:
        """Mock chrony_get_field_uinteger."""
        return self._session.get_field_value(index, FieldType.UINTEGER)

    def chrony_get_field_integer(self, session: Any, index: int) -> int:
        """Mock chrony_get_field_integer."""
        return self._session.get_field_value(index, FieldType.INTEGER)

    def chrony_get_field_string(self, session: Any, index: int) -> str | None:
        """Mock chrony_get_field_string."""
        value = self._session.get_field_value(index, FieldType.STRING)
        return value if value else None

    def chrony_get_field_timespec(self, session: Any, index: int) -> MockTimespec:
        """Mock chrony_get_field_timespec."""
        return self._session.get_field_value(index, FieldType.TIMESPEC)


class MockChronySession:
    """Mock chrony session that simulates the CFFI bindings.

    Maintains protocol state and returns configured data via
    mock _lib and _ffi objects.

    Attributes:
        config: Configuration driving mock behavior
        current_report: Currently active report name
        current_record_index: Current record being accessed
        pending_responses: Number of responses pending
        lib: Mock _lib object
        ffi: Mock _ffi object
    """

    def __init__(self, config: ChronyStateConfig) -> None:
        self.config = config
        self.current_report: str | None = None
        self.current_record_index: int = 0
        self.pending_responses: int = 0
        self.lib = MockLib(self)
        self.ffi = MockFFI()

    def get_field_value(self, index: int, field_type: FieldType) -> Any:
        """Get field value for current report and record.

        Args:
            index: Field index within the report
            field_type: Expected type of the field

        Returns:
            Field value from configuration
        """
        report = self.current_report

        if report == "tracking":
            return self._get_tracking_field(index)
        elif report == "sources":
            return self._get_source_field(index)
        elif report == "sourcestats":
            return self._get_sourcestats_field(index)
        elif report == "rtcdata":
            return self._get_rtc_field(index)

        return 0

    def _get_tracking_field(self, index: int) -> Any:
        """Get tracking report field by index."""
        config = self.config
        fields = list(TRACKING_FIELDS.keys())

        if index >= len(fields):
            return 0

        field_name = fields[index]

        mapping = {
            "reference ID": config.reference_id,
            "stratum": config.stratum,
            "leap status": config.leap_status.value,
            "address": config.reference_ip,
            "current correction": config.offset,
            "last offset": config.last_offset,
            "RMS offset": config.rms_offset,
            "frequency offset": config.frequency,
            "residual frequency": config.residual_freq,
            "skew": config.skew,
            "root delay": config.root_delay,
            "root dispersion": config.root_dispersion,
            "last update interval": config.update_interval,
            "reference time": MockTimespec.from_float(config.ref_time),
        }

        return mapping.get(field_name, 0)

    def _get_source_field(self, index: int) -> Any:
        """Get sources report field by index."""
        config = self.config
        record_idx = self.current_record_index

        if record_idx >= len(config.sources):
            return 0

        source = config.sources[record_idx]
        fields = list(SOURCE_FIELDS.keys())

        if index >= len(fields):
            return 0

        field_name = fields[index]

        # Compute reference_id if not set
        ref_id = source.reference_id
        if ref_id is None:
            ref_id = source.compute_reference_id()

        mapping = {
            "address": source.address,
            "reference ID": ref_id,
            "state": source.state.value,
            "mode": source.mode.value,
            "poll": source.poll,
            "stratum": source.stratum,
            "flags": source.flags,
            "reachability": source.reachability,
            "last sample ago": source.last_sample_ago,
            "original last sample offset": source.orig_latest_meas,
            "adjusted last sample offset": source.latest_meas,
            "last sample error": source.latest_meas_err,
        }

        return mapping.get(field_name, 0)

    def _get_sourcestats_field(self, index: int) -> Any:
        """Get sourcestats report field by index."""
        config = self.config
        record_idx = self.current_record_index

        if record_idx >= len(config.sources):
            return 0

        source = config.sources[record_idx]
        fields = list(SOURCESTATS_FIELDS.keys())

        if index >= len(fields):
            return 0

        field_name = fields[index]

        # Compute reference_id if not set
        ref_id = source.reference_id
        if ref_id is None:
            ref_id = source.compute_reference_id()

        mapping = {
            "reference ID": ref_id,
            "address": source.address,
            "samples": source.samples,
            "runs": source.runs,
            "span": source.span,
            "standard deviation": source.std_dev,
            "residual frequency": source.resid_freq,
            "skew": source.stats_skew,
            "offset": source.stats_offset,
            "offset error": source.offset_err,
        }

        return mapping.get(field_name, 0)

    def _get_rtc_field(self, index: int) -> Any:
        """Get rtcdata report field by index."""
        config = self.config

        if config.rtc is None or not config.rtc.available:
            return 0

        rtc = config.rtc
        fields = list(RTC_FIELDS.keys())

        if index >= len(fields):
            return 0

        field_name = fields[index]

        mapping = {
            "reference time": MockTimespec.from_float(rtc.ref_time),
            "samples": rtc.samples,
            "runs": rtc.runs,
            "span": rtc.span,
            "offset": rtc.offset,
            "frequency offset": rtc.freq_offset,
        }

        return mapping.get(field_name, 0)
