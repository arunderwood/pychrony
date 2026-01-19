# Data Model: Protocol-Level Test Mock Infrastructure

**Feature Branch**: `006-protocol-test-mocks`
**Date**: 2026-01-18
**Status**: Complete

## Overview

This document defines the configuration dataclasses used for declarative test scenario configuration. These classes live in `tests/mocks/config.py` and are used to configure the `MockChronySession` class.

---

## Entity Relationship Diagram

```text
ChronyStateConfig (root)
├── tracking fields (stratum, reference_id, leap_status, offset, etc.)
├── sources: List[SourceConfig] (0..N)
├── rtc: Optional[RTCConfig] (0..1)
└── error_injection: Dict[str, int]

SourceConfig
├── tracking fields for single source
└── stats fields (samples, runs, span, etc.)

RTCConfig
├── available flag
└── RTC-specific fields
```

---

## Entity: ChronyStateConfig

**Description**: Root configuration dataclass representing the complete state of a simulated chronyd connection. Contains tracking fields, source list, RTC configuration, and error injection settings.

**Location**: `tests/mocks/config.py`

### Fields

| Field | Type | Default | Validation | Description |
|-------|------|---------|------------|-------------|
| `stratum` | `int` | `2` | 0 ≤ x ≤ 15 | NTP stratum level |
| `reference_id` | `int` | `0x7F000001` | uint32 | Reference identifier |
| `reference_ip` | `str` | `"127.0.0.1"` | non-empty | Reference source IP/name |
| `leap_status` | `LeapStatus` | `NORMAL` | valid enum | Leap second status |
| `ref_time` | `float` | `1705320000.123` | ≥ 0 | Reference timestamp |
| `offset` | `float` | `0.000123` | finite | Current offset (seconds) |
| `last_offset` | `float` | `0.000111` | finite | Previous offset |
| `rms_offset` | `float` | `0.000100` | ≥ 0, finite | RMS offset |
| `frequency` | `float` | `1.234` | finite | Frequency offset (ppm) |
| `residual_freq` | `float` | `0.001` | finite | Residual frequency |
| `skew` | `float` | `0.005` | ≥ 0, finite | Frequency skew |
| `root_delay` | `float` | `0.001234` | ≥ 0, finite | Root delay |
| `root_dispersion` | `float` | `0.002345` | ≥ 0, finite | Root dispersion |
| `update_interval` | `float` | `64.0` | ≥ 0, finite | Update interval |
| `sources` | `list[SourceConfig]` | `[]` | valid list | Configured sources |
| `rtc` | `RTCConfig \| None` | `None` | optional | RTC configuration |
| `error_injection` | `dict[str, int]` | `{}` | operation→code | Error injection map |

### Relationships

- Contains 0..N `SourceConfig` instances (one per time source)
- Contains 0..1 `RTCConfig` instance (if RTC is configured)

### Derived Behaviors

```python
def reference_id_name(self) -> str:
    """Compute human-readable reference ID name."""
    # Uses same logic as models._ref_id_to_name()

def is_synchronized(self) -> bool:
    """Check if config represents synchronized state."""
    return self.reference_id != 0 and self.stratum < 16

def is_leap_pending(self) -> bool:
    """Check if leap second is pending."""
    return self.leap_status in (LeapStatus.INSERT, LeapStatus.DELETE)
```

### Error Injection Keys

The `error_injection` dictionary maps operation names to error codes:

| Key | Affected Operation | Error Effect |
|-----|-------------------|--------------|
| `"chrony_open_socket"` | Connection open | `ChronyConnectionError` |
| `"chrony_init_session"` | Session init | `ChronyConnectionError` |
| `"chrony_request_report_number_records"` | Report request | `ChronyDataError` |
| `"chrony_process_response"` | Response processing | `ChronyDataError` |
| `"chrony_request_record"` | Record request | `ChronyDataError` |

---

## Entity: SourceConfig

**Description**: Configuration for a single time source, including address, stratum, state, mode, reachability, and measurement values.

**Location**: `tests/mocks/config.py`

### Fields

