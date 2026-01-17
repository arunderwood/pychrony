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

PyChrony uses [libchrony](https://gitlab.com/chrony/libchrony), a C library for communicating with chronyd.

**Pre-built wheels** (recommended): libchrony is bundled—no system dependencies needed.

**Source installs** (sdist or development): Requires libchrony to be installed on your system. See below for installation instructions.

#### libchrony Package Availability

| Distribution | Available | Install Command |
|--------------|-----------|-----------------|
| Fedora 42+ | ✅ Yes | `sudo dnf install libchrony-devel` |
| RHEL/CentOS/Rocky/Alma 9 | ✅ Yes (EPEL) | `sudo dnf install epel-release && sudo dnf install libchrony-devel` |
| Debian/Ubuntu | ❌ No | [Build from source](#building-libchrony-from-source) |
| Alpine | ❌ No | [Build from source](#building-libchrony-from-source) |
| Arch Linux | ❌ No | [Build from source](#building-libchrony-from-source) |

#### Building libchrony from Source

For distributions that don't package libchrony, you'll need to build it from source:

```bash
# Install build dependencies
# Debian/Ubuntu:
sudo apt-get install build-essential libtool libffi-dev

# Alpine:
sudo apk add gcc make libtool libffi-dev musl-dev

# Arch:
sudo pacman -S base-devel libtool libffi

# Clone and build libchrony
git clone https://gitlab.com/chrony/libchrony.git
cd libchrony
make
sudo make install prefix=/usr
sudo ldconfig
```

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

PyChrony is licensed under MIT. See [LICENSE](LICENSE).

Pre-built wheels bundle [libchrony](https://gitlab.com/chrony/libchrony) which is licensed under LGPL-2.1-or-later. See [LICENSES/LGPL-2.1-or-later.txt](LICENSES/LGPL-2.1-or-later.txt).
