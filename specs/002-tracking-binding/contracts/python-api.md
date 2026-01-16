# Python API Contract: Chrony Tracking Binding

**Feature**: 002-tracking-binding
**Version**: 1.0.0
**Date**: 2026-01-15

## Public API Surface

This document defines the stable public API for pychrony tracking functionality.

## Module: pychrony

### Exported Names

```python
__all__ = [
    # Core function
    'get_tracking',

    # Data model
    'TrackingStatus',

    # Exceptions
    'ChronyError',
    'ChronyConnectionError',
    'ChronyPermissionError',
    'ChronyDataError',
    'ChronyLibraryError',
]
```

## Function: get_tracking

### Signature

```python
def get_tracking(
    socket_path: str | None = None,
) -> TrackingStatus:
    """Retrieve current chrony tracking status.

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
    ...
```

### Behavior Contract

| Precondition | Postcondition |
|--------------|---------------|
| libchrony installed | Returns TrackingStatus or raises ChronyLibraryError |
| chronyd running | Returns TrackingStatus or raises ChronyConnectionError |
| Socket accessible | Returns TrackingStatus or raises ChronyPermissionError |
| Valid response | Returns TrackingStatus or raises ChronyDataError |

### Default Socket Paths

Checked in order:
1. User-provided `socket_path` (if specified)
2. `/run/chrony/chronyd.sock`
3. `/var/run/chrony/chronyd.sock`

## Class: TrackingStatus

### Signature

```python
@dataclass(frozen=True)
class TrackingStatus:
    reference_id: int
    reference_id_name: str
    stratum: int
    leap_status: int
    offset: float
    last_offset: float
    rms_offset: float
    frequency: float
    residual_freq: float
    skew: float
    root_delay: float
    root_dispersion: float
    update_interval: float

    def is_synchronized(self) -> bool: ...
    def is_leap_pending(self) -> bool: ...
```

### Field Contracts

| Field | Type | Unit | Range | Description |
|-------|------|------|-------|-------------|
| reference_id | int | - | 0-2^32 | NTP reference identifier |
| reference_id_name | str | - | - | Human-readable source name |
| stratum | int | - | 0-15 | NTP stratum level |
| leap_status | int | - | 0-3 | Leap second indicator |
| offset | float | seconds | - | Time offset from reference |
| last_offset | float | seconds | - | Previous measurement offset |
| rms_offset | float | seconds | >= 0 | RMS of recent offsets |
| frequency | float | ppm | - | Clock frequency error |
| residual_freq | float | ppm | - | Residual frequency |
| skew | float | ppm | >= 0 | Frequency error bound |
| root_delay | float | seconds | >= 0 | Path delay to stratum-1 |
| root_dispersion | float | seconds | >= 0 | Total dispersion |
| update_interval | float | seconds | >= 0 | Time since last update |

### Method Contracts

#### is_synchronized

```python
def is_synchronized(self) -> bool:
    """Check if chronyd is synchronized to a time source.

    Returns:
        True if synchronized (reference_id != 0 and stratum < 16),
        False otherwise.
    """
```

#### is_leap_pending

```python
def is_leap_pending(self) -> bool:
    """Check if a leap second adjustment is pending.

    Returns:
        True if leap_status is 1 (insert) or 2 (delete),
        False otherwise.
    """
```

## Exception Classes

### ChronyError (Base)

```python
class ChronyError(Exception):
    message: str
    error_code: int | None

    def __init__(self, message: str, error_code: int | None = None): ...
    def __str__(self) -> str: ...
```

### ChronyConnectionError

```python
class ChronyConnectionError(ChronyError):
    """chronyd is not running or socket unreachable."""
```

### ChronyPermissionError

```python
class ChronyPermissionError(ChronyError):
    """Insufficient permissions to access chronyd socket."""
```

### ChronyDataError

```python
class ChronyDataError(ChronyError):
    """Tracking data is invalid, incomplete, or corrupted."""
```

### ChronyLibraryError

```python
class ChronyLibraryError(ChronyError):
    """libchrony is not installed or cannot be loaded."""

    def __init__(self, message: str): ...  # error_code always None
```

## Error Code Mapping

| Error Code | Exception Type | Description |
|------------|----------------|-------------|
| -1 | ChronyConnectionError | Connection refused |
| -2 | ChronyConnectionError | Socket not found |
| -3 | ChronyPermissionError | Permission denied |
| -4 | ChronyDataError | Invalid response |
| -5 | ChronyDataError | Incomplete data |
| None | ChronyLibraryError | Library not found |

## Usage Examples

### Basic Usage

```python
from pychrony import get_tracking, ChronyError

try:
    status = get_tracking()
    print(f"Stratum: {status.stratum}")
    print(f"Offset: {status.offset:.9f} seconds")
    print(f"Frequency: {status.frequency:.3f} ppm")
    print(f"Reference: {status.reference_id_name}")
except ChronyError as e:
    print(f"Error: {e}")
```

### Custom Socket Path

```python
from pychrony import get_tracking

status = get_tracking(socket_path="/custom/path/chronyd.sock")
```

### Error Handling

```python
from pychrony import (
    get_tracking,
    ChronyConnectionError,
    ChronyPermissionError,
    ChronyLibraryError,
)

try:
    status = get_tracking()
except ChronyLibraryError:
    print("Install libchrony: apt-get install libchrony-dev")
except ChronyConnectionError:
    print("chronyd is not running: systemctl start chronyd")
except ChronyPermissionError:
    print("Run as root or add user to chrony group")
```

### Sync Status Check

```python
from pychrony import get_tracking

status = get_tracking()
if status.is_synchronized():
    print(f"Synced to {status.reference_id_name} (stratum {status.stratum})")
else:
    print("Not synchronized to any time source")

if status.is_leap_pending():
    print("Warning: Leap second adjustment pending")
```

## Compatibility Guarantees

### Semantic Versioning

- **MAJOR**: Breaking changes to public API
- **MINOR**: New features, backward compatible
- **PATCH**: Bug fixes only

### Stability Promises

1. All names in `__all__` are stable
2. TrackingStatus fields will not be removed
3. Exception hierarchy will not change
4. Method signatures will remain compatible

### Deprecated Features

None currently.

## Testing Contract

Contract tests verify:
1. All exported names are importable
2. get_tracking returns TrackingStatus or raises ChronyError
3. TrackingStatus fields have correct types
4. Exception hierarchy is correct
5. Methods return expected types
