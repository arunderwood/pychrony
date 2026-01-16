# Data Model: Chrony Tracking Binding

**Feature**: 002-tracking-binding
**Date**: 2026-01-15
**Status**: Complete

## Entity Overview

This feature defines three primary entities:
1. **TrackingStatus** - Core data structure for tracking information
2. **Exception Hierarchy** - Error handling types
3. **ChronyClient** - Connection management (internal)

## Entity: TrackingStatus

**Purpose**: Pythonic representation of chrony tracking data retrieved via libchrony's high-level API

**Module**: `src/pychrony/models.py`

### Fields

| Field | Type | Description | Validation | Source (libchrony field name) |
|-------|------|-------------|------------|-------------------------------|
| reference_id | int | NTP reference source identifier (uint32) | Non-zero when synchronized | chrony_get_field_uinteger("reference id") |
| reference_id_name | str | Human-readable reference name | Non-empty | Derived from reference_id |
| reference_ip | str | IP address of reference source | Valid IP or ID | chrony_get_field_string("ip address") |
| stratum | int | NTP hierarchy level | 0-15 inclusive | chrony_get_field_uinteger("stratum") |
| leap_status | int | Leap second indicator | 0-3 inclusive | chrony_get_field_uinteger("leap status") |
| ref_time | float | Last measurement timestamp (epoch seconds) | Not NaN/Inf | chrony_get_field_timespec("reference time") |
| offset | float | Current time offset from reference (seconds) | Not NaN/Inf | chrony_get_field_float("current correction") |
| last_offset | float | Offset at last measurement (seconds) | Not NaN/Inf | chrony_get_field_float("last offset") |
| rms_offset | float | RMS of recent offsets (seconds) | >= 0, not NaN/Inf | chrony_get_field_float("rms offset") |
| frequency | float | Clock frequency error (ppm) | Not NaN/Inf | chrony_get_field_float("frequency") |
| residual_freq | float | Residual frequency for source (ppm) | Not NaN/Inf | chrony_get_field_float("residual frequency") |
| skew | float | Estimated frequency error (ppm) | >= 0, not NaN/Inf | chrony_get_field_float("skew") |
| root_delay | float | Network path delay to stratum-1 (seconds) | >= 0, not NaN/Inf | chrony_get_field_float("root delay") |
| root_dispersion | float | Total dispersion to reference (seconds) | >= 0, not NaN/Inf | chrony_get_field_float("root dispersion") |
| update_interval | float | Time since last update (seconds) | >= 0, not NaN/Inf | chrony_get_field_float("last update interval") |

### Python Definition

```python
from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class TrackingStatus:
    """Chrony tracking status information.

    Represents the current time synchronization state from chronyd,
    including offset, frequency, and accuracy metrics.

    Attributes:
        reference_id: NTP reference identifier (uint32 as hex IP or name)
        reference_id_name: Human-readable reference source name
        reference_ip: IP address of reference source (IPv4, IPv6, or ID#)
        stratum: NTP stratum level (0=reference clock, 1-15=downstream)
        leap_status: Leap second status (0=normal, 1=insert, 2=delete, 3=unsync)
        ref_time: Timestamp of last measurement (seconds since epoch)
        offset: Current offset from reference in seconds (can be negative)
        last_offset: Offset at last measurement in seconds
        rms_offset: Root mean square of recent offsets in seconds
        frequency: Clock frequency error in parts per million
        residual_freq: Residual frequency for current source in ppm
        skew: Estimated error bound on frequency in ppm
        root_delay: Total roundtrip delay to stratum-1 source in seconds
        root_dispersion: Total dispersion to reference in seconds
        update_interval: Seconds since last successful update
    """
    reference_id: int
    reference_id_name: str
    reference_ip: str
    stratum: int
    leap_status: int
    ref_time: float
    offset: float
    last_offset: float
    rms_offset: float
    frequency: float
    residual_freq: float
    skew: float
    root_delay: float
    root_dispersion: float
    update_interval: float

    def is_synchronized(self) -> bool:
        """Check if chronyd is synchronized to a source."""
        return self.reference_id != 0 and self.stratum < 16

    def is_leap_pending(self) -> bool:
        """Check if a leap second adjustment is pending."""
        return self.leap_status in (1, 2)
```

### Relationships

- TrackingStatus is created by `get_tracking()` function
- TrackingStatus has no external entity relationships (standalone data transfer object)

### State Transitions

TrackingStatus is immutable (frozen dataclass). No state transitions.

## Entity: Exception Hierarchy

**Purpose**: Typed exceptions for chrony-specific error conditions

**Module**: `src/pychrony/exceptions.py`

### Exception Types

| Exception | Parent | Error Code | When Raised |
|-----------|--------|------------|-------------|
| ChronyError | Exception | Optional[int] | Base class for all chrony errors |
| ChronyConnectionError | ChronyError | int | chronyd socket unreachable, session init failed |
| ChronyPermissionError | ChronyError | int | Insufficient permissions for socket |
| ChronyDataError | ChronyError | int | Missing fields, invalid responses, field index < 0 |
| ChronyLibraryError | ChronyError | None | libchrony not installed |

### Python Definition

