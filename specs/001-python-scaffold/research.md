# Research Findings

## pyproject.toml Structure and Build System

### Decision: Use hatchling build backend
**Rationale**: Modern Python packaging standard with excellent UV integration, faster than setuptools, and follows PEP 621. The hatchling ecosystem is actively maintained and provides better dependency management.

**Alternatives considered**: 
- setuptools (traditional but slower, more complex configuration)
- poetry (good but UV is better integrated with our toolchain)

### Complete Configuration Structure
```toml
[build-system]
requires = ["hatchling>=1.24.2", "hatch-vcs>=0.3"]
build-backend = "hatchling.build"

[project]
name = "pychrony"
version = "0.1.0"  # dynamic from version control
description = "Python bindings for chrony NTP client"
readme = "README.md"
license = {text = "GPL-2.0+"}
requires-python = ">=3.10"
authors = [
    {name = "arunderwood", email = "arunderwood@users.noreply.github.com"}
]
classifiers = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "Intended Audience :: System Administrators",
    "License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11", 
    "Programming Language :: Python :: 3.12",
    "Programming Language :: Python :: 3.13",
    "Programming Language :: Python :: 3.14",
    "Topic :: System :: Networking :: Time Synchronization",
    "Topic :: Software Development :: Libraries :: Python Modules",
    "Operating System :: POSIX :: Linux",
]
dependencies = [
    # Future libchrony C library binding
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-cov>=4.0.0",
    "ruff>=0.8.0",
    "ty>=0.1.0",
    "tox>=4.0.0",
]
docs = [
    "sphinx>=7.0.0",
]

[project.urls]
Homepage = "https://github.com/arunderwood/pychrony"
Repository = "https://github.com/arunderwood/pychrony.git"
Issues = "https://github.com/arunderwood/pychrony/issues"

[tool.hatch.version]
source = "vcs"

[tool.hatch.build.targets.wheel]
packages = ["src/pychrony"]

# Modern Python development toolchain
[tool.ruff]
line-length = 88
target-version = "py310"

[tool.ty]
# Future C library binding configuration
```

## UV Package Manager Integration

### Decision: Use UV for all dependency and environment management
**Rationale**: 10-100x faster than pip, Rust-based performance, excellent caching, and seamless integration with modern Python toolchain.

**Key Features**:
- `uv sync --all-groups` for development setup
- `uv run pytest` for test execution
- `uv run ruff` for linting
- `uv run ty` for type checking
- `uv build` for package creation

## GitHub Actions CI/CD Best Practices

### Decision: Use UV-based workflow with fail-fast matrix
**Rationale**: UV integration in GitHub Actions is native, fast, and provides consistent environment across Python versions.

**Workflow Structure**:
- Python version matrix: 3.10, 3.11, 3.12, 3.13, 3.14
- Ubuntu runners for Linux-first design
- fail-fast: true (any version failure = build failure)
- Coverage reporting to Codecov
- Automated publishing on main branch pushes

## Python Package Layout

### Decision: Standard src layout with clear separation
**Rationale**: Follows Python packaging standards, clear separation of concerns, and compatible with hatchling build system.

**Structure**:
```
src/pychrony/
├── __init__.py          # Package exports and metadata
├── __about__.py          # Version and author info
├── _core/               # Future libchrony C bindings
│   ├── __init__.py
│   └── _bindings.py    # CFFI interface
└── _utils/               # Helper utilities
    ├── __init__.py
    └── helpers.py
```

## CFFI Binding Strategy

### Decision: Use CFFI for libchrony binding
**Rationale**: CFFI is recommended standard for C library bindings, excellent PyPy performance, cleaner API design than ctypes, and mature ecosystem.

**Implementation Pattern**:
- API mode for better error handling
- Dynamic library loading with fallback paths
- Proper memory management with `ffi.gc()`
- Platform-specific error handling
- Zero-copy operations for performance

**Alternatives considered**:
- ctypes (standard library, but slower and more complex)
- Cython (great performance but requires C-level expertise)
- pybind11 (best for C++, overkill for C library)

## Testing Infrastructure

### Decision: pytest + tox for comprehensive testing
**Rationale**: pytest is industry standard with excellent ecosystem, tox provides cross-Python-version testing, both integrate well with UV.

**Test Categories**:
- Unit tests for individual functions
- Integration tests for C library interaction
- Property-based testing with hypothesis
- Coverage reporting with pytest-cov
- Mock testing for C library in unit tests

## Quality Standards Compliance

### All Constitution Gates PASS:
✅ API scope limited to libchrony read-only capabilities
✅ Implementation uses CFFI binding to system libchrony  
✅ Full type hints and Pythonic interfaces
✅ Linux-first design with Linux CI
✅ Test coverage for all new features
✅ No vendoring or reimplementation of libchrony
✅ UV as package manager
✅ Modern toolchain (ruff, ty, pytest)
