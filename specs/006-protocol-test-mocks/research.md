# Research: Protocol-Level Test Mock Infrastructure

**Feature Branch**: `006-protocol-test-mocks`
**Date**: 2026-01-18
**Status**: Complete

## Overview

This document captures research findings for implementing protocol-level test mocks that simulate chronyd responses without requiring hardware, special system states, or running chronyd.

---

## Research Area 1: CFFI Object Mocking Patterns

### Decision: Use Module-Level Patching with MagicMock

**Rationale**: The existing test suite in `tests/unit/test_connection.py` demonstrates successful patterns using `unittest.mock.patch` to replace `_lib` and `_ffi` at the module level. This approach is superior to trying to mock CFFI internals because CFFI compiled bindings are native extensions.

**Alternatives Considered**:
- **Direct CFFI struct creation**: Rejected - requires compiled bindings to exist
- **Subclassing CFFI types**: Rejected - CFFI types are C extensions, not subclassable
- **Monkey-patching CFFI module**: Rejected - too invasive, may affect other tests

**Implementation Pattern**:
```python
@contextmanager
def patched_chrony_connection(config):
    with patch('pychrony._core._bindings._lib') as mock_lib, \
         patch('pychrony._core._bindings._ffi') as mock_ffi, \
         patch('pychrony._core._bindings._LIBRARY_AVAILABLE', True):
        # Configure mocks based on config
        yield
```

---

## Research Area 2: Field Name Mapping

### Decision: Maintain Complete Field Name Registry

The mock must know all field names used in `_bindings.py`. Analysis of the source reveals these field names:

**Tracking Fields** (from `_bindings.py:393-420`):
- `"reference ID"` - uint32 reference identifier
- `"stratum"` - uint32 stratum level
- `"leap status"` - uint32 leap status code
- `"address"` - string IP address
- `"current correction"` - float offset
- `"last offset"` - float previous offset
- `"RMS offset"` - float RMS offset
- `"frequency offset"` - float frequency error
- `"residual frequency"` - float residual frequency
- `"skew"` - float frequency skew
- `"root delay"` - float root delay
- `"root dispersion"` - float root dispersion
- `"last update interval"` - float update interval
- `"reference time"` - timespec reference timestamp

**Source Fields** (from `_bindings.py:492-534`):
- `"address"` - string source address
- `"reference ID"` - uint32 reference ID
- `"state"` - uint32 source state
- `"mode"` - uint32 source mode
- `"poll"` - int32 polling interval
- `"stratum"` - uint32 stratum
- `"flags"` - uint32 flags
- `"reachability"` - uint32 reachability register
- `"last sample ago"` - uint32 seconds since sample
- `"original last sample offset"` - float original offset
- `"adjusted last sample offset"` - float adjusted offset
- `"last sample error"` - float error bound

**SourceStats Fields** (from `_bindings.py:582-595`):
- `"reference ID"` - uint32 reference ID
- `"address"` - string address
- `"samples"` - uint32 sample count
- `"runs"` - uint32 run count
- `"span"` - uint32 time span
- `"standard deviation"` - float std dev
- `"residual frequency"` - float residual freq
- `"skew"` - float skew
- `"offset"` - float offset
- `"offset error"` - float offset error

**RTC Fields** (from `_bindings.py:655-664`):
- `"reference time"` - timespec reference time
- `"samples"` - uint32 samples
- `"runs"` - uint32 runs
- `"span"` - uint32 span
- `"offset"` - float offset
- `"frequency offset"` - float freq offset

---

## Research Area 3: Protocol State Machine

### Decision: Track Report Context and Response Lifecycle

The chrony protocol follows a specific lifecycle that the mock must simulate:

1. **Request Phase**: `chrony_request_report_number_records(session, report_name)`
2. **Response Loop**: `chrony_needs_response()` → `chrony_process_response()` (repeat until needs_response returns false)
3. **Record Count**: `chrony_get_report_number_records(session)` → number of records
4. **Per-Record Loop**: For each record:
   - `chrony_request_record(session, report_name, index)`
   - Response loop (same as step 2)
   - Field extraction with `chrony_get_field_*` calls

**Report Types** (must track separately):
- `b"tracking"` - 1 record with synchronization data
- `b"sources"` - N records, one per time source
- `b"sourcestats"` - N records, statistics per source
- `b"rtcdata"` - 1 record if RTC available, 0 otherwise

---

## Research Area 4: Struct Simulation

### Decision: Use Simple Python Objects for CFFI Structs

**Timespec Simulation**:
```python
@dataclass
class MockTimespec:
    tv_sec: int
    tv_nsec: int
```

**Rationale**: The code only accesses `.tv_sec` and `.tv_nsec` attributes. A simple dataclass or object with these attributes suffices.

---

## Research Area 5: Error Injection

### Decision: Dictionary-Based Error Configuration

**Error Injection Pattern**:
```python
@dataclass
class ChronyStateConfig:
    error_injection: dict[str, int] = field(default_factory=dict)
    # Maps operation name to error code
    # e.g., {"chrony_open_socket": -13, "chrony_process_response": -1}
```

**Error Code Conventions**:
- Negative values indicate errors (follows POSIX errno convention)
- `chrony_open_socket` returns -errno.EACCES (-13) for permission denied
- `chrony_init_session`, `chrony_process_response`, `chrony_request_*` return negative error codes

---

## Research Area 6: ffi Object Simulation

### Decision: Custom FFI Mock with Required Methods

**Required `_ffi` Methods/Attributes**:
- `ffi.new(type_string)` - Returns mock pointer supporting `[0]` indexing
- `ffi.string(char_ptr)` - Converts char* to bytes
- `ffi.NULL` - NULL pointer sentinel (use `None`)

