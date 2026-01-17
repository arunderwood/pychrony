"""CFFI bindings to libchrony system library.

This module contains the Python wrapper functions for libchrony functionality.
It provides the get_tracking() function for retrieving tracking status.

Internal implementation - use pychrony.get_tracking() instead.
"""

import math
import os
from typing import Any, Optional

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


def _validate_tracking(data: dict) -> None:
    """Validate tracking data before creating TrackingStatus.

    Args:
        data: Dictionary of tracking field values

    Raises:
        ChronyDataError: If any field fails validation
    """
    # Stratum bounds
    if not 0 <= data["stratum"] <= 15:
        raise ChronyDataError(f"Invalid stratum: {data['stratum']}")

    # leap_status is validated during enum conversion in _extract_tracking_fields

    # Float validity
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

    # Non-negative fields
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


def _get_float_field(session: Any, name: str) -> float:
    """Get a float field by name from the session.

    Args:
        session: Active chrony session
        name: Field name (e.g., "current correction")

    Returns:
        Float value of the field

    Raises:
        ChronyDataError: If field not found
    """
    index = _lib.chrony_get_field_index(session, name.encode())
    if index < 0:
        raise ChronyDataError(f"Field '{name}' not found (libchrony version mismatch?)")
    return _lib.chrony_get_field_float(session, index)


def _get_uinteger_field(session: Any, name: str) -> int:
    """Get an unsigned integer field by name from the session.

    Args:
        session: Active chrony session
        name: Field name (e.g., "stratum")

    Returns:
        Integer value of the field

    Raises:
        ChronyDataError: If field not found
    """
    index = _lib.chrony_get_field_index(session, name.encode())
    if index < 0:
        raise ChronyDataError(f"Field '{name}' not found (libchrony version mismatch?)")
    return _lib.chrony_get_field_uinteger(session, index)


def _get_string_field(session: Any, name: str) -> str:
    """Get a string field by name from the session.

    Args:
        session: Active chrony session
        name: Field name (e.g., "ip address")

    Returns:
        String value of the field

    Raises:
        ChronyDataError: If field not found
    """
    index = _lib.chrony_get_field_index(session, name.encode())
    if index < 0:
        raise ChronyDataError(f"Field '{name}' not found (libchrony version mismatch?)")
    result = _lib.chrony_get_field_string(session, index)
    if result == _ffi.NULL:
        return ""
    return _ffi.string(result).decode("utf-8", errors="replace")


def _get_timespec_field(session: Any, name: str) -> float:
    """Get a timespec field by name, convert to epoch float.

    Args:
        session: Active chrony session
        name: Field name (e.g., "reference time")

    Returns:
        Float seconds since epoch

    Raises:
        ChronyDataError: If field not found
    """
    index = _lib.chrony_get_field_index(session, name.encode())
    if index < 0:
        raise ChronyDataError(f"Field '{name}' not found (libchrony version mismatch?)")
    ts = _lib.chrony_get_field_timespec(session, index)
    return _timespec_to_float(ts)


def _extract_tracking_fields(session: Any) -> dict:
    """Extract all tracking fields from the session.

    Args:
        session: Active chrony session after processing response

    Returns:
        Dictionary with all tracking field values

    Note: Field names are case-sensitive and must match libchrony's naming:
        - "reference ID" (capital ID)
        - "RMS offset" (capital RMS)
        - "address" (not "ip address")
        - "frequency offset" (not just "frequency")
    """
    ref_id = _get_uinteger_field(session, "reference ID")
    leap_status_int = _get_uinteger_field(session, "leap status")

    try:
        leap_status = LeapStatus(leap_status_int)
    except ValueError:
        raise ChronyDataError(
            f"Unknown leap_status value {leap_status_int}. "
            "This may indicate a newer chrony version - please update pychrony."
        )

    return {
        "reference_id": ref_id,
        "reference_id_name": _ref_id_to_name(ref_id),
        "reference_ip": _get_string_field(session, "address"),
        "stratum": _get_uinteger_field(session, "stratum"),
        "leap_status": leap_status,
        "ref_time": _get_timespec_field(session, "reference time"),
        "offset": _get_float_field(session, "current correction"),
        "last_offset": _get_float_field(session, "last offset"),
        "rms_offset": _get_float_field(session, "RMS offset"),
        "frequency": _get_float_field(session, "frequency offset"),
        "residual_freq": _get_float_field(session, "residual frequency"),
        "skew": _get_float_field(session, "skew"),
        "root_delay": _get_float_field(session, "root delay"),
        "root_dispersion": _get_float_field(session, "root dispersion"),
        "update_interval": _get_float_field(session, "last update interval"),
    }


