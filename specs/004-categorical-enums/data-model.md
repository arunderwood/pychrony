# Data Model: Python Enums for Categorical Fields

**Branch**: `004-categorical-enums` | **Date**: 2026-01-16

## Entity Overview

This feature introduces three new Enum classes to replace integer constants in existing dataclasses.

## New Entities

### LeapStatus

Represents the NTP leap second indicator status from chrony tracking data.

```python
class LeapStatus(Enum):
    """Leap second status for NTP synchronization.

    Indicates whether time is normal or if a leap second adjustment
    is scheduled at the next midnight UTC.
    """
    NORMAL = 0    # No leap second pending
    INSERT = 1    # Leap second will be inserted at midnight
    DELETE = 2    # Leap second will be deleted at midnight
    UNSYNC = 3    # Clock is unsynchronized
```

| Member | Value | Description |
|--------|-------|-------------|
| NORMAL | 0 | Time is proceeding normally, no leap second scheduled |
| INSERT | 1 | A positive leap second (23:59:60) will be inserted |
| DELETE | 2 | A negative leap second (skipping 23:59:59) will occur |
| UNSYNC | 3 | Clock is not synchronized to a reference |

**Used by**: `TrackingStatus.leap_status`

### SourceState

Represents the selection state of a time source in chrony's source list.

```python
class SourceState(Enum):
    """Selection state of a chrony time source.

    Indicates whether chrony has selected, rejected, or is
    considering this source for time synchronization.
    """
    SELECTED = 0      # Currently selected for synchronization
    NONSELECTABLE = 1 # Cannot be selected (bad measurements)
    FALSETICKER = 2   # Detected as providing incorrect time
    JITTERY = 3       # Measurements have excessive jitter
    UNSELECTED = 4    # Valid but not currently selected
    SELECTABLE = 5    # Candidate for selection
```

| Member | Value | Description |
|--------|-------|-------------|
| SELECTED | 0 | This source is currently being used for synchronization |
| NONSELECTABLE | 1 | Source cannot be selected due to configuration or quality |
| FALSETICKER | 2 | Source detected as providing incorrect time (outlier) |
| JITTERY | 3 | Source has excessive measurement jitter |
| UNSELECTED | 4 | Valid source but another was preferred |
| SELECTABLE | 5 | Candidate source that could be selected |

**Used by**: `Source.state`

### SourceMode

Represents the operational mode of a time source.

```python
class SourceMode(Enum):
    """Operational mode of a chrony time source.

    Distinguishes between NTP client connections, peer
    relationships, and local reference clocks.
    """
    CLIENT = 0    # NTP client polling a server
    PEER = 1      # NTP peer relationship (bidirectional)
    REFCLOCK = 2  # Local reference clock (GPS, PPS, etc.)
```

| Member | Value | Description |
|--------|-------|-------------|
| CLIENT | 0 | Source is an NTP server being polled as a client |
| PEER | 1 | Bidirectional peer relationship with another NTP system |
| REFCLOCK | 2 | Local reference clock (GPS receiver, PPS signal, etc.) |

**Used by**: `Source.mode`

## Modified Entities

### TrackingStatus (modified)

**Change**: `leap_status` field type changes from `int` to `LeapStatus`

```python
@dataclass(frozen=True)
class TrackingStatus:
    # ... other fields unchanged ...
    leap_status: LeapStatus  # Was: int
    # ... other fields unchanged ...
```

**Impact on methods**:
- `is_leap_pending()`: Implementation changes from `self.leap_status in (1, 2)` to `self.leap_status in (LeapStatus.INSERT, LeapStatus.DELETE)`

### Source (modified)

**Changes**:
1. `state` field type changes from `int` to `SourceState`
2. `mode` field type changes from `int` to `SourceMode`
3. `mode_name` property removed
4. `state_name` property removed

```python
@dataclass(frozen=True)
class Source:
    # ... other fields unchanged ...
    state: SourceState  # Was: int
    mode: SourceMode    # Was: int
    # ... other fields unchanged ...

    # REMOVED:
    # @property
    # def mode_name(self) -> str: ...
    # @property
    # def state_name(self) -> str: ...
```

**Impact on methods**:
- `is_selected()`: Implementation changes from `self.state == 0` to `self.state == SourceState.SELECTED`

## Relationships

```
TrackingStatus
    └── leap_status: LeapStatus

Source
    ├── state: SourceState
    └── mode: SourceMode
```

## Validation Rules

### Enum Construction Validation

All enums inherit from `Enum`. Invalid values raise `ValueError`, which is caught in `_bindings.py` and converted to `ChronyDataError`:

```python
# In _bindings.py
try:
    leap_status = LeapStatus(raw_value)
except ValueError:
    raise ChronyDataError(
        f"Unknown leap_status value {raw_value}. "
        "This may indicate a newer chrony version - please update pychrony."
    )
```

### Removed Validation

The following explicit bounds checks in `_bindings.py` become redundant and will be removed:

- `_validate_tracking()`: `if not 0 <= data["leap_status"] <= 3`
- `_validate_source()`: `_validate_bounded_int(data["mode"], "mode", 0, 2)`
- `_validate_source()`: `_validate_bounded_int(data["state"], "state", 0, 5)`

Enum construction handles these implicitly.

## Migration Notes

### For Library Users

**Using enums**:
```python
if source.state == SourceState.SELECTED:
    print("Selected!")
print(source.mode.name)  # "CLIENT"
print(source.mode.value)  # 0
```

### Breaking Changes (pre-1.0)

1. `Source.mode_name` property removed - use `source.mode.name`
2. `Source.state_name` property removed - use `source.state.name`
3. Enum names are uppercase (`"SELECTED"` not `"selected"`)
4. Integer comparisons no longer work (`state == 0` is False) - use enum members

## Type Annotations

All enum types are exported from the package for type annotations:

```python
from pychrony import LeapStatus, SourceState, SourceMode, TrackingStatus, Source

def check_sync(status: TrackingStatus) -> bool:
    return status.leap_status != LeapStatus.UNSYNC

def find_selected(sources: list[Source]) -> Source | None:
    for s in sources:
        if s.state == SourceState.SELECTED:
            return s
    return None
```
