"""CFFI bindings to libchrony system library.

This module contains the ChronyConnection context manager for connecting
to chronyd and retrieving time synchronization status.

Internal implementation - use pychrony.ChronyConnection instead.
"""

import errno
import math
import os
from types import TracebackType
from typing import Any

from ..exceptions import (
    ChronyConnectionError,
    ChronyDataError,
    ChronyLibraryError,
    ChronyPermissionError,
)
from ..models import (
    TrackingStatus,
    Source,
    SourceStats,
    RTCData,
    _ref_id_to_name,
    LeapStatus,
    SourceState,
    SourceMode,
)


# Default socket paths to try (in order)
DEFAULT_SOCKET_PATHS = [
    "/run/chrony/chronyd.sock",
    "/var/run/chrony/chronyd.sock",
]

# Conversion constants
NANOSECONDS_PER_SECOND = 1e9

# Try to import compiled CFFI bindings
# These are generated at build time by CFFI, so they may not exist
_lib: Any = None
_ffi: Any = None

try:
    from pychrony._core._cffi_bindings import lib as _lib, ffi as _ffi  # type: ignore[import-not-found]

    _LIBRARY_AVAILABLE = True
except ImportError:
    _LIBRARY_AVAILABLE = False


def _check_library_available() -> None:
    """Check if libchrony CFFI bindings are available.

    Raises:
        ChronyLibraryError: If libchrony bindings are not compiled or unavailable.
    """
    if not _LIBRARY_AVAILABLE:
        raise ChronyLibraryError(
            "libchrony bindings not available. "
            "Ensure libchrony and libchrony-devel are installed and "
            "the CFFI bindings have been compiled. "
            "Install with: pip install pychrony (on a system with libchrony-devel)"
        )


def _timespec_to_float(ts: Any) -> float:
    """Convert struct timespec to Python float (seconds since epoch).

    Args:
        ts: A CFFI struct timespec with tv_sec and tv_nsec fields

    Returns:
        Floating point seconds since epoch with nanosecond precision
    """
    return ts.tv_sec + ts.tv_nsec / NANOSECONDS_PER_SECOND


def _validate_finite_float(value: float, field_name: str) -> None:
    """Validate that a float value is finite (not NaN or Inf).

    Args:
        value: The float value to validate
        field_name: Name of the field for error messages

    Raises:
        ChronyDataError: If value is NaN or infinite
    """
    if math.isnan(value) or math.isinf(value):
        raise ChronyDataError(f"Invalid {field_name}: {value}")


def _validate_bounded_int(
    value: int, field_name: str, min_val: int, max_val: int
) -> None:
    """Validate that an integer is within bounds.

    Args:
        value: The integer value to validate
        field_name: Name of the field for error messages
        min_val: Minimum allowed value (inclusive)
        max_val: Maximum allowed value (inclusive)

    Raises:
        ChronyDataError: If value is outside bounds
    """
    if not min_val <= value <= max_val:
        raise ChronyDataError(f"Invalid {field_name}: {value}")


def _validate_non_negative_int(value: int, field_name: str) -> None:
    """Validate that an integer is non-negative.

    Args:
        value: The integer value to validate
        field_name: Name of the field for error messages

    Raises:
        ChronyDataError: If value is negative
    """
    if value < 0:
        raise ChronyDataError(f"{field_name} must be non-negative: {value}")


def _get_float_field(session: Any, name: str) -> float:
    """Get a float field by name from the session."""
    index = _lib.chrony_get_field_index(session, name.encode())
    if index < 0:
        raise ChronyDataError(f"Field '{name}' not found (libchrony version mismatch?)")
    return _lib.chrony_get_field_float(session, index)


def _get_uinteger_field(session: Any, name: str) -> int:
    """Get an unsigned integer field by name from the session."""
    index = _lib.chrony_get_field_index(session, name.encode())
    if index < 0:
        raise ChronyDataError(f"Field '{name}' not found (libchrony version mismatch?)")
    return _lib.chrony_get_field_uinteger(session, index)


def _get_integer_field(session: Any, name: str) -> int:
    """Get a signed integer field by name from the session."""
    index = _lib.chrony_get_field_index(session, name.encode())
    if index < 0:
        raise ChronyDataError(f"Field '{name}' not found (libchrony version mismatch?)")
    return _lib.chrony_get_field_integer(session, index)


