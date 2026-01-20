# Testing Guide

This document describes pychrony's test infrastructure, including the test pyramid and two distinct testing approaches for different audiences.

## Test Pyramid

```
                    ┌─────────────────────┐
                    │    Integration      │  Requires Docker + chronyd
                    │    (tests/integration/)  │
                    └──────────┬──────────┘
                               │
                    ┌──────────┴──────────┐
                    │     Contract        │  API stability verification
                    │   (tests/contract/) │
                    └──────────┬──────────┘
                               │
         ┌─────────────────────┴─────────────────────┐
         │                 Unit                      │  No external dependencies
         │              (tests/unit/)                │
         └───────────────────────────────────────────┘
```

### Test Tiers

| Tier | Location | Purpose | Dependencies |
|------|----------|---------|--------------|
| **Unit** | `tests/unit/` | Test business logic, validation, data models | None (mocks CFFI) |
| **Contract** | `tests/contract/` | Verify public API stability | None |
| **Integration** | `tests/integration/` | Test against real chronyd | Docker + chronyd |

### CI/CD Test Isolation

- **Wheel builds**: Run unit + contract tests only (no Docker required)
- **Integration tests**: Run separately in Docker environment with `--cap-add=SYS_TIME`

---

## Two Testing Approaches

pychrony provides two distinct testing utilities for different audiences:

```
┌──────────────────────────────────────────────────────────────────┐
│                     User's Application                           │
└──────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────┐
│                     pychrony Library                             │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │  Consumer Testing (pychrony.testing)                       │◄─┼── Creates objects HERE
│  │  Factory functions for test data                           │  │
│  └────────────────────────────────────────────────────────────┘  │
│                              │                                   │
│                              ▼                                   │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │  Python Wrapper Layer                                      │  │
│  │  (_core/_bindings.py)                                      │  │
│  └────────────────────────────────────────────────────────────┘  │
│                              │                                   │
│                              ▼                                   │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │  CFFI Bindings                                             │◄─┼── Binding Mocks intercept HERE
│  │  (_lib, _ffi)                                              │  │
│  └────────────────────────────────────────────────────────────┘  │
│                              │                                   │
└──────────────────────────────┼───────────────────────────────────┘
                               ▼
┌──────────────────────────────────────────────────────────────────┐
│                     libchrony (C library)                        │
│                 Protocol handling, socket I/O                    │
└──────────────────────────────────────────────────────────────────┘
                               ▼
┌──────────────────────────────────────────────────────────────────┐
│                     chronyd (daemon)                             │
└──────────────────────────────────────────────────────────────────┘
```

### Comparison Table

| Dimension | Consumer Testing | CFFI Binding Mocks |
|-----------|------------------|---------------------|
| **Audience** | Library consumers | pychrony developers |
| **Location** | `pychrony.testing` | `tests/mocks/` |
| **Import** | `from pychrony.testing import ...` | `from tests.mocks import ...` |
| **What it tests** | User application code | Python wrapper layer |
| **Needs chronyd** | No | No |
| **Needs libchrony** | No | No |
| **Creates** | Data objects directly | Mock CFFI session |
| **Simulates hardware scenarios** | No | Yes (GPS, PPS, RTC) |
| **Error injection** | No | Yes |

### What the Binding Mocks Test

The CFFI binding mocks replace `_lib` and `_ffi` objects, allowing tests to verify:

- Python wrapper logic in `_bindings.py` (field extraction, error handling)
- Error code to exception mapping
- Data model construction from field values
- Connection lifecycle management

**Note**: The actual chrony protocol (binary message format, socket I/O) is handled by libchrony. These mocks do not test protocol-level behavior—that's covered by integration tests against real chronyd.

---

## Consumer Testing Utilities (`pychrony.testing`)

**Purpose**: Help library consumers write tests for their applications that use pychrony.

### Overview

The `pychrony.testing` module provides factory functions for creating test instances of pychrony dataclasses with sensible defaults. This is useful when:

