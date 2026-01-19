# Mock API Contract

**Feature Branch**: `006-protocol-test-mocks`
**Date**: 2026-01-18
**Status**: Complete

## Overview

This document defines the public API contract for the protocol-level test mock infrastructure. The API is designed for test authors who want to write tests that simulate chronyd behavior without running chronyd.

---

## Module: `tests.mocks`

### Public Exports

```python
from tests.mocks import (
    # Configuration dataclasses
    ChronyStateConfig,
    SourceConfig,
    RTCConfig,

    # Pre-built scenarios
    SCENARIO_NTP_SYNCED,
    SCENARIO_UNSYNC,
    SCENARIO_LEAP_INSERT,
    SCENARIO_LEAP_DELETE,
    SCENARIO_GPS_REFCLOCK,
    SCENARIO_RTC_AVAILABLE,
    SCENARIO_MULTI_SOURCE,

    # Context manager
    patched_chrony_connection,
)
```

---

## Context Manager: `patched_chrony_connection`

### Signature

```python
@contextmanager
def patched_chrony_connection(
    config: ChronyStateConfig | None = None,
) -> Generator[ChronyConnection, None, None]:
    """
    Patch pychrony CFFI bindings with mock infrastructure.

    Args:
        config: Mock configuration. Defaults to SCENARIO_NTP_SYNCED.

    Yields:
        ChronyConnection instance connected to mock session.

    Raises:
        ChronyConnectionError: If error_injection includes connection errors.
        ChronyDataError: If error_injection includes data errors.
    """
```

### Usage Contract

1. **MUST** be used as a context manager (`with` statement)
2. **MUST** yield a valid `ChronyConnection` instance
3. **MUST** restore original bindings on exit (even on exception)
4. **MUST** set `_LIBRARY_AVAILABLE = True` for the duration
5. **MAY** raise configured exceptions if `error_injection` is set

### Examples

```python
# Basic usage with default config
with patched_chrony_connection() as conn:
    status = conn.get_tracking()
    assert status.is_synchronized()

# Custom configuration
config = ChronyStateConfig(stratum=3, offset=-0.001)
with patched_chrony_connection(config) as conn:
    status = conn.get_tracking()
    assert status.stratum == 3

# Pre-built scenario
with patched_chrony_connection(SCENARIO_LEAP_INSERT) as conn:
    status = conn.get_tracking()
    assert status.is_leap_pending()

# Error injection
config = ChronyStateConfig(error_injection={"chrony_open_socket": -13})
with pytest.raises(ChronyPermissionError):
    with patched_chrony_connection(config) as conn:
        pass  # Never reached
```

---

## Dataclass: `ChronyStateConfig`

### Signature

```python
@dataclass
class ChronyStateConfig:
    # Tracking fields
    stratum: int = 2
    reference_id: int = 0x7F000001
    reference_ip: str = "127.0.0.1"
    leap_status: LeapStatus = LeapStatus.NORMAL
    ref_time: float = 1705320000.123456789
    offset: float = 0.000123456
    last_offset: float = 0.000111222
    rms_offset: float = 0.000100000
    frequency: float = 1.234
    residual_freq: float = 0.001
    skew: float = 0.005
    root_delay: float = 0.001234
    root_dispersion: float = 0.002345
    update_interval: float = 64.0

    # Sub-configurations
    sources: list[SourceConfig] = field(default_factory=list)
    rtc: RTCConfig | None = None

    # Error injection
    error_injection: dict[str, int] = field(default_factory=dict)
```

### Validation Contract

- `stratum` **MUST** be 0-15
- `rms_offset`, `skew`, `root_delay`, `root_dispersion`, `update_interval`, `ref_time` **MUST** be ≥ 0
- All float fields **MUST** be finite (not NaN or Inf)
- `error_injection` keys **MUST** be valid operation names

### Behavior Contract

1. Fields map directly to `TrackingStatus` fields returned by `get_tracking()`
2. `sources` list determines records returned by `get_sources()` and `get_source_stats()`
3. `rtc` configuration determines `get_rtc_data()` behavior
4. `error_injection` causes specified operations to return error codes

---

## Dataclass: `SourceConfig`

### Signature

```python
@dataclass
class SourceConfig:
    # Source report fields
    address: str = "192.168.1.100"
    poll: int = 6
    stratum: int = 2
    state: SourceState = SourceState.SELECTED
    mode: SourceMode = SourceMode.CLIENT
    flags: int = 0
    reachability: int = 255
    last_sample_ago: int = 32
    orig_latest_meas: float = 0.000123456
    latest_meas: float = 0.000123456
    latest_meas_err: float = 0.000010000

    # Optional overrides
    reference_id: int | None = None  # Auto-computed from address if None

    # SourceStats fields
    samples: int = 8
    runs: int = 3
    span: int = 512
    std_dev: float = 0.000100000
    resid_freq: float = 0.001
    stats_skew: float = 0.005
    stats_offset: float = 0.000123456
    offset_err: float = 0.000010000
```

### Validation Contract

- `stratum` **MUST** be 0-15
- `reachability` **MUST** be 0-255
- `last_sample_ago`, `samples`, `runs`, `span` **MUST** be ≥ 0
- `latest_meas_err`, `std_dev`, `stats_skew`, `offset_err` **MUST** be ≥ 0

### Behavior Contract

