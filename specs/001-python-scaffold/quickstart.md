# PyChrony Development Quickstart

## Setup Instructions

### Prerequisites
- Python 3.10+ installed
- UV package manager installed
- Git for version control
- libchrony development library (for local testing)

### Initial Setup

```bash
# Clone repository
git clone https://github.com/arunderwood/pychrony.git
cd pychrony

# Install UV (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.bashrc  # or restart shell

# Setup development environment
uv venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install all dependencies (development + optional)
uv sync --all-groups
```

### Development Workflow

```bash
# Format code
uv run ruff format .

# Check linting
uv run ruff check .

# Type checking
uv run ty src/

# Run tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=src --cov-report=html

# Build package
uv build

# Install locally for testing
uv pip install dist/pychrony-*.whl --force-reinstall
```

### Testing Commands

```bash
# Run specific test file
uv run pytest tests/test_import.py -v

# Run with specific markers
uv run pytest -m "unit"          # Unit tests only
uv run pytest -m "integration"     # Integration tests only
uv run pytest -m "not slow"         # Skip slow tests

# Run with coverage
uv run pytest --cov=src --cov-report=term-missing

# Generate coverage report
uv run pytest --cov=src --cov-report=html
open htmlcov/index.html
```

### Environment Management

```bash
# Add new dependency
uv add requests

# Add development dependency
uv add --group dev pytest-xdist

# Remove dependency
uv remove requests

# Update all dependencies
uv lock --upgrade

# Clean environment
uv cache clean
```

### Git Workflow

```bash
# Feature branch workflow
git checkout -b feature/new-binding
# ... make changes ...
uv run pytest  # Ensure tests pass
git add .
git commit -m "Add new binding feature"
git push origin feature/new-binding

# Main branch update
git checkout main
git pull origin main
git merge feature/new-binding
git push origin main
```

## Project Structure

```
pychrony/
├── pyproject.toml          # Project configuration
├── README.md               # Documentation
├── LICENSE                  # GPL-2.0+ license
├── .gitignore              # Git ignore patterns
├── .python-version           # Python version for UV
├── uv.lock                 # Dependency lock file
├── src/
│   └── pychrony/
│       ├── __init__.py       # Package exports
│       ├── __about__.py       # Version info
│       ├── _core/            # Future C bindings
│       │   ├── __init__.py
│       │   └── _bindings.py   # CFFI interface
│       └── _utils/           # Helper utilities
│           ├── __init__.py
│           └── helpers.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py          # Pytest configuration
│   ├── test_import.py        # Import validation
│   └── test_*.py           # Additional tests
└── docs/
    └── conf.py             # Future Sphinx config
```

## Key Commands Reference

| Command | Purpose | Example |
|---------|---------|---------|
| Format code | Auto-format Python code | `uv run ruff format .` |
| Lint check | Find style/issues | `uv run ruff check .` |
| Type check | Verify type hints | `uv run ty src/` |
| Run tests | Execute test suite | `uv run pytest` |
| Coverage | Test coverage report | `uv run pytest --cov=src` |
| Build | Create package | `uv build` |
| Install local | Test package | `uv pip install dist/*.whl` |

## Getting Help

```bash
# Get help for any command
uv run --help pytest
uv run ruff --help
uv --help

# Check available scripts
uv run --list
```

This quickstart provides the essential workflow for contributors to get started with the pychrony project development environment.