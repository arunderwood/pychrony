"""CFFI bindings to libchrony system library.

This module contains the ChronyConnection context manager for connecting
to chronyd and retrieving time synchronization status.

Internal implementation - use pychrony.ChronyConnection instead.
"""

import math
import os
from types import TracebackType
from typing import Any, NoReturn

from ..exceptions import (
    ChronyConnectionError,
    ChronyDataError,
    ChronyLibraryError,
    ChronyPermissionError,
)
from ..models import (
    LeapStatus,
    RTCData,
    Source,
    SourceMode,
    SourceState,
    SourceStats,
    TrackingStatus,
    Transport,
    _ref_id_to_name,
)

# Default Unix socket paths tried during auto-detect, in order. chrony's
# compiled-in default is documented as both /run/chrony/chronyd.sock and
# /var/run/chrony/chronyd.sock depending on release, and the two are the same
# file wherever /var/run is a symlink to /run, so both are tried.
DEFAULT_SOCKET_PATHS = [
    "/run/chrony/chronyd.sock",
    "/var/run/chrony/chronyd.sock",
]

# Localhost command-port addresses tried after the Unix sockets. chronyd binds
# the command port to 127.0.0.1 and ::1 by default (bindcmdaddress) on port 323
# (cmdport), and accepts monitoring commands only from localhost by default
# (cmdallow). "cmdport 0" disables it; that does not disable the Unix socket.
#
# This chain mirrors chronyc's own documented behaviour: it tries the Unix
# socket first and, if that fails because it is not running as root, falls back
# to 127.0.0.1 and then ::1.
DEFAULT_COMMAND_PORTS = [
    "127.0.0.1:323",
    "[::1]:323",
]

# Conversion constants
NANOSECONDS_PER_SECOND = 1e9

# chrony_err values for a failed send()/recv() on the socket, from the
# chrony_err enum in libchrony's chrony.h. The CFFI cdef types chrony_err as a
# plain int, so the enumerators are not exposed and their values are mirrored
# here. Both mean chronyd could not be reached, not that its data was bad.
CHRONY_SEND_FAILED = 5
CHRONY_RECV_FAILED = 6

TRANSPORT_ERRORS = frozenset({CHRONY_SEND_FAILED, CHRONY_RECV_FAILED})

# Try to import compiled CFFI bindings
# These are generated at build time by CFFI, so they may not exist
_lib: Any = None
_ffi: Any = None

try:
    from pychrony._core._cffi_bindings import (  # type: ignore[import-not-found]
        ffi as _ffi,
    )
    from pychrony._core._cffi_bindings import (  # type: ignore[import-not-found]
        lib as _lib,
    )

    _LIBRARY_AVAILABLE = True
except ImportError:
    _LIBRARY_AVAILABLE = False


def _is_unix_socket_address(address: str) -> bool:
    """Return True if an address names a Unix socket path.

    Mirrors libchrony's own rule: a leading slash means a Unix socket,
    anything else is parsed as an IP address with an optional port.
    """
    return address.startswith("/")


