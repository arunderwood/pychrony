# Quickstart: Protocol-Level Test Mocks

**Feature Branch**: `006-protocol-test-mocks`
**Date**: 2026-01-18

## Overview

This guide shows how to use the protocol-level test mock infrastructure to write tests for pychrony without requiring chronyd or hardware dependencies.

---

## Installation

The mock infrastructure lives in `tests/mocks/` and is available automatically when running tests:

```python
from tests.mocks import (
    patched_chrony_connection,
    ChronyStateConfig,
    SourceConfig,
    RTCConfig,
    SCENARIO_NTP_SYNCED,
    SCENARIO_LEAP_INSERT,
)
```

---

## Basic Usage

### Using Default Configuration

```python
def test_default_synchronized_state():
    """Test with default synchronized configuration."""
    with patched_chrony_connection() as conn:
        status = conn.get_tracking()

        assert status.is_synchronized()
        assert status.stratum == 2
        assert status.leap_status == LeapStatus.NORMAL
```

### Using Pre-Built Scenarios

```python
def test_leap_second_pending():
    """Test leap second detection."""
    with patched_chrony_connection(SCENARIO_LEAP_INSERT) as conn:
        status = conn.get_tracking()

        assert status.is_leap_pending()
        assert status.leap_status == LeapStatus.INSERT
```

### Custom Configuration

```python
def test_custom_offset():
    """Test with custom offset value."""
    config = ChronyStateConfig(offset=-0.005)

    with patched_chrony_connection(config) as conn:
        status = conn.get_tracking()

        assert status.offset == -0.005
```

---

## Testing RTC Functionality

### RTC Available

```python
def test_rtc_available():
    """Test RTC data retrieval."""
    config = ChronyStateConfig(
        rtc=RTCConfig(available=True, samples=15, offset=0.5)
    )

    with patched_chrony_connection(config) as conn:
        rtc = conn.get_rtc_data()

        assert rtc is not None
        assert rtc.samples == 15
        assert rtc.offset == 0.5
        assert rtc.is_calibrated()
```

### RTC Unavailable

```python
def test_rtc_unavailable():
    """Test when RTC is not configured."""
    config = ChronyStateConfig(rtc=None)

    with patched_chrony_connection(config) as conn:
        rtc = conn.get_rtc_data()

        assert rtc is None
```

### RTC Uncalibrated

```python
def test_rtc_uncalibrated():
    """Test uncalibrated RTC (samples=0)."""
    config = ChronyStateConfig(
        rtc=RTCConfig(available=True, samples=0)
    )

    with patched_chrony_connection(config) as conn:
        rtc = conn.get_rtc_data()

        assert rtc is not None
        assert not rtc.is_calibrated()
```

---

## Testing Time Sources

### Single Source

```python
def test_single_source():
    """Test with one NTP source."""
    config = ChronyStateConfig(
        sources=[SourceConfig(address="ntp.example.com", stratum=2)]
    )

    with patched_chrony_connection(config) as conn:
        sources = conn.get_sources()

        assert len(sources) == 1
        assert sources[0].address == "ntp.example.com"
        assert sources[0].stratum == 2
```

### Multiple Sources with Different States

```python
def test_multi_source_filtering():
    """Test filtering sources by state."""
    config = ChronyStateConfig(
        sources=[
            SourceConfig(address="good.ntp.org", state=SourceState.SELECTED),
            SourceConfig(address="bad.ntp.org", state=SourceState.FALSETICKER),
            SourceConfig(address="ok.ntp.org", state=SourceState.SELECTABLE),
        ]
    )

    with patched_chrony_connection(config) as conn:
        sources = conn.get_sources()

        selected = [s for s in sources if s.is_selected()]
        assert len(selected) == 1
        assert selected[0].address == "good.ntp.org"
```

### GPS Reference Clock

```python
def test_gps_refclock():
    """Test GPS reference clock source."""
    config = ChronyStateConfig(
        stratum=1,
        reference_id=0x47505300,  # "GPS\0"
        sources=[SourceConfig(
            address="GPS",
            stratum=0,
            mode=SourceMode.REFCLOCK,
            state=SourceState.SELECTED,
        )]
    )

    with patched_chrony_connection(config) as conn:
        sources = conn.get_sources()

        assert len(sources) == 1
        assert sources[0].mode == SourceMode.REFCLOCK
        assert sources[0].address == "GPS"
```

### Source Reachability

```python
def test_source_reachability():
    """Test reachability detection."""
    config = ChronyStateConfig(
        sources=[
            SourceConfig(address="reachable.ntp.org", reachability=255),
            SourceConfig(address="unreachable.ntp.org", reachability=0),
        ]
    )

    with patched_chrony_connection(config) as conn:
        sources = conn.get_sources()

        reachable = [s for s in sources if s.is_reachable()]
        assert len(reachable) == 1
        assert reachable[0].address == "reachable.ntp.org"
```

---

## Testing Leap Seconds

### Leap Insert

```python
def test_leap_insert():
    """Test leap second insertion state."""
    with patched_chrony_connection(SCENARIO_LEAP_INSERT) as conn:
        status = conn.get_tracking()

        assert status.leap_status == LeapStatus.INSERT
        assert status.is_leap_pending()
```

### Leap Delete

```python
def test_leap_delete():
    """Test leap second deletion state."""
    with patched_chrony_connection(SCENARIO_LEAP_DELETE) as conn:
        status = conn.get_tracking()

        assert status.leap_status == LeapStatus.DELETE
        assert status.is_leap_pending()
```