- Testing code that processes pychrony data objects
- Writing unit tests that don't need a real chronyd connection
- Creating specific data states for test assertions

### Factory Functions

```python
from pychrony.testing import make_tracking, make_source, make_source_stats, make_rtc_data

# Create with defaults (synchronized state)
status = make_tracking()

# Override specific fields
status = make_tracking(stratum=3, offset=-0.001)

# Create unsynchronized state
status = make_tracking(stratum=16, reference_id=0)
```

Available factory functions:
- `make_tracking(**overrides)` - Creates `TrackingStatus` instances
- `make_source(**overrides)` - Creates `Source` instances
- `make_source_stats(**overrides)` - Creates `SourceStats` instances
- `make_rtc_data(**overrides)` - Creates `RTCData` instances

### Pytest Fixtures

When using pytest, fixtures are auto-discovered:

```python
def test_synchronized_check(tracking_status):
    """tracking_status fixture provides synchronized defaults."""
    assert tracking_status.is_synchronized()

def test_source_reachable(source):
    """source fixture provides selected, reachable source."""
    assert source.is_reachable()
```

Available fixtures: `tracking_status`, `source`, `source_stats`, `rtc_data`

---

## CFFI Binding Mocks (`tests/mocks/`)

**Purpose**: Enable testing pychrony's Python wrapper layer without chronyd, libchrony, or hardware.

### Overview

The binding mocks replace the CFFI `_lib` and `_ffi` objects, allowing tests to:

- Verify wrapper behavior with different chrony states (synchronized, unsync, leap pending)
- Simulate hardware configurations (GPS, PPS, RTC) without actual hardware
- Inject errors at CFFI function boundaries
- Test multi-source scenarios

### Key Components

| Component | Location | Purpose |
|-----------|----------|---------|
| `ChronyStateConfig` | `tests/mocks/config.py` | Root configuration dataclass |
| `SourceConfig` | `tests/mocks/config.py` | Per-source configuration |
| `RTCConfig` | `tests/mocks/config.py` | RTC hardware configuration |
| `patched_chrony_connection` | `tests/mocks/context.py` | Context manager for mocking |
| Scenarios | `tests/mocks/scenarios.py` | Pre-built test configurations |

### Basic Usage

```python
from tests.mocks import patched_chrony_connection, SCENARIO_NTP_SYNCED

def test_tracking_synchronized():
    with patched_chrony_connection(SCENARIO_NTP_SYNCED) as conn:
        status = conn.get_tracking()
        assert status.is_synchronized()
```

### Pre-Built Scenarios

| Scenario | Description |
|----------|-------------|
| `SCENARIO_NTP_SYNCED` | Standard synchronized NTP with one selected source |
| `SCENARIO_UNSYNC` | Unsynchronized state (reference_id=0, no sources) |
| `SCENARIO_LEAP_INSERT` | Leap second insertion pending |
| `SCENARIO_LEAP_DELETE` | Leap second deletion pending |
| `SCENARIO_GPS_REFCLOCK` | GPS reference clock at stratum 1 |
| `SCENARIO_PPS_REFCLOCK` | PPS (Pulse Per Second) reference clock |
| `SCENARIO_RTC_AVAILABLE` | NTP synchronized with RTC configured |
| `SCENARIO_RTC_UNAVAILABLE` | NTP synchronized without RTC |
| `SCENARIO_MULTI_SOURCE` | Multiple sources with different states |

### Configuration Dataclasses

#### ChronyStateConfig

Root configuration for mock chrony state:

```python
from tests.mocks import ChronyStateConfig, SourceConfig
from pychrony.models import LeapStatus

config = ChronyStateConfig(
    stratum=2,
    reference_id=0xC0A80164,  # 192.168.1.100
    reference_ip="192.168.1.100",
    leap_status=LeapStatus.NORMAL,
    offset=0.000123456,
    sources=[
        SourceConfig(address="192.168.1.100", stratum=1),
    ],
)
```