def _get_string_field(session: Any, name: str) -> str:
    """Get a string field by name from the session."""
    index = _lib.chrony_get_field_index(session, name.encode())
    if index < 0:
        raise ChronyDataError(f"Field '{name}' not found (libchrony version mismatch?)")
    result = _lib.chrony_get_field_string(session, index)
    if result == _ffi.NULL:
        return ""
    return _ffi.string(result).decode("utf-8", errors="replace")


def _get_timespec_field(session: Any, name: str) -> float:
    """Get a timespec field by name, convert to epoch float."""
    index = _lib.chrony_get_field_index(session, name.encode())
    if index < 0:
        raise ChronyDataError(f"Field '{name}' not found (libchrony version mismatch?)")
    ts = _lib.chrony_get_field_timespec(session, index)
    return _timespec_to_float(ts)


class ChronyConnection:
    """Context manager for chrony connections.

    Provides connection reuse for multiple queries to chronyd within a single
    context, properly managing socket and session lifecycle.

    Args:
        address: Connection address. Supports:

            - Unix socket path: ``"/run/chrony/chronyd.sock"``
            - IPv4: ``"192.168.1.1"`` or ``"192.168.1.1:323"``
            - IPv6: ``"2001:db8::1"`` or ``"[2001:db8::1]:323"``
            - ``None``: Auto-detect (tries Unix socket paths, then localhost)

    Methods:
        get_tracking: Get current NTP tracking status (returns `TrackingStatus`).
        get_sources: Get configured time sources (returns ``list[Source]``).
        get_source_stats: Get source statistics (returns ``list[SourceStats]``).
        get_rtc_data: Get RTC tracking data (returns `RTCData` or ``None``).

    Thread Safety:
        NOT thread-safe. Each thread needs its own connection.

    See Also:
        `TrackingStatus`: Tracking data model.
        `Source`: Time source data model.
        `SourceStats`: Source statistics data model.
        `RTCData`: RTC tracking data model.

    Example:
        >>> with ChronyConnection() as conn:
        ...     tracking = conn.get_tracking()
        ...     sources = conn.get_sources()
        ...     stats = conn.get_source_stats()
        ...     rtc = conn.get_rtc_data()
    """

    def __init__(self, address: str | None = None) -> None:
        """Initialize ChronyConnection with optional address.

        Args:
            address: Connection address (see class docstring for formats)
        """
        self._address = address
        self._fd: int | None = None
        self._session: Any = None
        self._session_ptr: Any = None
        self._in_context = False

    def __enter__(self) -> "ChronyConnection":
        """Enter context manager, opening connection to chronyd."""
        _check_library_available()
        self._open()
        self._in_context = True
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """Exit context manager, closing connection to chronyd."""
        self._in_context = False
        self._close()

    def _resolve_address(self) -> bytes | None:
        """Resolve the address to use for connection.

        Returns:
            Encoded address bytes, or None for auto-detect

        Raises:
            ChronyConnectionError: If no socket path found during auto-detect
        """
        if self._address is not None:
            return self._address.encode()

        # Auto-detect: try default Unix socket paths
        for path in DEFAULT_SOCKET_PATHS:
            if os.path.exists(path):
                return path.encode()

        # No Unix socket found - pass NULL to let libchrony try localhost
        return None

    def _open(self) -> None:
        """Open socket connection and initialize session.

        Raises:
            ChronyConnectionError: If connection fails
            ChronyPermissionError: If permission denied
        """
        address_bytes = self._resolve_address()

        # Open socket connection
        if address_bytes is not None:
            self._fd = _lib.chrony_open_socket(address_bytes)
        else:
            self._fd = _lib.chrony_open_socket(_ffi.NULL)

        if self._fd < 0:
            # Check for permission issues
            if self._fd == -errno.EACCES or (
                self._address is not None
                and os.path.exists(self._address)
                and not os.access(self._address, os.R_OK | os.W_OK)
            ):
                raise ChronyPermissionError(
                    f"Permission denied accessing {self._address or 'chronyd'}. "
                    "Run as root or add user to chrony group.",
                    error_code=self._fd,
                )
            address_desc = self._address or "chronyd (auto-detect)"
            raise ChronyConnectionError(
                f"Failed to connect to {address_desc}. Is chronyd running?",
                error_code=self._fd,
            )

        # Initialize session
        self._session_ptr = _ffi.new("chrony_session **")
        err = _lib.chrony_init_session(self._session_ptr, self._fd)
        if err != 0:
            # Clean up socket on failure
            _lib.chrony_close_socket(self._fd)
            self._fd = None
            raise ChronyConnectionError(
                "Failed to initialize chrony session",
                error_code=err,
            )

        self._session = self._session_ptr[0]

    def _close(self) -> None:
        """Close session and socket connection."""
        if self._session is not None and self._session != _ffi.NULL:
            _lib.chrony_deinit_session(self._session)
            self._session = None

        if self._fd is not None and self._fd >= 0:
            _lib.chrony_close_socket(self._fd)
            self._fd = None

        self._session_ptr = None

    def _ensure_context(self) -> None:
        """Ensure we're within a context manager.

        Raises:
            RuntimeError: If called outside context manager
        """
        if not self._in_context:
            raise RuntimeError(
                "ChronyConnection methods must be called within a 'with' block"
            )

    def _request_report(self, report_name: bytes) -> int:
        """Request number of records for a report type.

        Args:
            report_name: Report name (e.g., b"tracking", b"sources")

        Returns:
            Number of records available

        Raises:
            ChronyDataError: If request fails
        """
        err = _lib.chrony_request_report_number_records(self._session, report_name)
        if err != 0:
            raise ChronyDataError(
                f"Failed to request {report_name.decode()} report",
                error_code=err,
            )

        while _lib.chrony_needs_response(self._session):
            err = _lib.chrony_process_response(self._session)
            if err != 0:
                raise ChronyDataError(
                    f"Failed to process {report_name.decode()} response",
                    error_code=err,
                )

        return _lib.chrony_get_report_number_records(self._session)

    def _request_record(self, report_name: bytes, index: int) -> None:
        """Request a specific record from a report.

        Args:
            report_name: Report name (e.g., b"tracking", b"sources")
            index: Record index

        Raises:
            ChronyDataError: If request fails
        """
        err = _lib.chrony_request_record(self._session, report_name, index)
        if err != 0:
            raise ChronyDataError(
                f"Failed to request {report_name.decode()} record {index}",
                error_code=err,
            )

        while _lib.chrony_needs_response(self._session):
            err = _lib.chrony_process_response(self._session)
            if err != 0:
                raise ChronyDataError(
                    f"Failed to process {report_name.decode()} record {index}",
                    error_code=err,
                )

    def get_tracking(self) -> TrackingStatus:
        """Get current tracking status from chronyd.

        Returns:
            TrackingStatus: Current tracking information from chronyd.

        Raises:
            RuntimeError: If called outside context manager
            ChronyDataError: If tracking data is invalid or incomplete.

        Example:
            with ChronyConnection() as conn:
                status = conn.get_tracking()
                print(f"Offset: {status.offset:.6f} seconds")
        """
        self._ensure_context()

        num_records = self._request_report(b"tracking")
        if num_records < 1:
            raise ChronyDataError("No tracking records available")

        self._request_record(b"tracking", 0)

        # Extract fields
        ref_id = _get_uinteger_field(self._session, "reference ID")
        leap_status_int = _get_uinteger_field(self._session, "leap status")

        try:
            leap_status = LeapStatus(leap_status_int)
        except ValueError:
            raise ChronyDataError(
                f"Unknown leap_status value {leap_status_int}. "
                "This may indicate a newer chrony version - please update pychrony."
            )

        data = {
            "reference_id": ref_id,
            "reference_id_name": _ref_id_to_name(ref_id),
            "reference_ip": _get_string_field(self._session, "address"),
            "stratum": _get_uinteger_field(self._session, "stratum"),
            "leap_status": leap_status,
            "ref_time": _get_timespec_field(self._session, "reference time"),
            "offset": _get_float_field(self._session, "current correction"),
            "last_offset": _get_float_field(self._session, "last offset"),
            "rms_offset": _get_float_field(self._session, "RMS offset"),
            "frequency": _get_float_field(self._session, "frequency offset"),
            "residual_freq": _get_float_field(self._session, "residual frequency"),
            "skew": _get_float_field(self._session, "skew"),
            "root_delay": _get_float_field(self._session, "root delay"),
            "root_dispersion": _get_float_field(self._session, "root dispersion"),
            "update_interval": _get_float_field(self._session, "last update interval"),
        }

        # Validate
        self._validate_tracking(data)

        return TrackingStatus(**data)

    def _validate_tracking(self, data: dict) -> None:
        """Validate tracking data before creating TrackingStatus."""
        if not 0 <= data["stratum"] <= 15:
            raise ChronyDataError(f"Invalid stratum: {data['stratum']}")

        float_fields = [
            "ref_time",
            "offset",
            "last_offset",
            "rms_offset",
            "frequency",
            "residual_freq",
            "skew",
            "root_delay",
            "root_dispersion",
            "update_interval",
        ]
        for field in float_fields:
            if math.isnan(data[field]) or math.isinf(data[field]):
                raise ChronyDataError(f"Invalid {field}: {data[field]}")

        non_negative = [
            "ref_time",
            "rms_offset",
            "skew",
            "root_delay",
            "root_dispersion",
            "update_interval",
        ]
        for field in non_negative:
            if data[field] < 0:
                raise ChronyDataError(f"{field} must be non-negative: {data[field]}")

    def get_sources(self) -> list[Source]:
        """Get all configured time sources from chronyd.

        Returns:
            list[Source]: List of Source objects for each configured source.
                Empty list if no sources are configured.

        Raises:
            RuntimeError: If called outside context manager
            ChronyDataError: If source data is invalid or incomplete.

        Example:
            with ChronyConnection() as conn:
                sources = conn.get_sources()
                for src in sources:
                    print(f"{src.address}: stratum {src.stratum}")
        """
        self._ensure_context()

        num_records = self._request_report(b"sources")
        if num_records < 1:
            return []

        sources = []
        for i in range(num_records):
            self._request_record(b"sources", i)
            data = self._extract_source()
            self._validate_source(data)
            sources.append(Source(**data))

        return sources

    def _extract_source(self) -> dict:
        """Extract source fields from the current session record."""
        state_int = _get_uinteger_field(self._session, "state")
        mode_int = _get_uinteger_field(self._session, "mode")

        try:
            state = SourceState(state_int)
        except ValueError:
            raise ChronyDataError(
                f"Unknown state value {state_int}. "
                "This may indicate a newer chrony version - please update pychrony."
            )

        try:
            mode = SourceMode(mode_int)
        except ValueError:
            raise ChronyDataError(
                f"Unknown mode value {mode_int}. "
                "This may indicate a newer chrony version - please update pychrony."
            )

        # In libchrony 0.2, sources report uses TYPE_ADDRESS_OR_UINT32_IN_ADDRESS
        # which exposes either "address" (NTP sources) or "reference ID" (refclocks).
        # We check mode to determine which field to fetch.
        if mode == SourceMode.REFCLOCK:
            ref_id = _get_uinteger_field(self._session, "reference ID")
            address = _ref_id_to_name(ref_id)
        else:
            address = _get_string_field(self._session, "address")

        return {
            "address": address,
            "poll": _get_integer_field(self._session, "poll"),
            "stratum": _get_uinteger_field(self._session, "stratum"),
            "state": state,
            "mode": mode,
            "flags": _get_uinteger_field(self._session, "flags"),
            "reachability": _get_uinteger_field(self._session, "reachability"),
            "last_sample_ago": _get_uinteger_field(self._session, "last sample ago"),
            "orig_latest_meas": _get_float_field(
                self._session, "original last sample offset"
            ),
            "latest_meas": _get_float_field(
                self._session, "adjusted last sample offset"
            ),
            "latest_meas_err": _get_float_field(self._session, "last sample error"),
        }

    def _validate_source(self, data: dict) -> None:
        """Validate source data before creating Source."""
        _validate_bounded_int(data["stratum"], "stratum", 0, 15)
        _validate_bounded_int(data["reachability"], "reachability", 0, 255)
        _validate_non_negative_int(data["last_sample_ago"], "last_sample_ago")

        for field in ["orig_latest_meas", "latest_meas", "latest_meas_err"]:
            _validate_finite_float(data[field], field)

        if data["latest_meas_err"] < 0:
            raise ChronyDataError(
                f"latest_meas_err must be non-negative: {data['latest_meas_err']}"
            )

    def get_source_stats(self) -> list[SourceStats]:
        """Get statistical data for all time sources from chronyd.

        Returns:
            list[SourceStats]: List of SourceStats objects for each source.
                Empty list if no sources are configured.

        Raises:
            RuntimeError: If called outside context manager
            ChronyDataError: If statistics data is invalid or incomplete.

        Example:
            with ChronyConnection() as conn:
                stats = conn.get_source_stats()
                for s in stats:
                    print(f"{s.address}: {s.samples} samples")
        """
        self._ensure_context()

        num_records = self._request_report(b"sourcestats")
        if num_records < 1:
            return []

        stats = []
        for i in range(num_records):
            self._request_record(b"sourcestats", i)
            data = self._extract_sourcestats()
            self._validate_sourcestats(data)
            stats.append(SourceStats(**data))

        return stats

    def _extract_sourcestats(self) -> dict:
        """Extract sourcestats fields from the current session record."""
        return {
            "reference_id": _get_uinteger_field(self._session, "reference ID"),
            "address": _get_string_field(self._session, "address"),
            "samples": _get_uinteger_field(self._session, "samples"),
            "runs": _get_uinteger_field(self._session, "runs"),
            "span": _get_uinteger_field(self._session, "span"),
            "std_dev": _get_float_field(self._session, "standard deviation"),
            "resid_freq": _get_float_field(self._session, "residual frequency"),
            "skew": _get_float_field(self._session, "skew"),
            "offset": _get_float_field(self._session, "offset"),
            "offset_err": _get_float_field(self._session, "offset error"),
        }

    def _validate_sourcestats(self, data: dict) -> None:
        """Validate sourcestats data before creating SourceStats."""
        _validate_non_negative_int(data["samples"], "samples")
        _validate_non_negative_int(data["runs"], "runs")
        _validate_non_negative_int(data["span"], "span")

        for field in ["std_dev", "resid_freq", "skew", "offset", "offset_err"]:
            _validate_finite_float(data[field], field)

        if data["std_dev"] < 0:
            raise ChronyDataError(f"std_dev must be non-negative: {data['std_dev']}")
        if data["skew"] < 0:
            raise ChronyDataError(f"skew must be non-negative: {data['skew']}")
        if data["offset_err"] < 0:
            raise ChronyDataError(
                f"offset_err must be non-negative: {data['offset_err']}"
            )

    def get_rtc_data(self) -> RTCData | None:
        """Get Real-Time Clock tracking data from chronyd.

        Returns:
            RTCData if RTC tracking is enabled, None otherwise.

        Raises:
            RuntimeError: If called outside context manager
            ChronyDataError: If RTC data is invalid or malformed.

        Example:
            with ChronyConnection() as conn:
                rtc = conn.get_rtc_data()
                if rtc:
                    print(f"RTC offset: {rtc.offset:.6f}s")
        """
        self._ensure_context()

        num_records = self._request_report(b"rtcdata")
        if num_records < 1:
            return None

        # Try to fetch rtcdata record - may fail if RTC not actually configured
        try:
            err = _lib.chrony_request_record(self._session, b"rtcdata", 0)
            if err != 0:
                return None

            while _lib.chrony_needs_response(self._session):
                err = _lib.chrony_process_response(self._session)
                if err != 0:
                    return None
        except Exception:
            return None

        data = self._extract_rtc()
        self._validate_rtc(data)

        return RTCData(**data)

    def _extract_rtc(self) -> dict:
        """Extract RTC fields from the current session record."""
        return {
            "ref_time": _get_timespec_field(self._session, "reference time"),
            "samples": _get_uinteger_field(self._session, "samples"),
            "runs": _get_uinteger_field(self._session, "runs"),
            "span": _get_uinteger_field(self._session, "span"),
            "offset": _get_float_field(self._session, "offset"),
            "freq_offset": _get_float_field(self._session, "frequency offset"),
        }

    def _validate_rtc(self, data: dict) -> None:
        """Validate RTC data before creating RTCData."""
        _validate_non_negative_int(data["samples"], "samples")
        _validate_non_negative_int(data["runs"], "runs")
        _validate_non_negative_int(data["span"], "span")

        for field in ["ref_time", "offset", "freq_offset"]:
            _validate_finite_float(data[field], field)

        if data["ref_time"] < 0:
            raise ChronyDataError(f"ref_time must be non-negative: {data['ref_time']}")
