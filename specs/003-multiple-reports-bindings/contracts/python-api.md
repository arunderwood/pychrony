# Python API Contract: Multiple Reports Bindings

**Branch**: `003-multiple-reports-bindings` | **Date**: 2026-01-16
**Verified against**: libchrony source (client.c from gitlab.com/chrony/libchrony)

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
        >>> print(f"RTC offset: {rtc.offset:.6f}s, drift: {rtc.freq_offset:.2f} ppm")
        RTC offset: 0.012345s, drift: -1.23 ppm
    """
```

## Data Classes (Verified from libchrony source)

### Source

```python
@dataclass(frozen=True)
class Source:
    address: str           # IP address or reference ID (from "address" or "reference ID")
    poll: int              # log2 of polling interval in seconds (TYPE_INT16)
    stratum: int           # 0-15, NTP stratum level (TYPE_UINT16)
    state: int             # 0-5, see state_name property (TYPE_UINT16 enum)
    mode: int              # 0=client, 1=peer, 2=reference clock (TYPE_UINT16 enum)
    flags: int             # source flags bitfield (TYPE_UINT16)
    reachability: int      # 0-255, reachability register (TYPE_UINT16)
    last_sample_ago: int   # seconds since last sample (TYPE_UINT32)
    orig_latest_meas: float  # original last sample offset (TYPE_FLOAT)
    latest_meas: float     # adjusted last sample offset (TYPE_FLOAT)
    latest_meas_err: float # last sample error bound (TYPE_FLOAT)

    def is_reachable(self) -> bool: ...
    def is_selected(self) -> bool: ...  # Returns state == 0
    @property
    def mode_name(self) -> str: ...
    @property
    def state_name(self) -> str: ...
```

**State values** (from `sources_state_enums[]`):
- 0: selected
- 1: nonselectable
- 2: falseticker
- 3: jittery
- 4: unselected
- 5: selectable

**Mode values** (from `sources_mode_enums[]`):
- 0: client
- 1: peer
- 2: reference clock

### SourceStats

```python
@dataclass(frozen=True)
class SourceStats:
    reference_id: int      # NTP reference identifier (TYPE_UINT32)
    address: str           # IP address (empty for refclocks) (TYPE_ADDRESS)
    samples: int           # number of sample points (TYPE_UINT32)
    runs: int              # number of same-sign residual runs (TYPE_UINT32)
    span: int              # sample span in seconds (TYPE_UINT32)
    std_dev: float         # sample standard deviation in seconds (TYPE_FLOAT)
    resid_freq: float      # residual frequency in ppm (TYPE_FLOAT)
    skew: float            # frequency skew in ppm (TYPE_FLOAT)
    offset: float          # estimated offset in seconds (TYPE_FLOAT)
    offset_err: float      # offset error bound in seconds (TYPE_FLOAT)

    def has_sufficient_samples(self, minimum: int = 4) -> bool: ...
```

### RTCData

```python
@dataclass(frozen=True)
class RTCData:
    ref_time: float        # last RTC measurement time (TYPE_TIMESPEC -> float)
    samples: int           # calibration sample count (TYPE_UINT16)
    runs: int              # same-sign residual runs (TYPE_UINT16)
    span: int              # sample span in seconds (TYPE_UINT32)
    offset: float          # RTC offset (fast by) in seconds (TYPE_FLOAT)
    freq_offset: float     # RTC frequency offset in ppm (TYPE_FLOAT)

    def is_calibrated(self) -> bool: ...
```

## libchrony Field Name Mapping

### Source Fields
| libchrony Field | Python Attribute |
|-----------------|------------------|
| `"address"` or `"reference ID"` | `address` |
| `"poll"` | `poll` |
| `"stratum"` | `stratum` |
| `"state"` | `state` |
| `"mode"` | `mode` |
| `"flags"` | `flags` |
| `"reachability"` | `reachability` |
| `"last sample ago"` | `last_sample_ago` |
| `"original last sample offset"` | `orig_latest_meas` |
| `"adjusted last sample offset"` | `latest_meas` |
| `"last sample error"` | `latest_meas_err` |

### SourceStats Fields
| libchrony Field | Python Attribute |
|-----------------|------------------|
| `"reference ID"` | `reference_id` |
| `"address"` | `address` |
| `"samples"` | `samples` |
| `"runs"` | `runs` |
| `"span"` | `span` |
| `"standard deviation"` | `std_dev` |
| `"residual frequency"` | `resid_freq` |
| `"skew"` | `skew` |
| `"offset"` | `offset` |
| `"offset error"` | `offset_err` |

### RTCData Fields
| libchrony Field | Python Attribute |
|-----------------|------------------|
| `"reference time"` | `ref_time` |
| `"samples"` | `samples` |
| `"runs"` | `runs` |
| `"span"` | `span` |
| `"offset"` | `offset` |
| `"frequency offset"` | `freq_offset` |

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