| Field | Type | Default | Validation | Description |
|-------|------|---------|------------|-------------|
| `address` | `str` | `"192.168.1.100"` | non-empty | Source address |
| `poll` | `int` | `6` | any int | Polling interval (log2 seconds) |
| `stratum` | `int` | `2` | 0 ≤ x ≤ 15 | Source stratum |
| `state` | `SourceState` | `SELECTED` | valid enum | Selection state |
| `mode` | `SourceMode` | `CLIENT` | valid enum | Source mode |
| `flags` | `int` | `0` | uint32 | Source flags |
| `reachability` | `int` | `255` | 0 ≤ x ≤ 255 | Reachability register |
| `last_sample_ago` | `int` | `32` | ≥ 0 | Seconds since sample |
| `orig_latest_meas` | `float` | `0.000123` | finite | Original offset |
| `latest_meas` | `float` | `0.000123` | finite | Adjusted offset |
| `latest_meas_err` | `float` | `0.000010` | ≥ 0, finite | Error bound |
| `reference_id` | `int \| None` | `None` | optional uint32 | Reference ID (auto-computed if None) |
| `samples` | `int` | `8` | ≥ 0 | Sample count (for sourcestats) |
| `runs` | `int` | `3` | ≥ 0 | Run count |
| `span` | `int` | `512` | ≥ 0 | Time span |
| `std_dev` | `float` | `0.000100` | ≥ 0, finite | Standard deviation |
| `resid_freq` | `float` | `0.001` | finite | Residual frequency |
| `stats_skew` | `float` | `0.005` | ≥ 0, finite | Stats skew |
| `stats_offset` | `float` | `0.000123` | finite | Stats offset |
| `offset_err` | `float` | `0.000010` | ≥ 0, finite | Offset error |

### Derived Behaviors

```python
def compute_reference_id(self) -> int:
    """Compute reference_id from address if not set."""
    if self.reference_id is not None:
        return self.reference_id
    # Convert IP to uint32 or ASCII refclock ID
    ...

def is_reachable(self) -> bool:
    """Check if source is reachable."""
    return self.reachability > 0

def is_selected(self) -> bool:
    """Check if source is selected."""
    return self.state == SourceState.SELECTED
```

### Notes

- The `SourceConfig` combines both `sources` report fields and `sourcestats` report fields for convenience
- When used in the mock, source fields populate the `sources` report and stats fields populate `sourcestats`
- The `reference_id` is auto-computed from `address` if not explicitly provided

---

## Entity: RTCConfig

**Description**: Configuration for RTC (Real-Time Clock) data, including reference time, samples, runs, span, offset, and frequency offset.

**Location**: `tests/mocks/config.py`

### Fields

| Field | Type | Default | Validation | Description |
|-------|------|---------|------------|-------------|
| `available` | `bool` | `True` | bool | Whether RTC data is available |
| `ref_time` | `float` | `1705320000.123` | ≥ 0, finite | RTC reference time |
| `samples` | `int` | `10` | ≥ 0 | Calibration samples |
| `runs` | `int` | `4` | ≥ 0 | Run count |
| `span` | `int` | `86400` | ≥ 0 | Time span |
| `offset` | `float` | `0.123456` | finite | RTC offset |
| `freq_offset` | `float` | `-1.234` | finite | Frequency offset |

### Derived Behaviors

```python
def is_calibrated(self) -> bool:
    """Check if RTC has calibration data."""
    return self.samples > 0
```

### Notes

- When `available=False`, the mock returns 0 records for the `rtcdata` report (simulating no RTC)
- When `available=True` but `samples=0`, the RTC is available but uncalibrated

---

## Entity: MockChronySession

**Description**: The mock implementation that maintains protocol state and returns configured data via mock `_lib` and `_ffi` objects.

**Location**: `tests/mocks/session.py`

### State Fields

| Field | Type | Description |
|-------|------|-------------|
| `config` | `ChronyStateConfig` | The configuration driving mock behavior |
| `current_report` | `str \| None` | Currently active report name |
| `current_record_index` | `int` | Current record being accessed |
| `pending_responses` | `int` | Number of responses pending |
| `lib` | `MockLib` | Mock `_lib` object |
| `ffi` | `MockFFI` | Mock `_ffi` object |

### Mock `_lib` Methods

