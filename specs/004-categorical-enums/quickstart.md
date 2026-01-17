# Quickstart: Python Enums for Categorical Fields

**Branch**: `004-categorical-enums` | **Date**: 2026-01-16

## Overview

This feature adds Python `Enum` classes for categorical fields in pychrony, providing type safety and IDE autocomplete.

## New Enums

```python
from pychrony import LeapStatus, SourceState, SourceMode
```

### LeapStatus
```python
LeapStatus.NORMAL    # 0 - No leap second pending
LeapStatus.INSERT    # 1 - Leap second will be inserted
LeapStatus.DELETE    # 2 - Leap second will be deleted
LeapStatus.UNSYNC    # 3 - Clock unsynchronized
```

### SourceState
```python
SourceState.SELECTED      # 0 - Currently selected for sync
SourceState.NONSELECTABLE # 1 - Cannot be selected
SourceState.FALSETICKER   # 2 - Detected as false ticker
SourceState.JITTERY       # 3 - Too much jitter
SourceState.UNSELECTED    # 4 - Not currently selected
SourceState.SELECTABLE    # 5 - Candidate for selection
```

### SourceMode
```python
SourceMode.CLIENT   # 0 - NTP client mode
SourceMode.PEER     # 1 - NTP peer mode
SourceMode.REFCLOCK # 2 - Reference clock
```

## Usage Examples

### Check Leap Second Status

```python
from pychrony import get_tracking, LeapStatus

status = get_tracking()

if status.leap_status == LeapStatus.UNSYNC:
    print("Warning: Clock not synchronized")
elif status.leap_status == LeapStatus.INSERT:
    print("Leap second will be inserted at midnight")
elif status.leap_status == LeapStatus.DELETE:
    print("Leap second will be deleted at midnight")
else:
    print("Time is normal")
```

### Filter Sources by State

```python
from pychrony import get_sources, SourceState

sources = get_sources()

# Find the selected source
selected = [s for s in sources if s.state == SourceState.SELECTED]
if selected:
    print(f"Syncing to: {selected[0].address}")

# Find problematic sources
falsetickers = [s for s in sources if s.state == SourceState.FALSETICKER]
for ft in falsetickers:
    print(f"Warning: {ft.address} detected as false ticker")
```

### Group Sources by Mode

```python
from pychrony import get_sources, SourceMode

sources = get_sources()

# Group sources by type
by_mode = {}
for src in sources:
    mode_name = src.mode.name  # "CLIENT", "PEER", or "REFCLOCK"
    by_mode.setdefault(mode_name, []).append(src)

for mode, srcs in by_mode.items():
    print(f"{mode}: {len(srcs)} source(s)")
```

### Type-Safe Match Statement (Python 3.10+)

```python
from pychrony import get_sources, SourceState

for source in get_sources():
    match source.state:
        case SourceState.SELECTED:
            print(f"✓ {source.address} (selected)")
        case SourceState.SELECTABLE:
            print(f"○ {source.address} (selectable)")
        case SourceState.FALSETICKER:
            print(f"✗ {source.address} (falseticker)")
        case _:
            print(f"  {source.address} ({source.state.name.lower()})")
```

## Migration from Previous Versions

### Removed Properties

Replace `mode_name` and `state_name` properties with `.name`:

```python
# Before:
print(source.mode_name)   # "client"
print(source.state_name)  # "selected"

# After:
print(source.mode.name)   # "CLIENT"
print(source.state.name)  # "SELECTED"

# For lowercase (if needed):
print(source.mode.name.lower())  # "client"
```

## Error Handling

Unknown enum values raise `ChronyDataError`:

```python
from pychrony import get_tracking, ChronyDataError

try:
    status = get_tracking()
except ChronyDataError as e:
    # May indicate chrony version mismatch
    print(f"Data error: {e}")
```
