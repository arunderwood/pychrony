# PyChrony: Python bindings for chrony NTP client

PyChrony provides Python bindings for [chrony](https://chrony.tuxfamily.org/) NTP (Network Time Protocol) client, allowing monitoring of chrony via native Python code.

## Features

- **Read-only monitoring**: Access chrony status and tracking information
- **Pythonic API**: Clean, typed interface following Python conventions  
- **CFFI binding**: Efficient interface to system libchrony library
- **Linux-first**: Optimized for Linux environments with libchrony
- **Type hints**: Full type annotation support for better IDE integration

## What pychrony is

- A thin, typed Python wrapper around libchrony
- Focused on read-only monitoring data
- Designed for observability, dashboards, and analysis
- Linux-first and CI-tested

## What pychrony is not

- A replacement for chronyc
- A chronyd configuration or control tool
- A client-reporting API (chronyc clients is out of scope)
- A reimplementation of chronyd protocols

If libchrony does not support a feature, pychrony does not implement it.

## Installation

### Prerequisites

- Python 3.10 or higher
- libchrony development library (on Ubuntu/Debian: `sudo apt-get install libchrony-dev`)
- UV package manager

### Quick Install

```bash
# Install UV (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone and install
git clone https://github.com/arunderwood/pychrony.git
cd pychrony
uv sync --all-groups

# Install in development mode
uv pip install -e .
```

## Usage

```python
import pychrony
from importlib.metadata import version

# Check version
print(f"PyChrony version: {version('pychrony')}")

# Future API:
# from pychrony import ChronyClient
# client = ChronyClient()
# status = client.get_tracking()
# print(f"Time offset: {status.offset}")
```

## Development

### Setup Development Environment

```bash
# Clone repository
git clone https://github.com/arunderwood/pychrony.git
cd pychrony

# Install development dependencies
uv sync --all-groups

# Run tests
uv run pytest

# Format code
uv run ruff format .

# Check linting
uv run ruff check .

# Type checking
uv run ty check src/
```

### Testing

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src --cov-report=html

# Run specific test file
uv run pytest tests/test_import.py -v
```

### Multi-Python Testing

```bash
# Test across Python versions (requires tox)
uv run tox

# Or test specific version
uv run tox -e py311
```

## Project Structure

```
src/pychrony/
├── __init__.py          # Package exports
├── _core/               # Future libchrony C bindings
│   ├── __init__.py
│   └── _bindings.py    # CFFI interface
└── _utils/               # Helper utilities
    ├── __init__.py
    └── helpers.py
```

## Contributing

1. Fork repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (`uv run pytest`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## License

This project is licensed under the MIT Licence - see the [LICENSE](LICENSE) file for details.

## Compatibility

- **Python**: 3.10, 3.11, 3.12, 3.13, 3.14
- **Platform**: Linux (primary), other platforms where libchrony is available
- **chrony**: Compatible with chrony 4.x and later

## Roadmap

- [ ] Complete CFFI binding implementation
- [ ] Add comprehensive chrony API coverage
- [ ] Integration tests with real chrony instances
- [ ] Documentation and examples
- [ ] Performance optimization

## Links

- [chrony](https://chrony.tuxfamily.org/) - NTP daemon
- [GitHub Repository](https://github.com/arunderwood/pychrony)
- [Issue Tracker](https://github.com/arunderwood/pychrony/issues)