| Method | Signature | Behavior |
|--------|-----------|----------|
| `chrony_open_socket` | `(address) -> int` | Returns 5 (valid fd) or error |
| `chrony_close_socket` | `(fd) -> None` | No-op |
| `chrony_init_session` | `(session_ptr, fd) -> int` | Returns 0 or error |
| `chrony_deinit_session` | `(session) -> None` | No-op |
| `chrony_request_report_number_records` | `(session, name) -> int` | Sets current_report, returns 0 or error |
| `chrony_needs_response` | `(session) -> bool` | Returns True if responses pending |
| `chrony_process_response` | `(session) -> int` | Decrements pending, returns 0 or error |
| `chrony_get_report_number_records` | `(session) -> int` | Returns record count for current report |
| `chrony_request_record` | `(session, name, index) -> int` | Sets current_record_index, returns 0 or error |
| `chrony_get_field_index` | `(session, name) -> int` | Returns field index or -1 |
| `chrony_get_field_float` | `(session, index) -> float` | Returns float field value |
| `chrony_get_field_uinteger` | `(session, index) -> int` | Returns unsigned int value |
| `chrony_get_field_integer` | `(session, index) -> int` | Returns signed int value |
| `chrony_get_field_string` | `(session, index) -> str \| None` | Returns string or NULL |
| `chrony_get_field_timespec` | `(session, index) -> MockTimespec` | Returns timespec struct |

### Mock `_ffi` Methods

| Method/Attr | Behavior |
|-------------|----------|
| `ffi.NULL` | `None` |
| `ffi.new(type_string)` | Returns mock pointer supporting `[0]` |
| `ffi.string(char_ptr)` | Returns bytes from char* |

---

## Field Name Registry

The mock must map field names (as bytes) to field indices and know which report each field belongs to:

### Tracking Report Fields

| Field Name | Index | Type | Config Field |
|------------|-------|------|--------------|
| `b"reference ID"` | 0 | uint | `reference_id` |
| `b"stratum"` | 1 | uint | `stratum` |
| `b"leap status"` | 2 | uint | `leap_status.value` |
| `b"address"` | 3 | string | `reference_ip` |
| `b"current correction"` | 4 | float | `offset` |
| `b"last offset"` | 5 | float | `last_offset` |
| `b"RMS offset"` | 6 | float | `rms_offset` |
| `b"frequency offset"` | 7 | float | `frequency` |
| `b"residual frequency"` | 8 | float | `residual_freq` |
| `b"skew"` | 9 | float | `skew` |
| `b"root delay"` | 10 | float | `root_delay` |
| `b"root dispersion"` | 11 | float | `root_dispersion` |
| `b"last update interval"` | 12 | float | `update_interval` |
| `b"reference time"` | 13 | timespec | `ref_time` |

### Sources Report Fields

| Field Name | Index | Type | Config Field |
|------------|-------|------|--------------|
| `b"address"` | 0 | string | `sources[i].address` |
| `b"reference ID"` | 1 | uint | `sources[i].reference_id` |
| `b"state"` | 2 | uint | `sources[i].state.value` |
| `b"mode"` | 3 | uint | `sources[i].mode.value` |
| `b"poll"` | 4 | int | `sources[i].poll` |
| `b"stratum"` | 5 | uint | `sources[i].stratum` |
| `b"flags"` | 6 | uint | `sources[i].flags` |
| `b"reachability"` | 7 | uint | `sources[i].reachability` |
| `b"last sample ago"` | 8 | uint | `sources[i].last_sample_ago` |
| `b"original last sample offset"` | 9 | float | `sources[i].orig_latest_meas` |
| `b"adjusted last sample offset"` | 10 | float | `sources[i].latest_meas` |
| `b"last sample error"` | 11 | float | `sources[i].latest_meas_err` |

### SourceStats Report Fields

| Field Name | Index | Type | Config Field |
|------------|-------|------|--------------|
| `b"reference ID"` | 0 | uint | `sources[i].reference_id` |
| `b"address"` | 1 | string | `sources[i].address` |
| `b"samples"` | 2 | uint | `sources[i].samples` |
| `b"runs"` | 3 | uint | `sources[i].runs` |
| `b"span"` | 4 | uint | `sources[i].span` |
| `b"standard deviation"` | 5 | float | `sources[i].std_dev` |
| `b"residual frequency"` | 6 | float | `sources[i].resid_freq` |
| `b"skew"` | 7 | float | `sources[i].stats_skew` |
| `b"offset"` | 8 | float | `sources[i].stats_offset` |
| `b"offset error"` | 9 | float | `sources[i].offset_err` |