1. Populates one `Source` in `get_sources()` result
2. Populates one `SourceStats` in `get_source_stats()` result
3. `reference_id` auto-computed from `address` if not provided

---

## Dataclass: `RTCConfig`

### Signature

```python
@dataclass
class RTCConfig:
    available: bool = True
    ref_time: float = 1705320000.123456789
    samples: int = 10
    runs: int = 4
    span: int = 86400
    offset: float = 0.123456
    freq_offset: float = -1.234
```

### Validation Contract

- `ref_time`, `samples`, `runs`, `span` **MUST** be ≥ 0

### Behavior Contract

1. If `available=True`: `get_rtc_data()` returns `RTCData` with configured values
2. If `available=False`: `get_rtc_data()` returns `None`
3. If `samples=0`: RTC is uncalibrated (`is_calibrated()` returns False)

---

## Pre-Built Scenarios

### `SCENARIO_NTP_SYNCED`

Standard synchronized state with one NTP source.

```python
SCENARIO_NTP_SYNCED = ChronyStateConfig(
    stratum=2,
    reference_id=0x7F000001,
    leap_status=LeapStatus.NORMAL,
    sources=[SourceConfig(state=SourceState.SELECTED)],
)
```

**Use Case**: Default test state, verifying synchronized behavior.

### `SCENARIO_UNSYNC`

Unsynchronized state (stratum 16, no reference).

```python
SCENARIO_UNSYNC = ChronyStateConfig(
    stratum=16,
    reference_id=0,
    leap_status=LeapStatus.UNSYNC,
)
```

**Use Case**: Testing `is_synchronized()` returns False.

### `SCENARIO_LEAP_INSERT`

Leap second insertion pending.

```python
SCENARIO_LEAP_INSERT = ChronyStateConfig(
    stratum=2,
    reference_id=0x7F000001,
    leap_status=LeapStatus.INSERT,
)
```

**Use Case**: Testing `is_leap_pending()` returns True for INSERT.

### `SCENARIO_LEAP_DELETE`

Leap second deletion pending.

```python
SCENARIO_LEAP_DELETE = ChronyStateConfig(
    stratum=2,
    reference_id=0x7F000001,
    leap_status=LeapStatus.DELETE,
)
```

**Use Case**: Testing `is_leap_pending()` returns True for DELETE.

### `SCENARIO_GPS_REFCLOCK`

GPS reference clock at stratum 1.

```python
SCENARIO_GPS_REFCLOCK = ChronyStateConfig(
    stratum=1,
    reference_id=0x47505300,  # "GPS\0"
    sources=[SourceConfig(
        address="GPS",
        stratum=0,
        mode=SourceMode.REFCLOCK,
    )],
)
```

**Use Case**: Testing reference clock scenarios.

### `SCENARIO_RTC_AVAILABLE`

RTC available and calibrated.

```python
SCENARIO_RTC_AVAILABLE = ChronyStateConfig(
    rtc=RTCConfig(available=True, samples=10),
)
```

**Use Case**: Testing `get_rtc_data()` returns valid data.

### `SCENARIO_MULTI_SOURCE`

Multiple sources with different states.

```python
SCENARIO_MULTI_SOURCE = ChronyStateConfig(
    sources=[
        SourceConfig(address="192.168.1.100", state=SourceState.SELECTED),
        SourceConfig(address="192.168.1.101", state=SourceState.FALSETICKER),
        SourceConfig(address="192.168.1.102", state=SourceState.SELECTABLE),
    ],
)
```

**Use Case**: Testing source filtering and selection.

---

## Error Injection Contract

### Supported Operations

| Operation Key | Triggered By | Exception Type |
|---------------|--------------|----------------|
| `"chrony_open_socket"` | Entering context | `ChronyConnectionError` or `ChronyPermissionError` |
| `"chrony_init_session"` | Entering context | `ChronyConnectionError` |
| `"chrony_request_report_number_records"` | Any `get_*` method | `ChronyDataError` |
| `"chrony_process_response"` | Any `get_*` method | `ChronyDataError` |
| `"chrony_request_record"` | Any `get_*` method | `ChronyDataError` |

### Error Code Conventions

- `-13` (EACCES): Permission denied → `ChronyPermissionError`
- Other negative values: General errors → `ChronyConnectionError` or `ChronyDataError`

### Example

```python
# Test permission denied
config = ChronyStateConfig(error_injection={"chrony_open_socket": -13})
with pytest.raises(ChronyPermissionError):
    with patched_chrony_connection(config):
        pass

# Test data error during tracking request
config = ChronyStateConfig(error_injection={"chrony_process_response": -1})
with patched_chrony_connection(config) as conn:
    with pytest.raises(ChronyDataError):
        conn.get_tracking()
```

---

## Compatibility Contract

### Existing Tests

- **MUST NOT** break existing unit tests in `tests/unit/`
- **MUST NOT** break existing contract tests in `tests/contract/`
- **MUST NOT** break existing integration tests in `tests/integration/`

### CFFI Bindings

- **MUST NOT** modify production code in `src/pychrony/`
- **MUST** work without CFFI bindings compiled
- **MUST** work without chronyd running

### Determinism

- **MUST** produce identical results for identical configurations
- **MUST NOT** depend on timing or external state
- **MUST** be safe for parallel test execution (no shared mutable state)
