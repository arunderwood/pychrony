# PyChrony: Python bindings for chrony NTP client

[![PyPI version](https://img.shields.io/pypi/v/pychrony)](https://pypi.org/project/pychrony/)
[![Python versions](https://img.shields.io/pypi/pyversions/pychrony)](https://pypi.org/project/pychrony/)
[![CI](https://github.com/arunderwood/pychrony/actions/workflows/ci.yml/badge.svg)](https://github.com/arunderwood/pychrony/actions/workflows/ci.yml)
[![Documentation](https://img.shields.io/badge/docs-pychrony.org-blue)](https://pychrony.org/)
[![License](https://img.shields.io/pypi/l/pychrony)](https://github.com/arunderwood/pychrony/blob/main/LICENSE)

Query your system's time synchronization status from Python. PyChrony provides bindings for [chrony](https://chrony.tuxfamily.org/), the default NTP (Network Time Protocol) client on most Linux distributions, letting you monitor clock accuracy, sync status, and time sources programmatically.

## Features

- **Read-only monitoring**: Access tracking (offset, drift, stratum), sources (NTP servers, peers), statistics (samples, deviation), and RTC data
- **Pythonic API**: Clean, typed interface following Python conventions
- **[CFFI](https://cffi.readthedocs.io/) binding**: Efficient interface to [libchrony](https://gitlab.com/chrony/libchrony)
- **Linux-first**: Optimized for Linux environments with libchrony
- **Type hints**: Full type annotation support for better IDE integration

## Installation

```bash
pip install pychrony
```

Pre-built wheels include libchrony—no system dependencies needed.

<details>
<summary><strong>Building from Source</strong></summary>

Source installs (sdist or development) require [libchrony](https://gitlab.com/chrony/libchrony) to be installed on your system.

#### libchrony Package Availability

| Distribution | Available | Install Command |
|--------------|-----------|-----------------|
| Fedora 42+ | ✅ Yes | `sudo dnf install libchrony-devel` |
| RHEL/CentOS/Rocky/Alma 9 | ✅ Yes (EPEL) | `sudo dnf install epel-release && sudo dnf install libchrony-devel` |
| Debian/Ubuntu | ❌ No | Build from source (see below) |
| Alpine | ❌ No | Build from source (see below) |
| Arch Linux | ❌ No | Build from source (see below) |

#### Building libchrony from Source

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

#### Development Install

```bash
git clone https://github.com/arunderwood/pychrony.git
cd pychrony
git submodule update --init
uv sync --all-groups
uv pip install -e .
```

</details>

## Usage

```python
from pychrony import ChronyConnection

with ChronyConnection() as conn:
    status = conn.get_tracking()
    print(f"Reference: {status.reference_id_name}")
    print(f"Stratum: {status.stratum}")
    print(f"Offset: {status.offset:.9f} seconds")
    print(f"Synchronized: {status.is_synchronized()}")
```

## Compatibility

- **Python**: 3.10, 3.11, 3.12, 3.13, 3.14
- **Platform**: Linux (primary), other platforms where libchrony is available
- **chrony**: 4.x and later

## Resources

- [Documentation](https://pychrony.org/) — Full API reference and guides
- [GitHub Issues](https://github.com/arunderwood/pychrony/issues) — Report bugs or request features
- [chrony documentation](https://chrony.tuxfamily.org/documentation.html) — Understanding NTP and chrony

## License

PyChrony is licensed under MIT. See [LICENSE](LICENSE).

Pre-built wheels bundle [libchrony](https://gitlab.com/chrony/libchrony) which is licensed under LGPL-2.1-or-later. See [LICENSES/LGPL-2.1-or-later.txt](LICENSES/LGPL-2.1-or-later.txt).
