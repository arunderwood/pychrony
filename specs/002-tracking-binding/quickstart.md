# Quickstart: Chrony Tracking Binding

**Feature**: 002-tracking-binding
**Date**: 2026-01-15

## Prerequisites

### System Requirements

1. **Linux** (primary platform)
2. **chronyd** running (`systemctl status chronyd`)
3. **libchrony** installed

### Installing libchrony

```bash
# Ubuntu/Debian
sudo apt-get install libchrony-dev

# Fedora/RHEL/CentOS
sudo dnf install libchrony-devel

# Arch Linux
sudo pacman -S chrony
```

### Installing pychrony

```bash
# Using UV (recommended)
uv pip install pychrony

# Using pip
pip install pychrony
```

## Basic Usage

### Get Tracking Status

```python
from pychrony import get_tracking

# Retrieve current tracking information
status = get_tracking()

# Display synchronization status
print(f"Reference: {status.reference_id_name}")
print(f"Stratum: {status.stratum}")
print(f"Offset: {status.offset:.9f} seconds")
print(f"Frequency: {status.frequency:.3f} ppm")
```

### Check Synchronization

```python
from pychrony import get_tracking

status = get_tracking()

if status.is_synchronized():
    print(f"Synchronized to {status.reference_id_name}")
    print(f"  Stratum: {status.stratum}")
    print(f"  Offset: {status.offset * 1000:.3f} ms")
else:
    print("Not synchronized - check chronyd configuration")
```

### Error Handling

```python
from pychrony import (
    get_tracking,
    ChronyLibraryError,
    ChronyConnectionError,
    ChronyPermissionError,
    ChronyDataError,
)

try:
    status = get_tracking()
    print(f"Offset: {status.offset:.9f} s")

except ChronyLibraryError as e:
    print(f"libchrony not found: {e}")
    print("Install with: sudo apt-get install libchrony-dev")

except ChronyConnectionError as e:
    print(f"Cannot connect to chronyd: {e}")
    print("Check: sudo systemctl status chronyd")

except ChronyPermissionError as e:
    print(f"Permission denied: {e}")
    print("Run as root or add user to chrony group")

except ChronyDataError as e:
    print(f"Invalid data: {e}")
```

## Common Patterns

### Monitoring Script

```python
#!/usr/bin/env python3
"""Simple chrony monitoring script."""

import time
from pychrony import get_tracking, ChronyError

def monitor_chrony(interval: float = 5.0):
    """Monitor chrony tracking status."""
    while True:
        try:
            status = get_tracking()
            offset_ms = status.offset * 1000
            freq_ppm = status.frequency

            sync_char = "+" if status.is_synchronized() else "!"
            print(f"[{sync_char}] offset={offset_ms:+.3f}ms "
                  f"freq={freq_ppm:+.3f}ppm "
                  f"stratum={status.stratum} "
                  f"ref={status.reference_id_name}")

        except ChronyError as e:
            print(f"[E] {e}")

        time.sleep(interval)

if __name__ == "__main__":
    monitor_chrony()
```

### Health Check

```python
from pychrony import get_tracking, ChronyError

def check_time_health(
    max_offset_ms: float = 100.0,
    max_stratum: int = 5,
) -> tuple[bool, str]:
    """Check if time synchronization is healthy.

    Args:
        max_offset_ms: Maximum acceptable offset in milliseconds
        max_stratum: Maximum acceptable stratum level

    Returns:
        Tuple of (healthy: bool, message: str)
    """
    try:
        status = get_tracking()

        if not status.is_synchronized():
            return False, "Not synchronized to any time source"

        offset_ms = abs(status.offset * 1000)
        if offset_ms > max_offset_ms:
            return False, f"Offset too high: {offset_ms:.1f}ms > {max_offset_ms}ms"

        if status.stratum > max_stratum:
            return False, f"Stratum too high: {status.stratum} > {max_stratum}"

        return True, f"Healthy: offset={offset_ms:.3f}ms, stratum={status.stratum}"

    except ChronyError as e:
        return False, f"Error: {e}"


# Usage
healthy, message = check_time_health()
print(f"Time sync: {'OK' if healthy else 'FAIL'} - {message}")
```

### Metrics Export

```python
from pychrony import get_tracking, ChronyError

def get_metrics() -> dict:
    """Get chrony metrics for export (e.g., Prometheus)."""
    try:
        status = get_tracking()
        return {
            "chrony_synchronized": 1 if status.is_synchronized() else 0,
            "chrony_stratum": status.stratum,
            "chrony_offset_seconds": status.offset,
            "chrony_frequency_ppm": status.frequency,
            "chrony_root_delay_seconds": status.root_delay,
            "chrony_root_dispersion_seconds": status.root_dispersion,
            "chrony_rms_offset_seconds": status.rms_offset,
            "chrony_update_interval_seconds": status.update_interval,
        }
    except ChronyError:
        return {"chrony_synchronized": 0}
```

## TrackingStatus Fields

| Field | Type | Description |
|-------|------|-------------|
| `reference_id` | int | NTP reference identifier |
| `reference_id_name` | str | Human-readable source name |
| `stratum` | int | NTP stratum (0=ref clock, 1-15=downstream) |
| `leap_status` | int | Leap second status (0=none, 1=insert, 2=delete) |
| `offset` | float | Time offset from reference (seconds) |
| `last_offset` | float | Previous measurement offset (seconds) |
| `rms_offset` | float | RMS of recent offsets (seconds) |
| `frequency` | float | Clock frequency error (ppm) |
| `residual_freq` | float | Residual frequency (ppm) |
| `skew` | float | Frequency error bound (ppm) |
| `root_delay` | float | Path delay to stratum-1 (seconds) |
| `root_dispersion` | float | Total dispersion (seconds) |
| `update_interval` | float | Time since last update (seconds) |

## Troubleshooting

### chronyd not running

```bash
# Check status
sudo systemctl status chronyd

# Start chronyd
sudo systemctl start chronyd
```

### Permission denied

```bash
# Option 1: Run as root
sudo python your_script.py

# Option 2: Add user to chrony group
sudo usermod -aG chrony $USER
# Log out and back in for group change to take effect
```

### libchrony not found

```bash
# Verify installation
ldconfig -p | grep chrony

# If missing, install development package
sudo apt-get install libchrony-dev  # Debian/Ubuntu
sudo dnf install libchrony-devel     # Fedora/RHEL
```

### Custom socket path

```python
# If chronyd uses non-standard socket location
status = get_tracking(socket_path="/custom/path/chronyd.sock")
```

## Next Steps

- See [API Contract](./contracts/python-api.md) for full API documentation
- See [Data Model](./data-model.md) for field details and validation
- See [Research](./research.md) for technical background