```python
from typing import Optional

class ChronyError(Exception):
    """Base exception for all chrony-related errors.

    Attributes:
        message: Human-readable error description
        error_code: Optional numeric error code from libchrony
    """
    def __init__(self, message: str, error_code: Optional[int] = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code

    def __str__(self) -> str:
        if self.error_code is not None:
            return f"{self.message} (error code: {self.error_code})"
        return self.message


class ChronyConnectionError(ChronyError):
    """Raised when connection to chronyd fails.

    Common causes:
    - chronyd is not running
    - Socket path does not exist
    - chrony_open_socket() returns < 0
    - chrony_init_session() returns error
    """
    pass


class ChronyPermissionError(ChronyError):
    """Raised when access to chronyd is denied.

    Common causes:
    - User not in chrony group
    - Running as unprivileged user
    - SELinux/AppArmor restrictions
    """
    pass


class ChronyDataError(ChronyError):
    """Raised when tracking data is invalid or incomplete.

    Common causes:
    - chrony_get_field_index() returns < 0 (field not found)
    - chrony_process_response() returns error
    - Field validation fails (NaN, out of range)
    - Protocol version mismatch
    """
    pass


class ChronyLibraryError(ChronyError):
    """Raised when libchrony is not available.

    Common causes:
    - libchrony not installed at runtime
    - CFFI bindings not compiled (missing libchrony-devel at build time)
    - Library version incompatible
    """
    def __init__(self, message: str):
        super().__init__(message, error_code=None)
```

## Entity: ChronyClient (Internal)

**Purpose**: Internal session manager for libchrony high-level API (not part of public API)

**Module**: `src/pychrony/_core/_bindings.py`

### Internal Structure

```python
class _ChronyClient:
    """Internal libchrony session manager.

    Not part of public API. Use get_tracking() function instead.

    Creates a new session per request (stateless pattern).
    Uses libchrony's high-level introspection API.
    """
    _ffi: FFI
    _lib: Any
    _socket_path: str

    def get_tracking(self) -> TrackingStatus:
        """Get tracking status using session-per-call pattern."""
        ...

    def _get_float_field(self, session, name: str) -> float:
        """Get float field by name, raise ChronyDataError if not found."""
        ...

    def _get_uinteger_field(self, session, name: str) -> int:
        """Get unsigned integer field by name."""
        ...

    def _get_timespec_field(self, session, name: str) -> float:
        """Get timespec field by name, convert to epoch float."""
        ...

    def _get_string_field(self, session, name: str) -> str:
        """Get string field by name."""
        ...
```

### Session Lifecycle (per get_tracking() call)

```
chrony_open_socket() → chrony_init_session() → chrony_request_report_number_records("tracking")
    → chrony_process_response() → chrony_get_field_*() for each field → chrony_deinit_session()
```

Each `get_tracking()` call creates and destroys its own session (stateless).

## Validation Rules

### TrackingStatus Validation

Applied during construction from libchrony data:

```python
def _validate_tracking(data: dict) -> None:
    """Validate tracking data before creating TrackingStatus."""
    # Stratum bounds
    if not 0 <= data['stratum'] <= 15:
        raise ChronyDataError(f"Invalid stratum: {data['stratum']}")

    # Leap status bounds
    if not 0 <= data['leap_status'] <= 3:
        raise ChronyDataError(f"Invalid leap_status: {data['leap_status']}")

    # Float validity
    import math
    float_fields = ['ref_time', 'offset', 'last_offset', 'rms_offset', 'frequency',
                    'residual_freq', 'skew', 'root_delay', 'root_dispersion',
                    'update_interval']
    for field in float_fields:
        if math.isnan(data[field]) or math.isinf(data[field]):
            raise ChronyDataError(f"Invalid {field}: {data[field]}")

    # Non-negative fields
    non_negative = ['ref_time', 'rms_offset', 'skew', 'root_delay', 'root_dispersion',
                    'update_interval']
    for field in non_negative:
        if data[field] < 0:
            raise ChronyDataError(f"{field} must be non-negative: {data[field]}")
```

## Type Mappings

### libchrony High-Level API → Python Types

libchrony's high-level API returns native C types that map directly to Python:

| libchrony Function | Returns | Python Type | Notes |
|--------------------|---------|-------------|-------|
| chrony_get_field_uinteger() | uint64_t | int | Direct mapping |
| chrony_get_field_integer() | int64_t | int | Direct mapping |
| chrony_get_field_float() | double | float | Direct mapping |
| chrony_get_field_string() | const char* | str | Decode as UTF-8 |
| chrony_get_field_timespec() | struct timespec | float | Convert: tv_sec + tv_nsec/1e9 |

**No custom conversion utilities needed** - libchrony handles all wire-format conversions internally.

### Timespec to Float Conversion

The only conversion needed is `struct timespec` to Python float (epoch seconds):

```python
def _timespec_to_float(ts) -> float:
    """Convert struct timespec to Python float (seconds since epoch)."""
    return ts.tv_sec + ts.tv_nsec / 1e9
```

### Reference ID Format

The reference_id (ref_id) is a 32-bit value interpreted as:
- For IP addresses: Network byte order IP (e.g., 0x7f000001 = 127.0.0.1)
- For reference clocks: ASCII characters (e.g., 0x47505300 = "GPS\0")

Conversion to human-readable name:
```python
def _ref_id_to_name(ref_id: int) -> str:
    """Convert reference ID to human-readable name."""
    # Check if it looks like ASCII (all bytes printable or null)
    bytes_val = ref_id.to_bytes(4, 'big')
    if all(b == 0 or 32 <= b < 127 for b in bytes_val):
        return bytes_val.rstrip(b'\x00').decode('ascii', errors='replace')
    # Otherwise format as IP address
    return '.'.join(str(b) for b in bytes_val)
```