def _find_socket_path(socket_path: Optional[str]) -> str:
    """Find an accessible socket path.

    Args:
        socket_path: User-provided path or None for auto-detection

    Returns:
        Path to use for connection

    Raises:
        ChronyConnectionError: If no socket path found
    """
    if socket_path is not None:
        return socket_path

    # Try default paths
    for path in DEFAULT_SOCKET_PATHS:
        if os.path.exists(path):
            return path

    raise ChronyConnectionError(
        f"chronyd socket not found. Tried: {', '.join(DEFAULT_SOCKET_PATHS)}. "
        "Is chronyd running?"
    )


def get_tracking(socket_path: Optional[str] = None) -> TrackingStatus:
    """Get current tracking status from chronyd.

    Connects to chronyd and retrieves the current time synchronization
    tracking information.

    Args:
        socket_path: Path to chronyd Unix socket. Defaults to
            '/run/chrony/chronyd.sock' or '/var/run/chrony/chronyd.sock'.

    Returns:
        TrackingStatus: Current tracking information from chronyd.

    Raises:
        ChronyLibraryError: If libchrony is not installed or cannot be loaded.
        ChronyConnectionError: If chronyd is not running or unreachable.
        ChronyPermissionError: If insufficient permissions to access chronyd.
        ChronyDataError: If tracking data is invalid or incomplete.

    Example:
        >>> from pychrony import get_tracking
        >>> status = get_tracking()
        >>> print(f"Offset: {status.offset:.6f} seconds")
        Offset: 0.000123 seconds
    """
    _check_library_available()

    # Find socket path
    actual_path = _find_socket_path(socket_path)

    # Open socket connection
    fd = _lib.chrony_open_socket(actual_path.encode())
    if fd < 0:
        # Check for permission issues
        if fd == -13 or (
            os.path.exists(actual_path)
            and not os.access(actual_path, os.R_OK | os.W_OK)
        ):
            raise ChronyPermissionError(
                f"Permission denied accessing {actual_path}. "
                "Run as root or add user to chrony group.",
                error_code=fd,
            )
        raise ChronyConnectionError(
            f"Failed to connect to chronyd at {actual_path}. Is chronyd running?",
            error_code=fd,
        )

    # Initialize session
    session = _ffi.new("chrony_session **")
    try:
        err = _lib.chrony_init_session(session, fd)
        if err != 0:
            raise ChronyConnectionError(
                "Failed to initialize chrony session",
                error_code=err,
            )

        # Step 1: Request number of tracking records
        err = _lib.chrony_request_report_number_records(session[0], b"tracking")
        if err != 0:
            raise ChronyDataError(
                "Failed to request tracking report",
                error_code=err,
            )

        # Step 2: Process response(s) for number of records
        while _lib.chrony_needs_response(session[0]):
            err = _lib.chrony_process_response(session[0])
            if err != 0:
                raise ChronyDataError(
                    "Failed to process tracking response",
                    error_code=err,
                )

        # Step 3: Get number of records (should be 1 for tracking)
        num_records = _lib.chrony_get_report_number_records(session[0])
        if num_records < 1:
            raise ChronyDataError("No tracking records available")

        # Step 4: Request the first (and only) tracking record
        err = _lib.chrony_request_record(session[0], b"tracking", 0)
        if err != 0:
            raise ChronyDataError(
                "Failed to request tracking record",
                error_code=err,
            )

        # Step 5: Process response(s) for record data
        while _lib.chrony_needs_response(session[0]):
            err = _lib.chrony_process_response(session[0])
            if err != 0:
                raise ChronyDataError(
                    "Failed to process tracking record",
                    error_code=err,
                )

        # Step 6: Extract and validate fields
        data = _extract_tracking_fields(session[0])
        _validate_tracking(data)

        return TrackingStatus(**data)

    finally:
        if session[0] != _ffi.NULL:
            _lib.chrony_deinit_session(session[0])