def _is_permission_denied(address: str) -> bool:
    """Return True if a failed connect to `address` was a permissions problem.

    Only meaningful for Unix sockets. Note the check is deliberately not used
    to decide *whether* to attempt a connection: `os.path.exists` also reports
    False when the socket's parent directory is not traversable, which says
    nothing about whether chronyd is reachable.
    """
    return (
        _is_unix_socket_address(address)
        and os.path.exists(address)
        and not os.access(address, os.R_OK | os.W_OK)
    )


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
            - ``None``: Auto-detect. Each candidate is tried by actually
              attempting the connection, in order: the default Unix socket
              paths, then the localhost command port (IPv4, then IPv6).
              The first candidate that connects wins; use `address` and
              `transport` to find out which one that was.

    Methods:
        get_tracking: Get current NTP tracking status (returns `TrackingStatus`).
        get_sources: Get configured time sources (returns ``list[Source]``).
        get_source_stats: Get source statistics (returns ``list[SourceStats]``).
        get_rtc_data: Get RTC tracking data (returns `RTCData` or ``None``).

    Choosing a transport:
        chronyd's Unix socket is its control channel and is accessible locally
        by the root or chrony user only; its command port is limited to
        monitoring commands. Every report this class reads is in the monitoring
        set, so a read-only consumer should prefer the command port and can
        assert on `transport` to be sure of what it holds.

    Thread Safety:
        NOT thread-safe. Each thread needs its own connection.

    See Also:
        `Transport`: Which transport a connection resolved to.
        `TrackingStatus`: Tracking data model.
        `Source`: Time source data model.
        `SourceStats`: Source statistics data model.
        `RTCData`: RTC tracking data model.

        chronyc man page (access methods and the monitoring command set):
        https://chrony-project.org/doc/4.9/chronyc.html

    Examples:
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
        self._resolved_address: str | None = None
        self._denied_socket: str | None = None
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

    @property
    def address(self) -> str | None:
        """Address this connection is actually using, or None if not connected.

        For an explicit address this is that address. For auto-detect it is
        whichever candidate connected, so callers can tell a Unix socket from
        the localhost command port. Cleared when the connection closes.
        """
        return self._resolved_address

    @property
    def transport(self) -> Transport | None:
        """Transport in use, or None if not connected.

        The two transports differ in privilege: `Transport.UNIX_SOCKET` is
        chronyd's control channel, while over `Transport.COMMAND_PORT` chronyd
        serves monitoring commands only. A caller that must not hold a control
        channel can assert on this.
        """
        if self._resolved_address is None:
            return None
        return (
            Transport.UNIX_SOCKET
            if _is_unix_socket_address(self._resolved_address)
            else Transport.COMMAND_PORT
        )

    def _candidate_addresses(self) -> list[str]:
        """Return the addresses to try, in order.

        An explicit address is used as given, with no fallback: asking for a
        specific transport should not silently land on a different one. Only
        auto-detect walks the candidate chain.
        """
        if self._address is not None:
            return [self._address]
        return [*DEFAULT_SOCKET_PATHS, *DEFAULT_COMMAND_PORTS]

    def _open(self) -> None:
        """Open socket connection and initialize session.

        Candidates are tried by attempting the connection, not by probing the
        filesystem: a socket path can exist and still refuse connections (a
        Unix socket needs write permission), and a path can be unstattable
        while chronyd is perfectly reachable. Only a real connection attempt
        distinguishes those.

        Raises:
            ChronyConnectionError: If no candidate could be connected to
            ChronyPermissionError: If a Unix socket was rejected on permissions
        """
        candidates = self._candidate_addresses()
        last_error_code = -1
        denied_address: str | None = None

        for address in candidates:
            fd = _lib.chrony_open_socket(address.encode())
            if fd >= 0:
                self._fd = fd
                self._resolved_address = address
                break
            last_error_code = fd
            if denied_address is None and _is_permission_denied(address):
                denied_address = address
        else:
            self._raise_open_error(candidates, denied_address, last_error_code)

        # Remembered for diagnostics: a command-port connection reached after a
        # Unix socket refused us explains later "chronyd never answered" errors.
        self._denied_socket = denied_address

        # Initialize session
        self._session_ptr = _ffi.new("chrony_session **")
        err = _lib.chrony_init_session(self._session_ptr, self._fd)
        if err != 0:
            # Clean up socket on failure
            _lib.chrony_close_socket(self._fd)
            self._fd = None
            self._resolved_address = None
            raise ChronyConnectionError(
                "Failed to initialize chrony session",
                error_code=err,
            )

        self._session = self._session_ptr[0]

    def _raise_open_error(
        self,
        candidates: list[str],
        denied_address: str | None,
        error_code: int,
    ) -> None:
        """Raise the most specific error for a failed set of connect attempts.

        Args:
            candidates: Addresses that were tried, in order
            denied_address: First candidate rejected on permissions, if any
            error_code: Error code from the last failed attempt

        Raises:
            ChronyPermissionError: If a Unix socket was rejected on permissions
            ChronyConnectionError: Otherwise
        """
        if denied_address is not None:
            raise ChronyPermissionError(
                f"Permission denied connecting to {denied_address}. This is "
                "chronyd's control socket, accessible only to the root or "
                "chrony user; joining chrony's group does not help, because "
                "the socket is not group-writable. For read-only monitoring "
                'use the command port instead - ChronyConnection("127.0.0.1") '
                "- which serves every report this library reads. chronyd binds "
                'it to localhost by default; "cmdport 0" disables it. See '
                "https://chrony-project.org/doc/4.9/chronyc.html",
                error_code=error_code,
            )

        if self._address is not None:
            raise ChronyConnectionError(
                f"Failed to connect to {self._address}. Is chronyd running?",
                error_code=error_code,
            )

        raise ChronyConnectionError(
            "Failed to connect to chronyd (auto-detect). Tried: "
            f"{', '.join(candidates)}. Is chronyd running? If it is, its Unix "
            "socket may be unreachable for this user and its command port "
            'disabled ("cmdport 0").',
            error_code=error_code,
        )

    def _close(self) -> None:
        """Close session and socket connection."""
        if self._session is not None and self._session != _ffi.NULL:
            _lib.chrony_deinit_session(self._session)
            self._session = None

        if self._fd is not None and self._fd >= 0:
            _lib.chrony_close_socket(self._fd)
            self._fd = None

        self._session_ptr = None
        self._resolved_address = None
        self._denied_socket = None

    def _ensure_context(self) -> None:
        """Ensure we're within a context manager.

        Raises:
            RuntimeError: If called outside context manager
        """
        if not self._in_context:
            raise RuntimeError(
                "ChronyConnection methods must be called within a 'with' block"
            )

    def _raise_request_error(self, description: str, err: int) -> NoReturn:
        """Raise the appropriate error for a failed request or response.

        `CHRONY_SEND_FAILED` and `CHRONY_RECV_FAILED` are returned when the
        underlying `send()` or `recv()` fails, so they mean chronyd could not be
        reached - a connection problem, not a data problem. They are reported as
        `ChronyConnectionError` so that callers handling "chronyd unreachable"
        catch them. Every other `chrony_err` concerns the report itself and is
        reported as `ChronyDataError`.

        This matters most on the command port: it is UDP, so the socket opens
        whether or not chronyd is listening, and a dead command port only shows
        up here.

        Args:
            description: What was being attempted, e.g. "Failed to process
                tracking response"
            err: chrony_err value from the failed call

        Raises:
            ChronyConnectionError: If the send or receive itself failed
            ChronyDataError: For any other failure
        """
        if err not in TRANSPORT_ERRORS:
            raise ChronyDataError(description, error_code=err)

        message = f"{description}: chronyd did not respond on {self._resolved_address}."
        if self.transport is Transport.COMMAND_PORT:
            message += (
                " The command port is UDP, so the connection opens even when "
                'chronyd is not listening. It may be disabled ("cmdport 0"), '
                "bound to another address (bindcmdaddress), or blocked."
            )
            if self._denied_socket is not None:
                message += (
                    f" Auto-detect used it because {self._denied_socket} "
                    "refused the connection."
                )
        raise ChronyConnectionError(message, error_code=err)

    def _request_report(self, report_name: bytes) -> int:
        """Request number of records for a report type.

        Args:
            report_name: Report name (e.g., b"tracking", b"sources")

        Returns:
            Number of records available

        Raises:
            ChronyConnectionError: If chronyd could not be reached
            ChronyDataError: If the report itself could not be retrieved
        """
        err = _lib.chrony_request_report_number_records(self._session, report_name)
        if err != 0:
            self._raise_request_error(
                f"Failed to request {report_name.decode()} report", err
            )

        while _lib.chrony_needs_response(self._session):
            err = _lib.chrony_process_response(self._session)
            if err != 0:
                self._raise_request_error(
                    f"Failed to process {report_name.decode()} response", err
                )

        return _lib.chrony_get_report_number_records(self._session)

    def _request_record(self, report_name: bytes, index: int) -> None:
        """Request a specific record from a report.

        Args:
            report_name: Report name (e.g., b"tracking", b"sources")
            index: Record index

        Raises:
            ChronyConnectionError: If chronyd could not be reached
            ChronyDataError: If the record itself could not be retrieved
        """
        err = _lib.chrony_request_record(self._session, report_name, index)
        if err != 0:
            self._raise_request_error(
                f"Failed to request {report_name.decode()} record {index}", err
            )

        while _lib.chrony_needs_response(self._session):
            err = _lib.chrony_process_response(self._session)
            if err != 0:
                self._raise_request_error(
                    f"Failed to process {report_name.decode()} record {index}", err
                )

    def get_tracking(self) -> TrackingStatus:
        """Get current tracking status from chronyd.

        Returns:
            TrackingStatus: Current tracking information from chronyd.

        Raises:
            RuntimeError: If called outside context manager
            ChronyConnectionError: If chronyd did not respond.
            ChronyDataError: If tracking data is invalid or incomplete.

        Examples:
            >>> with ChronyConnection() as conn:
            ...     status = conn.get_tracking()
            ...     print(f"Offset: {status.offset:.6f} seconds")
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
            ChronyConnectionError: If chronyd did not respond.
            ChronyDataError: If source data is invalid or incomplete.

        Examples:
            >>> with ChronyConnection() as conn:
            ...     sources = conn.get_sources()
            ...     for src in sources:
            ...         print(f"{src.address}: stratum {src.stratum}")
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
            ChronyConnectionError: If chronyd did not respond.
            ChronyDataError: If statistics data is invalid or incomplete.

        Examples:
            >>> with ChronyConnection() as conn:
            ...     stats = conn.get_source_stats()
            ...     for s in stats:
            ...         print(f"{s.address}: {s.samples} samples")
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
            ChronyConnectionError: If chronyd did not respond.
            ChronyDataError: If RTC data is invalid or malformed.

        Examples:
            >>> with ChronyConnection() as conn:
            ...     rtc = conn.get_rtc_data()
            ...     if rtc:
            ...         print(f"RTC offset: {rtc.offset:.6f}s")
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
        # Deliberately broad: this is a C-library boundary, and an absent RTC is a
        # supported outcome reported as None rather than an error. Narrowing the
        # catch risks surfacing a CFFI failure as a crash for that normal case.
        except Exception:  # noqa: BLE001
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