Key fields:
- `stratum`: NTP stratum level (0-16)
- `reference_id`: Reference identifier (uint32)
- `leap_status`: `LeapStatus` enum value
- `sources`: List of `SourceConfig` instances
- `rtc`: Optional `RTCConfig` for RTC data
- `error_injection`: Dict for injecting errors

#### SourceConfig

Configuration for a single time source:

```python
from tests.mocks import SourceConfig
from pychrony.models import SourceState, SourceMode

source = SourceConfig(
    address="192.168.1.100",
    poll=6,  # 64 seconds
    stratum=1,
    state=SourceState.SELECTED,
    mode=SourceMode.CLIENT,
    reachability=255,  # All recent polls succeeded
)
```

#### RTCConfig

Configuration for RTC (Real-Time Clock) data:

```python
from tests.mocks import RTCConfig

rtc = RTCConfig(
    available=True,
    samples=10,
    runs=4,
    span=86400,
    offset=0.123456,
    freq_offset=-1.234,
)
```

### Error Injection

Inject errors at specific CFFI function calls to test error handling:

```python
from tests.mocks import ChronyStateConfig, patched_chrony_connection
from pychrony.exceptions import ChronyPermissionError

config = ChronyStateConfig(
    error_injection={
        "chrony_open_socket": -13,  # EACCES (permission denied)
    }
)

def test_permission_error():
    with pytest.raises(ChronyPermissionError):
        with patched_chrony_connection(config) as conn:
            pass  # Error raised during connection
```

Supported CFFI functions for error injection:
- `chrony_open_socket`: Simulate connection failures (-13 for EACCES)
- `chrony_init_session`: Simulate session initialization failures
- `chrony_request_report_number_records`: Simulate report request failures
- `chrony_process_response`: Simulate response processing failures
- `chrony_request_record`: Simulate record fetch failures

### Custom Scenarios

Create custom scenarios for specific test needs:

```python
from tests.mocks import (
    ChronyStateConfig,
    SourceConfig,
    RTCConfig,
    patched_chrony_connection,
)
from pychrony.models import LeapStatus, SourceState, SourceMode

# Custom scenario: GPS primary with NTP fallback
custom_config = ChronyStateConfig(
    stratum=1,
    reference_id=0x47505300,  # "GPS"
    reference_ip="GPS",
    leap_status=LeapStatus.NORMAL,
    sources=[
        SourceConfig(
            address="GPS",
            stratum=0,
            state=SourceState.SELECTED,
            mode=SourceMode.REFCLOCK,
        ),
        SourceConfig(
            address="pool.ntp.org",
            stratum=2,
            state=SourceState.SELECTABLE,
            mode=SourceMode.CLIENT,
        ),
    ],
    rtc=RTCConfig(available=True, samples=10),
)

def test_gps_with_ntp_fallback():
    with patched_chrony_connection(custom_config) as conn:
        status = conn.get_tracking()
        assert status.stratum == 1

        sources = conn.get_sources()
        assert len(sources) == 2
```

---

## Running Tests

### Unit Tests

```bash
# Run all unit tests
uv run pytest tests/unit -v

# Run specific test file
uv run pytest tests/unit/test_models.py -v

# Run single test
uv run pytest tests/unit/test_models.py::test_name -v
```

### Contract Tests

```bash
# Run contract tests
uv run pytest tests/contract -v
```

### Integration Tests (Docker Required)

```bash
# Build test image
docker build -t pychrony-test -f docker/Dockerfile.test .

# Run integration tests
docker run --rm --cap-add=SYS_TIME pychrony-test \
    sh -c "chronyd && sleep 2 && pytest tests/integration -v"
```

### All Tests with Coverage

```bash
# Run all tests with coverage report
uv run pytest --cov=src --cov-report=html

# View report
open htmlcov/index.html
```

### Quick Verification

```bash
# Run unit + contract tests (no Docker)
uv run pytest tests/unit tests/contract -v
```