def _validate_source(data: dict) -> None:
    """Validate source data before creating Source.

    Args:
        data: Dictionary of source field values

    Raises:
        ChronyDataError: If any field fails validation
    """
    # mode and state are validated during enum conversion in _get_source_from_record

    # Stratum bounds (0-15)
    _validate_bounded_int(data["stratum"], "stratum", 0, 15)

    # Reachability bounds (0-255)
    _validate_bounded_int(data["reachability"], "reachability", 0, 255)

    # Non-negative integers
    _validate_non_negative_int(data["last_sample_ago"], "last_sample_ago")

    # All float fields must be finite
    for field in ["orig_latest_meas", "latest_meas", "latest_meas_err"]:
        _validate_finite_float(data[field], field)

    # latest_meas_err must be non-negative
    if data["latest_meas_err"] < 0:
        raise ChronyDataError(
            f"latest_meas_err must be non-negative: {data['latest_meas_err']}"
        )


def _get_source_from_record(session: Any) -> dict:
    """Extract source fields from the current session record.

    Args:
        session: Active chrony session after processing response

    Returns:
        Dictionary with all source field values
    """
    # Try to get address first, fall back to reference ID string
    address = _get_string_field(session, "address")
    if not address:
        # For reference clocks, address might be in "reference ID" field
        ref_id = _get_uinteger_field(session, "reference ID")
        address = _ref_id_to_name(ref_id)

    state_int = _get_uinteger_field(session, "state")
    mode_int = _get_uinteger_field(session, "mode")

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

    return {
        "address": address,
        "poll": _get_integer_field(session, "poll"),
        "stratum": _get_uinteger_field(session, "stratum"),
        "state": state,
        "mode": mode,
        "flags": _get_uinteger_field(session, "flags"),
        "reachability": _get_uinteger_field(session, "reachability"),
        "last_sample_ago": _get_uinteger_field(session, "last sample ago"),
        "orig_latest_meas": _get_float_field(session, "original last sample offset"),
        "latest_meas": _get_float_field(session, "adjusted last sample offset"),
        "latest_meas_err": _get_float_field(session, "last sample error"),
    }


def _get_integer_field(session: Any, name: str) -> int:
    """Get a signed integer field by name from the session.

    Args:
        session: Active chrony session
        name: Field name (e.g., "poll")

    Returns:
        Integer value of the field

    Raises:
        ChronyDataError: If field not found
    """
    index = _lib.chrony_get_field_index(session, name.encode())
    if index < 0:
        raise ChronyDataError(f"Field '{name}' not found (libchrony version mismatch?)")
    return _lib.chrony_get_field_integer(session, index)


