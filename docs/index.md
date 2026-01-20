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
```

## Features

- **Read-only monitoring**: Query chronyd status without modification capabilities
- **Full type hints**: Complete type annotations for IDE support
- **Pythonic API**: Native Python data structures and context managers
- **Multiple reports**: Access tracking, sources, source stats, and RTC data

## Quick Links

- [API Reference](api/index.md) - Complete API documentation
- [GitHub Repository](https://github.com/arunderwood/pychrony) - Source code and issues
- [PyPI Package](https://pypi.org/project/pychrony/) - Installation

## Requirements

- Python 3.10+
- libchrony (system library)
- Linux (primary platform)
