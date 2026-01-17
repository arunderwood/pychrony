# PyChrony: Python bindings for chrony NTP client

PyChrony provides Python bindings for [chrony](https://chrony.tuxfamily.org/) NTP client, allowing monitoring of chrony via native Python code.

## Features

- **Read-only monitoring**: Access chrony status and tracking information
- **Pythonic API**: Clean, typed interface following Python conventions
- **CFFI binding**: Efficient interface to system libchrony library
- **Linux-first**: Optimized for Linux environments with libchrony
- **Type hints**: Full type annotation support for better IDE integration

## Installation

### Prerequisites

- Python 3.10+
- libchrony development library (`sudo apt-get install libchrony-dev` on Debian/Ubuntu)

### Install

```bash
git clone https://github.com/arunderwood/pychrony.git
cd pychrony
uv sync --all-groups
uv pip install -e .
```

## Usage

```python
from pychrony import get_tracking

status = get_tracking()
print(f"Stratum: {status.stratum}")
print(f"Offset: {status.offset:.9f} seconds")
print(f"Synchronized: {status.is_synchronized()}")
```

## Compatibility

- **Python**: 3.10, 3.11, 3.12, 3.13, 3.14
- **Platform**: Linux (primary), other platforms where libchrony is available
- **chrony**: 4.x and later

## License

MIT - see [LICENSE](LICENSE)