def get_sources(socket_path: Optional[str] = None) -> list[Source]:
    """Get all configured time sources from chronyd.

    Connects to chronyd and retrieves information about all configured
    NTP servers, peers, and reference clocks.

    Args:
        socket_path: Path to chronyd Unix socket. Defaults to
            '/run/chrony/chronyd.sock' or '/var/run/chrony/chronyd.sock'.

    Returns:
        list[Source]: List of Source objects for each configured source.
            Empty list if no sources are configured.

    Raises:
        ChronyLibraryError: If libchrony is not installed or cannot be loaded.
        ChronyConnectionError: If chronyd is not running or unreachable.
        ChronyPermissionError: If insufficient permissions to access chronyd.
        ChronyDataError: If source data is invalid or incomplete.

    Example:
        >>> from pychrony import get_sources
        >>> sources = get_sources()
        >>> for src in sources:
        ...     print(f"{src.address}: stratum {src.stratum}, state {src.state_name}")
        pool.ntp.org: stratum 2, state selected
    """
    _check_library_available()

    # Find socket path
    actual_path = _find_socket_path(socket_path)

    # Open socket connection
    fd = _lib.chrony_open_socket(actual_path.encode())
    if fd < 0:
        # Check for permission issues
        if fd == -13 or (
            os.path.exists(actual_path)
            and not os.access(actual_path, os.R_OK | os.W_OK)
        ):
            raise ChronyPermissionError(
                f"Permission denied accessing {actual_path}. "
                "Run as root or add user to chrony group.",
                error_code=fd,
            )
        raise ChronyConnectionError(
            f"Failed to connect to chronyd at {actual_path}. Is chronyd running?",
            error_code=fd,
        )

    # Initialize session
    session = _ffi.new("chrony_session **")
    try:
        err = _lib.chrony_init_session(session, fd)
        if err != 0:
            raise ChronyConnectionError(
                "Failed to initialize chrony session",
                error_code=err,
            )

        # Step 1: Request number of source records
        err = _lib.chrony_request_report_number_records(session[0], b"sources")
        if err != 0:
            raise ChronyDataError(
                "Failed to request sources report",
                error_code=err,
            )

        # Step 2: Process response(s) for number of records
        while _lib.chrony_needs_response(session[0]):
            err = _lib.chrony_process_response(session[0])
            if err != 0:
                raise ChronyDataError(
                    "Failed to process sources response",
                    error_code=err,
                )

        # Step 3: Get number of records
        num_records = _lib.chrony_get_report_number_records(session[0])

        # Empty list if no sources (not an error)
        if num_records < 1:
            return []

        # Step 4: Iterate through all records
        sources = []
        for i in range(num_records):
            err = _lib.chrony_request_record(session[0], b"sources", i)
            if err != 0:
                raise ChronyDataError(
                    f"Failed to request source record {i}",
                    error_code=err,
                )

            # Process response(s) for record data
            while _lib.chrony_needs_response(session[0]):
                err = _lib.chrony_process_response(session[0])
                if err != 0:
                    raise ChronyDataError(
                        f"Failed to process source record {i}",
                        error_code=err,
                    )

            # Extract and validate fields
            data = _get_source_from_record(session[0])
            _validate_source(data)
            sources.append(Source(**data))

        return sources

    finally:
        if session[0] != _ffi.NULL:
            _lib.chrony_deinit_session(session[0])


def _validate_sourcestats(data: dict) -> None:
    """Validate sourcestats data before creating SourceStats.

    Args:
        data: Dictionary of sourcestats field values

    Raises:
        ChronyDataError: If any field fails validation
    """
    # Non-negative integers
    _validate_non_negative_int(data["samples"], "samples")
    _validate_non_negative_int(data["runs"], "runs")
    _validate_non_negative_int(data["span"], "span")

    # All float fields must be finite
    for field in ["std_dev", "resid_freq", "skew", "offset", "offset_err"]:
        _validate_finite_float(data[field], field)

    # Non-negative float fields
    if data["std_dev"] < 0:
        raise ChronyDataError(f"std_dev must be non-negative: {data['std_dev']}")
    if data["skew"] < 0:
        raise ChronyDataError(f"skew must be non-negative: {data['skew']}")
    if data["offset_err"] < 0:
        raise ChronyDataError(f"offset_err must be non-negative: {data['offset_err']}")


def _get_sourcestats_from_record(session: Any) -> dict:
    """Extract sourcestats fields from the current session record.

    Args:
        session: Active chrony session after processing response

    Returns:
        Dictionary with all sourcestats field values
    """
    return {
        "reference_id": _get_uinteger_field(session, "reference ID"),
        "address": _get_string_field(session, "address"),
        "samples": _get_uinteger_field(session, "samples"),
        "runs": _get_uinteger_field(session, "runs"),
        "span": _get_uinteger_field(session, "span"),
        "std_dev": _get_float_field(session, "standard deviation"),
        "resid_freq": _get_float_field(session, "residual frequency"),
        "skew": _get_float_field(session, "skew"),
        "offset": _get_float_field(session, "offset"),
        "offset_err": _get_float_field(session, "offset error"),
    }


