# pychrony

Python bindings for libchrony - read-only monitoring of chronyd NTP daemon.

## Installation

```bash
pip install pychrony
```

## Quick Example

```python
from pychrony import ChronyConnection

with ChronyConnection() as conn:
    status = conn.get_tracking()
    print(f"Offset: {status.offset:.6f} seconds")
    print(f"Stratum: {status.stratum}")
    if status.is_synchronized():
        print(f"Synchronized to {status.reference_id_name}")
```

## Features

- **Read-only monitoring**: Query chronyd status without modification capabilities
- **Full type hints**: Complete type annotations for IDE support
- **Pythonic API**: Native Python data structures and context managers
- **Multiple reports**: Access tracking, sources, source stats, and RTC data

## Multiple Queries (Connection Reuse)

Use a single connection for multiple queries to minimize overhead:

```python
from pychrony import ChronyConnection

with ChronyConnection() as conn:
    tracking = conn.get_tracking()
    sources = conn.get_sources()
    stats = conn.get_source_stats()
    rtc = conn.get_rtc_data()
```

## Error Handling

pychrony provides typed exceptions for different error conditions:

```python
from pychrony import (
    ChronyConnection,
    ChronyError,
    ChronyLibraryError,
    ChronyConnectionError,
    ChronyPermissionError,
)

try:
    with ChronyConnection() as conn:
        status = conn.get_tracking()
except ChronyLibraryError:
    print("libchrony not installed")
except ChronyConnectionError:
    print("chronyd not running")
except ChronyPermissionError:
    print("Permission denied - add user to chrony group")
```

## Remote and Custom Connections

Connect to a custom Unix socket path:

```python
with ChronyConnection("/custom/path/chronyd.sock") as conn:
    status = conn.get_tracking()
```

Connect to a remote chronyd instance via UDP:

```python
with ChronyConnection("192.168.1.100") as conn:
    status = conn.get_tracking()
```

## Thread Safety

`ChronyConnection` is **NOT thread-safe**. The underlying libchrony session
maintains stateful request/response cycles that cannot be safely shared
between threads.

For multi-threaded applications, use one of these patterns:

**Connection per thread (simplest):**

```python
def worker():
    with ChronyConnection() as conn:
        return conn.get_tracking()
```

**Thread-local storage (for connection reuse):**

```python
import threading

_local = threading.local()

def get_tracking():
    if not hasattr(_local, 'conn'):
        _local.conn = ChronyConnection()
    with _local.conn as conn:
        return conn.get_tracking()
```

The returned dataclasses (`TrackingStatus`, `Source`, etc.) are frozen and
immutable, so they can be safely shared across threads after retrieval.

## Quick Links

- [API Reference](api/index.md) - Complete API documentation
- [GitHub Repository](https://github.com/arunderwood/pychrony) - Source code and issues
- [PyPI Package](https://pypi.org/project/pychrony/) - Installation

## Requirements

- Python 3.10+
- libchrony (system library)
- Linux (primary platform)
