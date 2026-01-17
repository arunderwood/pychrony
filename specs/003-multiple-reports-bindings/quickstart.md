# Quickstart: Multiple Reports Bindings

**Date**: 2026-01-16
**Feature**: 003-multiple-reports-bindings

## Overview

This feature adds three new functions to pychrony for retrieving additional chronyd reports:

- `get_sources()` - List of NTP time sources
- `get_source_stats()` - Statistics for each source
- `get_rtc_data()` - Real-Time Clock information

## Installation

```bash
# Requires libchrony and libchrony-devel on the system
pip install pychrony
```

## Basic Usage

### Query Time Sources

```python
from pychrony import get_sources

# Get all configured time sources
sources = get_sources()

for source in sources:
    print(f"{source.address}:")
    print(f"  Mode: {source.mode_name}")
    print(f"  State: {source.state_name}")
    print(f"  Stratum: {source.stratum}")
    print(f"  Reachable: {source.is_reachable()}")
    print(f"  Offset: {source.offset:.6f} seconds")
```

### Query Source Statistics

```python
from pychrony import get_source_stats

# Get statistics for all sources
stats = get_source_stats()

for stat in stats:
    print(f"{stat.address}:")
    print(f"  Samples: {stat.n_samples}")
    print(f"  Span: {stat.span:.0f} seconds")
    print(f"  Offset: {stat.offset:.6f} seconds")
    print(f"  Std Dev: {stat.std_dev:.6f} seconds")
    print(f"  Frequency: {stat.frequency:.3f} ppm")
```

### Query RTC Data

```python
from pychrony import get_rtc_data, ChronyDataError

try:
    rtc = get_rtc_data()
    print(f"RTC offset: {rtc.offset:.3f} seconds")
    print(f"RTC drift: {rtc.frequency:.3f} ppm")
    print(f"Calibration samples: {rtc.n_samples}")
except ChronyDataError as e:
    print(f"RTC not available: {e}")
```

## Complete Monitoring Example

```python
from pychrony import (
    get_tracking,
    get_sources,
    get_source_stats,
    get_rtc_data,
    ChronyDataError,
)

def monitor_chrony():
    """Print complete chronyd status."""

    # Tracking status
    tracking = get_tracking()
    print("=== Tracking ===")
    print(f"Synchronized: {tracking.is_synchronized()}")
    print(f"Reference: {tracking.reference_ip}")
    print(f"Offset: {tracking.offset:.6f} seconds")
    print()

    # Time sources
    sources = get_sources()
    print(f"=== Sources ({len(sources)}) ===")
    for src in sources:
        sync_marker = "*" if src.is_selected() else " "
        print(f"{sync_marker} {src.address}: {src.state_name}, stratum {src.stratum}")
    print()

    # Source statistics
    stats = get_source_stats()
    print("=== Source Stats ===")
    for stat in stats:
        print(f"{stat.address}: {stat.n_samples} samples, offset={stat.offset:.6f}s")
    print()

    # RTC (may not be available)
    print("=== RTC ===")
    try:
        rtc = get_rtc_data()
        print(f"Offset: {rtc.offset:.3f}s, drift: {rtc.frequency:.3f} ppm")
    except ChronyDataError:
        print("RTC tracking not available")

if __name__ == "__main__":
    monitor_chrony()
```

## Correlating Sources with Stats

Sources and their statistics are returned as separate snapshots. Correlate by address:

```python
from pychrony import get_sources, get_source_stats

sources = get_sources()
stats = get_source_stats()

# Build lookup by address
stats_by_addr = {s.address: s for s in stats}

for source in sources:
    stat = stats_by_addr.get(source.address)
    if stat:
        print(f"{source.address}:")
        print(f"  State: {source.state_name}")
        print(f"  Samples: {stat.n_samples}")
        print(f"  Offset: {stat.offset:.6f}s ± {stat.std_dev:.6f}s")
```

## Error Handling

```python
from pychrony import (
    get_sources,
    ChronyLibraryError,
    ChronyConnectionError,
    ChronyPermissionError,
    ChronyDataError,
)

try:
    sources = get_sources()
except ChronyLibraryError:
    print("libchrony not installed - install libchrony-devel")
except ChronyConnectionError:
    print("Cannot connect to chronyd - is it running?")
except ChronyPermissionError:
    print("Permission denied - add user to chrony group")
except ChronyDataError as e:
    print(f"Data error: {e}")
```

## Custom Socket Path

All functions accept an optional `socket_path` parameter:

```python
from pychrony import get_sources

# Use custom socket location
sources = get_sources(socket_path="/custom/path/chronyd.sock")
```
