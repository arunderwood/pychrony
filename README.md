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

PyChrony requires the **libchrony** system library to be installed. This is the C library that provides the chrony client API.

| Distribution | Install Command |
|--------------|-----------------|
| Debian/Ubuntu | `sudo apt-get install libchrony-dev` |
| Fedora/RHEL | `sudo dnf install libchrony-devel` |
| Arch Linux | `sudo pacman -S chrony` |

### Install from PyPI

```bash
pip install pychrony
```

### Install from Source (Development)

```bash
git clone https://github.com/arunderwood/pychrony.git
cd pychrony
git submodule update --init
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