**Implementation Pattern**:
```python
class MockFFI:
    NULL = None

    def new(self, type_string):
        if "**" in type_string:
            ptr = MagicMock()
            ptr.__getitem__ = MagicMock(return_value=MagicMock())
            return ptr
        return MagicMock()

    def string(self, char_ptr):
        if char_ptr is None:
            return b""
        return char_ptr.encode() if isinstance(char_ptr, str) else char_ptr
```

---

## Research Area 7: Configuration Dataclass Design

### Decision: Hierarchical Dataclass Configuration

**Root Configuration**:
```python
@dataclass
class ChronyStateConfig:
    # Tracking fields (maps directly to TrackingStatus)
    stratum: int = 2
    reference_id: int = 0x7F000001
    leap_status: LeapStatus = LeapStatus.NORMAL
    offset: float = 0.000123
    # ... other tracking fields

    # Related configurations
    sources: list[SourceConfig] = field(default_factory=list)
    rtc: RTCConfig | None = None

    # Error injection
    error_injection: dict[str, int] = field(default_factory=dict)
```

**Source Configuration**:
```python
@dataclass
class SourceConfig:
    address: str = "192.168.1.100"
    stratum: int = 2
    state: SourceState = SourceState.SELECTED
    mode: SourceMode = SourceMode.CLIENT
    reachability: int = 255
    # ... other source fields
```

**RTC Configuration**:
```python
@dataclass
class RTCConfig:
    available: bool = True
    samples: int = 10
    offset: float = 0.123
    # ... other RTC fields
```

**Rationale**:
- Dataclasses provide automatic `__init__`, `__repr__`, `__eq__`
- Type hints enable IDE support and documentation
- Default values enable quick scenario creation
- Composition allows building complex scenarios from simple configs

---

## Research Area 8: Pre-Built Scenario Design

### Decision: Module-Level Constants with Descriptive Names

**Scenario Constants** (per spec FR-005):
```python
# Standard synchronized state
SCENARIO_NTP_SYNCED = ChronyStateConfig(
    stratum=2,
    reference_id=0x7F000001,
    leap_status=LeapStatus.NORMAL,
    sources=[SourceConfig(state=SourceState.SELECTED)],
)

# Unsynchronized (stratum 16)
SCENARIO_UNSYNC = ChronyStateConfig(
    stratum=16,
    reference_id=0,
    leap_status=LeapStatus.UNSYNC,
)

# Leap second pending insert
SCENARIO_LEAP_INSERT = ChronyStateConfig(
    leap_status=LeapStatus.INSERT,
)

# Leap second pending delete
SCENARIO_LEAP_DELETE = ChronyStateConfig(
    leap_status=LeapStatus.DELETE,
)

# GPS reference clock at stratum 1
SCENARIO_GPS_REFCLOCK = ChronyStateConfig(
    stratum=1,
    reference_id=0x47505300,  # "GPS\0"
    sources=[SourceConfig(
        address="GPS",
        stratum=0,
        mode=SourceMode.REFCLOCK,
    )],
)

# RTC available and calibrated
SCENARIO_RTC_AVAILABLE = ChronyStateConfig(
    rtc=RTCConfig(available=True, samples=10),
)

# Multiple sources with different states
SCENARIO_MULTI_SOURCE = ChronyStateConfig(
    sources=[
        SourceConfig(address="192.168.1.100", state=SourceState.SELECTED),
        SourceConfig(address="192.168.1.101", state=SourceState.FALSETICKER),
        SourceConfig(address="192.168.1.102", state=SourceState.SELECTABLE),
    ],
)
```

---

## Research Area 9: Context Manager Design

### Decision: Single-Entry Context Manager Yielding Connection

**Pattern**:
```python
@contextmanager
def patched_chrony_connection(config: ChronyStateConfig | None = None):
    """Context manager that patches CFFI bindings with mock infrastructure.

    Args:
        config: Configuration for the mock. If None, uses SCENARIO_NTP_SYNCED.

    Yields:
        ChronyConnection instance ready for use.

    Example:
        with patched_chrony_connection(SCENARIO_LEAP_INSERT) as conn:
            status = conn.get_tracking()
            assert status.is_leap_pending()
    """
    config = config or SCENARIO_NTP_SYNCED

    mock_session = MockChronySession(config)

    with patch('pychrony._core._bindings._lib', mock_session.lib), \
         patch('pychrony._core._bindings._ffi', mock_session.ffi), \
         patch('pychrony._core._bindings._LIBRARY_AVAILABLE', True):
        with ChronyConnection() as conn:
            yield conn
```

**Rationale**:
- Users get a ready-to-use `ChronyConnection` object
- No need to understand mock internals
- Configuration is declarative
- Test code is minimal (≤3 lines as per SC-003)

---

## Summary

| Research Area | Decision | Key Rationale |
|---------------|----------|---------------|
| CFFI Mocking | Module-level patching | Existing patterns work; CFFI internals not subclassable |
| Field Names | Complete registry | Must match `_bindings.py` exactly |
| Protocol State | Request/response tracking | Simulates async protocol lifecycle |
| Structs | Simple Python objects | Only need attribute access |
| Error Injection | Dictionary mapping | Flexible, per-operation errors |
| FFI Mock | Custom class | Need `new()`, `string()`, `NULL` |
| Configuration | Hierarchical dataclasses | Type-safe, composable, documented |
| Scenarios | Module constants | Pre-built for common cases |
| Context Manager | Yields ChronyConnection | Minimal test setup |

All research areas resolved. Ready for Phase 1: Design & Contracts.