def get_source_stats(socket_path: Optional[str] = None) -> list[SourceStats]:
    """Get statistical data for all time sources from chronyd.

    Connects to chronyd and retrieves drift rate and offset estimation
    statistics for each configured time source.

    Args:
        socket_path: Path to chronyd Unix socket. Defaults to
            '/run/chrony/chronyd.sock' or '/var/run/chrony/chronyd.sock'.

    Returns:
        list[SourceStats]: List of SourceStats objects for each source.
            Empty list if no sources are configured.

    Raises:
        ChronyLibraryError: If libchrony is not installed or cannot be loaded.
        ChronyConnectionError: If chronyd is not running or unreachable.
        ChronyPermissionError: If insufficient permissions to access chronyd.
        ChronyDataError: If statistics data is invalid or incomplete.

    Example:
        >>> from pychrony import get_source_stats
        >>> stats = get_source_stats()
        >>> for s in stats:
        ...     print(f"{s.address}: {s.samples} samples, offset {s.offset:.6f}s")
        pool.ntp.org: 8 samples, offset 0.000123s
    """
    _check_library_available()

    # Find socket path
    actual_path = _find_socket_path(socket_path)

    # Open socket connection
    fd = _lib.chrony_open_socket(actual_path.encode())
    if fd < 0:
        # Check for permission issues
        if fd == -13 or (
            os.path.exists(actual_path)
            and not os.access(actual_path, os.R_OK | os.W_OK)
        ):
            raise ChronyPermissionError(
                f"Permission denied accessing {actual_path}. "
                "Run as root or add user to chrony group.",
                error_code=fd,
            )
        raise ChronyConnectionError(
            f"Failed to connect to chronyd at {actual_path}. Is chronyd running?",
            error_code=fd,
        )

    # Initialize session
    session = _ffi.new("chrony_session **")
    try:
        err = _lib.chrony_init_session(session, fd)
        if err != 0:
            raise ChronyConnectionError(
                "Failed to initialize chrony session",
                error_code=err,
            )

        # Step 1: Request number of sourcestats records
        err = _lib.chrony_request_report_number_records(session[0], b"sourcestats")
        if err != 0:
            raise ChronyDataError(
                "Failed to request sourcestats report",
                error_code=err,
            )

        # Step 2: Process response(s) for number of records
        while _lib.chrony_needs_response(session[0]):
            err = _lib.chrony_process_response(session[0])
            if err != 0:
                raise ChronyDataError(
                    "Failed to process sourcestats response",
                    error_code=err,
                )

        # Step 3: Get number of records
        num_records = _lib.chrony_get_report_number_records(session[0])

        # Empty list if no sources (not an error)
        if num_records < 1:
            return []

        # Step 4: Iterate through all records
        stats = []
        for i in range(num_records):
            err = _lib.chrony_request_record(session[0], b"sourcestats", i)
            if err != 0:
                raise ChronyDataError(
                    f"Failed to request sourcestats record {i}",
                    error_code=err,
                )

            # Process response(s) for record data
            while _lib.chrony_needs_response(session[0]):
                err = _lib.chrony_process_response(session[0])
                if err != 0:
                    raise ChronyDataError(
                        f"Failed to process sourcestats record {i}",
                        error_code=err,
                    )

            # Extract and validate fields
            data = _get_sourcestats_from_record(session[0])
            _validate_sourcestats(data)
            stats.append(SourceStats(**data))

        return stats

    finally:
        if session[0] != _ffi.NULL:
            _lib.chrony_deinit_session(session[0])


def _validate_rtc(data: dict) -> None:
    """Validate RTC data before creating RTCData.

    Args:
        data: Dictionary of rtcdata field values

    Raises:
        ChronyDataError: If any field fails validation
    """
    # Non-negative integers
    _validate_non_negative_int(data["samples"], "samples")
    _validate_non_negative_int(data["runs"], "runs")
    _validate_non_negative_int(data["span"], "span")

    # All float fields must be finite
    for field in ["ref_time", "offset", "freq_offset"]:
        _validate_finite_float(data[field], field)

    # ref_time should be non-negative (epoch time)
    if data["ref_time"] < 0:
        raise ChronyDataError(f"ref_time must be non-negative: {data['ref_time']}")


def _get_rtc_from_record(session: Any) -> dict:
    """Extract RTC fields from the current session record.

    Args:
        session: Active chrony session after processing response

    Returns:
        Dictionary with all rtcdata field values
    """
    return {
        "ref_time": _get_timespec_field(session, "reference time"),
        "samples": _get_uinteger_field(session, "samples"),
        "runs": _get_uinteger_field(session, "runs"),
        "span": _get_uinteger_field(session, "span"),
        "offset": _get_float_field(session, "offset"),
        "freq_offset": _get_float_field(session, "frequency offset"),
    }


