# Python API Contract: Multiple Reports Bindings

**Branch**: `003-multiple-reports-bindings` | **Date**: 2026-01-16

## Overview

This document defines the public Python API contract for the new report functions. All functions follow the established `get_tracking()` pattern and are exported from the `pychrony` package.

## Public API

### Module Exports

```python
# pychrony/__init__.py
__all__ = [
    # Existing exports
    "get_tracking",
    "TrackingStatus",
    "ChronyError",
    "ChronyConnectionError",
    "ChronyPermissionError",
    "ChronyDataError",
    "ChronyLibraryError",
    # New exports (this feature)
    "get_sources",
    "get_source_stats",
    "get_rtc_data",
    "Source",
    "SourceStats",
    "RTCData",
]
```

## Function Signatures

### get_sources

```python
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
```

### get_source_stats

```python
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
        ...     print(f"{s.address}: {s.n_samples} samples, offset {s.offset:.6f}s")
        pool.ntp.org: 8 samples, offset 0.000123s
    """
```

### get_rtc_data

```python
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
        >>> print(f"RTC offset: {rtc.offset:.6f}s, drift: {rtc.frequency:.2f} ppm")
        RTC offset: 0.012345s, drift: -1.23 ppm
    """
```

## Data Classes

### Source

```python
@dataclass(frozen=True)
class Source:
    address: str          # IP address or reference ID
    mode: int             # 0=unspecified, 1=server, 2=peer, 3=refclock
    state: int            # 0-6, see state_name property
    stratum: int          # 0-15, NTP stratum level
    poll: int             # log2 of polling interval in seconds
    reach: int            # 0-255, reachability register (octal 377 = full)
    last_sample_ago: float  # seconds since last sample
    offset: float         # offset in seconds
    offset_err: float     # offset error bound in seconds

    def is_reachable(self) -> bool: ...
    def is_selected(self) -> bool: ...
    @property
    def mode_name(self) -> str: ...
    @property
    def state_name(self) -> str: ...
```

### SourceStats

```python
@dataclass(frozen=True)
class SourceStats:
    address: str          # IP address or reference ID
    n_samples: int        # number of sample points
    n_runs: int           # number of same-sign residual runs
    span: float           # sample span in seconds
    frequency: float      # residual frequency in ppm
    freq_skew: float      # frequency error bound in ppm
    offset: float         # estimated offset in seconds
    std_dev: float        # sample standard deviation in seconds

    def has_sufficient_samples(self, minimum: int = 4) -> bool: ...
```

### RTCData

```python
@dataclass(frozen=True)
class RTCData:
    ref_time: float       # last RTC measurement time (epoch seconds)
    n_samples: int        # calibration sample count
    n_runs: int           # same-sign residual runs
    span: float           # sample span in seconds
    offset: float         # RTC offset (fast by) in seconds
    frequency: float      # RTC drift rate in ppm

    def is_calibrated(self) -> bool: ...
```

## Error Conditions

| Scenario | Exception | Message Pattern |
|----------|-----------|-----------------|
| libchrony not installed | `ChronyLibraryError` | "libchrony bindings not available..." |
| Socket not found | `ChronyConnectionError` | "chronyd socket not found. Tried: ..." |
| Permission denied | `ChronyPermissionError` | "Permission denied accessing {path}..." |
| Connection failed | `ChronyConnectionError` | "Failed to connect to chronyd at {path}..." |
| Session init failed | `ChronyConnectionError` | "Failed to initialize chrony session" |
| Report request failed | `ChronyDataError` | "Failed to request {report} report" |
| Response processing failed | `ChronyDataError` | "Failed to process {report} response" |
| RTC not available | `ChronyDataError` | "RTC tracking is not available..." |
| Invalid field value | `ChronyDataError` | "Invalid {field}: {value}" |

## Behavioral Contract

1. **Thread Safety**: Functions are not thread-safe. Each call opens a new socket connection.

2. **Connection Lifecycle**: Each function call opens a connection, retrieves data, and closes the connection. No persistent connections.

3. **Empty Results**: `get_sources()` and `get_source_stats()` return empty lists if no sources configured. They do NOT raise an exception.

4. **RTC Unavailable**: `get_rtc_data()` raises `ChronyDataError` if RTC tracking is not enabled (per spec clarification).

5. **Independent Snapshots**: Each function returns data as of call time. No atomicity across multiple calls.

6. **Immutability**: All returned dataclasses are frozen (immutable).

7. **Socket Path Resolution**: If socket_path is None, tries `/run/chrony/chronyd.sock` then `/var/run/chrony/chronyd.sock`.

## Versioning

- These functions are added in pychrony version TBD
- API follows semantic versioning: additions are minor version bumps
- Breaking changes (if any) would be major version bumps