### RTCData Report Fields

| Field Name | Index | Type | Config Field |
|------------|-------|------|--------------|
| `b"reference time"` | 0 | timespec | `rtc.ref_time` |
| `b"samples"` | 1 | uint | `rtc.samples` |
| `b"runs"` | 2 | uint | `rtc.runs` |
| `b"span"` | 3 | uint | `rtc.span` |
| `b"offset"` | 4 | float | `rtc.offset` |
| `b"frequency offset"` | 5 | float | `rtc.freq_offset` |

---

## State Transitions

### MockChronySession State Machine

```text
IDLE
  │
  ├─ chrony_request_report_number_records(name) ─┐
  │                                               ▼
  │                                         REPORT_REQUESTED
  │                                               │
  │  ┌───────────────────────────────────────────┘
  │  │
  │  ├─ chrony_needs_response() → True
  │  │     └─ chrony_process_response() → decrements pending
  │  │        └─ if pending > 0: stay in REPORT_REQUESTED
  │  │
  │  └─ chrony_needs_response() → False ─────────┐
  │                                               ▼
  │                                         REPORT_READY
  │                                               │
  │  ┌───────────────────────────────────────────┘
  │  │
  │  ├─ chrony_get_report_number_records() → returns count
  │  │
  │  └─ chrony_request_record(name, index) ──────┐
  │                                               ▼
  │                                         RECORD_REQUESTED
  │                                               │
  │  ┌───────────────────────────────────────────┘
  │  │
  │  ├─ chrony_needs_response() → True
  │  │     └─ chrony_process_response()
  │  │
  │  └─ chrony_needs_response() → False ─────────┐
  │                                               ▼
  │                                         RECORD_READY
  │                                               │
  └──────────── chrony_get_field_*() ────────────┘
               (returns configured values)
```

---

## Validation Rules

### ChronyStateConfig Validation

```python
def __post_init__(self):
    if not 0 <= self.stratum <= 15:
        raise ValueError("stratum must be 0-15")
    if self.rms_offset < 0:
        raise ValueError("rms_offset must be non-negative")
    if self.skew < 0:
        raise ValueError("skew must be non-negative")
    if self.root_delay < 0:
        raise ValueError("root_delay must be non-negative")
    if self.root_dispersion < 0:
        raise ValueError("root_dispersion must be non-negative")
    if self.update_interval < 0:
        raise ValueError("update_interval must be non-negative")
    if self.ref_time < 0:
        raise ValueError("ref_time must be non-negative")
```

### SourceConfig Validation

```python
def __post_init__(self):
    if not 0 <= self.stratum <= 15:
        raise ValueError("stratum must be 0-15")
    if not 0 <= self.reachability <= 255:
        raise ValueError("reachability must be 0-255")
    if self.last_sample_ago < 0:
        raise ValueError("last_sample_ago must be non-negative")
    if self.latest_meas_err < 0:
        raise ValueError("latest_meas_err must be non-negative")
```

### RTCConfig Validation

```python
def __post_init__(self):
    if self.samples < 0:
        raise ValueError("samples must be non-negative")
    if self.runs < 0:
        raise ValueError("runs must be non-negative")
    if self.span < 0:
        raise ValueError("span must be non-negative")
    if self.ref_time < 0:
        raise ValueError("ref_time must be non-negative")
```

---

## Usage Examples

### Basic Configuration

```python
from tests.mocks.config import ChronyStateConfig, SourceConfig, RTCConfig
from pychrony import LeapStatus, SourceState, SourceMode

# Default synchronized state
config = ChronyStateConfig()

# Custom configuration
config = ChronyStateConfig(
    stratum=3,
    offset=0.001,
    leap_status=LeapStatus.INSERT,
    sources=[
        SourceConfig(address="ntp.example.com", stratum=2),
        SourceConfig(address="GPS", mode=SourceMode.REFCLOCK, stratum=0),
    ],
    rtc=RTCConfig(samples=20),
)
```

### Error Injection

```python
# Fail on connection
config = ChronyStateConfig(
    error_injection={"chrony_open_socket": -13}  # Permission denied
)

# Fail on tracking request
config = ChronyStateConfig(
    error_injection={"chrony_process_response": -1}
)
```