def get_rtc_data(socket_path: Optional[str] = None) -> RTCData:
    """Get Real-Time Clock tracking data from chronyd.

    Connects to chronyd and retrieves RTC calibration information.
    RTC tracking must be enabled in chronyd configuration.

    Args:
        socket_path: Path to chronyd Unix socket. Defaults to
            '/run/chrony/chronyd.sock' or '/var/run/chrony/chronyd.sock'.

    Returns:
        RTCData: RTC tracking information.

    Raises:
        ChronyLibraryError: If libchrony is not installed or cannot be loaded.
        ChronyConnectionError: If chronyd is not running or unreachable.
        ChronyPermissionError: If insufficient permissions to access chronyd.
        ChronyDataError: If RTC tracking is not enabled/available, or
            if RTC data is invalid.

    Example:
        >>> from pychrony import get_rtc_data
        >>> rtc = get_rtc_data()
        >>> print(f"RTC offset: {rtc.offset:.6f}s, drift: {rtc.freq_offset:.2f} ppm")
        RTC offset: 0.012345s, drift: -1.23 ppm
    """
    _check_library_available()

    # Find socket path
    actual_path = _find_socket_path(socket_path)

    # Open socket connection
    fd = _lib.chrony_open_socket(actual_path.encode())
    if fd < 0:
        # Check for permission issues
        if fd == -13 or (
            os.path.exists(actual_path)
            and not os.access(actual_path, os.R_OK | os.W_OK)
        ):
            raise ChronyPermissionError(
                f"Permission denied accessing {actual_path}. "
                "Run as root or add user to chrony group.",
                error_code=fd,
            )
        raise ChronyConnectionError(
            f"Failed to connect to chronyd at {actual_path}. Is chronyd running?",
            error_code=fd,
        )

    # Initialize session
    session = _ffi.new("chrony_session **")
    try:
        err = _lib.chrony_init_session(session, fd)
        if err != 0:
            raise ChronyConnectionError(
                "Failed to initialize chrony session",
                error_code=err,
            )

        # Step 1: Request number of rtcdata records
        err = _lib.chrony_request_report_number_records(session[0], b"rtcdata")
        if err != 0:
            raise ChronyDataError(
                "Failed to request rtcdata report",
                error_code=err,
            )

        # Step 2: Process response(s) for number of records
        while _lib.chrony_needs_response(session[0]):
            err = _lib.chrony_process_response(session[0])
            if err != 0:
                raise ChronyDataError(
                    "Failed to process rtcdata response",
                    error_code=err,
                )

        # Step 3: Get number of records
        num_records = _lib.chrony_get_report_number_records(session[0])

        # RTC not available if no records
        if num_records < 1:
            raise ChronyDataError(
                "RTC tracking is not available. Ensure RTC tracking is "
                "enabled in chronyd configuration (rtcsync or rtcfile directive)."
            )

        # Step 4: Request the first (and only) rtcdata record
        err = _lib.chrony_request_record(session[0], b"rtcdata", 0)
        if err != 0:
            raise ChronyDataError(
                "Failed to request rtcdata record",
                error_code=err,
            )

        # Step 5: Process response(s) for record data
        # Note: chrony may report 1 rtcdata record but fail to provide it
        # if RTC tracking is not actually configured. Error code 10 indicates
        # the data is not available.
        while _lib.chrony_needs_response(session[0]):
            err = _lib.chrony_process_response(session[0])
            if err != 0:
                # Treat errors during rtcdata fetch as "RTC not available"
                raise ChronyDataError(
                    "RTC tracking is not available. Ensure RTC tracking is "
                    "enabled in chronyd configuration (rtcsync or rtcfile directive)."
                )

        # Step 6: Extract and validate fields
        data = _get_rtc_from_record(session[0])
        _validate_rtc(data)

        return RTCData(**data)

    finally:
        if session[0] != _ffi.NULL:
            _lib.chrony_deinit_session(session[0])