### Normal (No Leap)

```python
def test_no_leap_pending():
    """Test normal state (no leap second)."""
    config = ChronyStateConfig(leap_status=LeapStatus.NORMAL)

    with patched_chrony_connection(config) as conn:
        status = conn.get_tracking()

        assert not status.is_leap_pending()
```

---

## Testing Synchronization States

### Synchronized

```python
def test_synchronized():
    """Test synchronized state."""
    config = ChronyStateConfig(stratum=2, reference_id=0x7F000001)

    with patched_chrony_connection(config) as conn:
        status = conn.get_tracking()

        assert status.is_synchronized()
```

### Unsynchronized

```python
def test_unsynchronized():
    """Test unsynchronized state."""
    with patched_chrony_connection(SCENARIO_UNSYNC) as conn:
        status = conn.get_tracking()

        assert not status.is_synchronized()
        assert status.stratum == 16
        assert status.reference_id == 0
```

### Stratum Boundary

```python
def test_stratum_boundary():
    """Test stratum 15 is still synchronized."""
    config = ChronyStateConfig(stratum=15, reference_id=0x7F000001)

    with patched_chrony_connection(config) as conn:
        status = conn.get_tracking()

        assert status.is_synchronized()
```

---

## Error Injection

### Connection Error

```python
def test_connection_error():
    """Test connection failure."""
    config = ChronyStateConfig(
        error_injection={"chrony_open_socket": -1}
    )

    with pytest.raises(ChronyConnectionError):
        with patched_chrony_connection(config) as conn:
            pass  # Should not reach here
```

### Permission Denied

```python
def test_permission_denied():
    """Test permission denied error."""
    config = ChronyStateConfig(
        error_injection={"chrony_open_socket": -13}  # EACCES
    )

    with pytest.raises(ChronyPermissionError):
        with patched_chrony_connection(config) as conn:
            pass
```

### Data Error During Tracking

```python
def test_tracking_data_error():
    """Test data error during tracking request."""
    config = ChronyStateConfig(
        error_injection={"chrony_process_response": -1}
    )

    with patched_chrony_connection(config) as conn:
        with pytest.raises(ChronyDataError):
            conn.get_tracking()
```

### Record Request Error

```python
def test_record_request_error():
    """Test error during record retrieval."""
    config = ChronyStateConfig(
        error_injection={"chrony_request_record": -1}
    )

    with patched_chrony_connection(config) as conn:
        with pytest.raises(ChronyDataError):
            conn.get_sources()  # Fails when requesting source records
```

---

## Source Statistics

```python
def test_source_stats():
    """Test source statistics retrieval."""
    config = ChronyStateConfig(
        sources=[SourceConfig(
            address="ntp.example.com",
            samples=12,
            std_dev=0.0001,
        )]
    )

    with patched_chrony_connection(config) as conn:
        stats = conn.get_source_stats()

        assert len(stats) == 1
        assert stats[0].samples == 12
        assert stats[0].has_sufficient_samples(minimum=10)
```

---

## Combining Configurations

```python
def test_complex_scenario():
    """Test complex multi-feature scenario."""
    config = ChronyStateConfig(
        stratum=1,
        reference_id=0x47505300,  # GPS
        leap_status=LeapStatus.INSERT,
        offset=0.000001,
        sources=[
            SourceConfig(address="GPS", mode=SourceMode.REFCLOCK, stratum=0),
            SourceConfig(address="192.168.1.100", stratum=2),
        ],
        rtc=RTCConfig(available=True, samples=50),
    )

    with patched_chrony_connection(config) as conn:
        status = conn.get_tracking()
        sources = conn.get_sources()
        rtc = conn.get_rtc_data()

        assert status.stratum == 1
        assert status.is_leap_pending()
        assert len(sources) == 2
        assert rtc is not None
        assert rtc.is_calibrated()
```

---

## Best Practices

### 1. Use Pre-Built Scenarios When Possible

```python
# Good - clear intent
with patched_chrony_connection(SCENARIO_LEAP_INSERT) as conn:
    ...

# Less clear - same effect but requires reading the config
with patched_chrony_connection(ChronyStateConfig(leap_status=LeapStatus.INSERT)) as conn:
    ...
```

### 2. Keep Test Configs Minimal

```python
# Good - only set what you're testing
config = ChronyStateConfig(stratum=3)

# Verbose - unnecessary defaults repeated
config = ChronyStateConfig(
    stratum=3,
    reference_id=0x7F000001,  # default
    leap_status=LeapStatus.NORMAL,  # default
    offset=0.000123456,  # default
    ...
)
```

### 3. Test One Thing at a Time

```python
# Good - focused test
def test_leap_pending_returns_true_for_insert():
    with patched_chrony_connection(SCENARIO_LEAP_INSERT) as conn:
        assert conn.get_tracking().is_leap_pending()

# Too broad - testing multiple unrelated things
def test_everything():
    with patched_chrony_connection(SCENARIO_LEAP_INSERT) as conn:
        status = conn.get_tracking()
        assert status.is_leap_pending()
        assert status.stratum == 2
        assert status.offset > 0
        ...
```

### 4. Use Descriptive Test Names

```python
# Good
def test_get_rtc_data_returns_none_when_rtc_unavailable():
    ...

def test_is_synchronized_returns_false_when_stratum_is_16():
    ...

# Poor
def test_rtc():
    ...

def test_sync():
    ...
```
