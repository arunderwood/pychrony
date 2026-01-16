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
from ..models import TrackingStatus, _ref_id_to_name


# Default socket paths to try (in order)
DEFAULT_SOCKET_PATHS = [
    "/run/chrony/chronyd.sock",
    "/var/run/chrony/chronyd.sock",
]

# Conversion constants
NANOSECONDS_PER_SECOND = 1e9

# Try to import compiled CFFI bindings
_lib = None
_ffi = None

try:
    from pychrony._core._cffi_bindings import lib as _lib, ffi as _ffi

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

    # Leap status bounds
    if not 0 <= data["leap_status"] <= 3:
        raise ChronyDataError(f"Invalid leap_status: {data['leap_status']}")

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

    return {
        "reference_id": ref_id,
        "reference_id_name": _ref_id_to_name(ref_id),
        "reference_ip": _get_string_field(session, "address"),
        "stratum": _get_uinteger_field(session, "stratum"),
        "leap_status": _get_uinteger_field(session, "leap status"),
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
