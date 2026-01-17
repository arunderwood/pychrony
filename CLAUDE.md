# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Testing
uv run pytest                              # run all tests
uv run pytest tests/unit -v                # run unit tests only
uv run pytest tests/contract -v            # run contract tests
uv run pytest tests/path/to/test.py -v     # run specific test file
uv run pytest tests/unit/test_models.py::test_name -v  # run single test
uv run pytest --cov=src --cov-report=html  # with coverage

# Code quality
uv run ruff check .                        # lint
uv run ruff format .                       # format
uv run ty check src/                       # type check

# Building wheels
uv build                                   # build sdist and wheel in dist/
uv pip install cibuildwheel               # install cibuildwheel for manylinux builds
cibuildwheel --platform linux             # build manylinux wheels (requires Docker)
                                          # output in wheelhouse/

# Integration tests (require Docker with libchrony)
docker build -t pychrony-test -f docker/Dockerfile.test .
docker run --rm --cap-add=SYS_TIME pychrony-test sh -c "chronyd && sleep 2 && pytest tests/integration -v"
```

Cross-version testing (Python 3.10-3.14) is handled by CI.

## Before Committing

Always run the test suite and all quality checks before creating a commit:
```bash
uv run pytest
uv run ruff check .
uv run ruff format .
uv run ty check src/
docker build -t pychrony-test -f docker/Dockerfile.test .
docker run --rm --cap-add=SYS_TIME pychrony-test sh -c "chronyd && sleep 2 && pytest tests/integration -v"
```

## Architecture

- **CFFI bindings**: `src/pychrony/_core/_bindings.py` wraps libchrony C library
- **Build script**: `src/pychrony/_core/_build_bindings.py` generates `_cffi_bindings*.so` at install time
- **Data model**: `TrackingStatus` frozen dataclass in `models.py` (15 NTP tracking fields)
- **Exceptions**: `ChronyError` base with 4 specific subclasses in `exceptions.py`
- **libchrony reference**: `vendor/libchrony/` - submodule with API source (field definitions in `reports.h`)

## Testing Structure

- **Unit tests** (`tests/unit/`): No external dependencies, mock CFFI bindings
- **Contract tests** (`tests/contract/`): API stability verification
- **Integration tests** (`tests/integration/`): Require Docker with running chronyd

## Notes

- ty configured to ignore `possibly-missing-attribute` in `_bindings.py` (dynamic CFFI imports)
- This is a read-only monitoring library; it does not control chronyd

## Active Technologies
- Python 3.10+ (supports 3.10, 3.11, 3.12, 3.13, 3.14) + CFFI (API mode) + libchrony (system library) (003-multiple-reports-bindings)
- N/A (read-only monitoring, no persistence) (003-multiple-reports-bindings)
- Python 3.10+ (supports 3.10, 3.11, 3.12, 3.13, 3.14) + CFFI (API mode), libchrony (system library), standard library Enum (004-categorical-enums)
- Python 3.10+ (supports 3.10, 3.11, 3.12, 3.13, 3.14) + hatchling (build), hatch-vcs (versioning), cffi (runtime), cibuildwheel (CI wheel builds) (005-pypi-packaging)
- N/A (library package, no persistence) (005-pypi-packaging)

## Recent Changes
- 005-pypi-packaging: Added PyPI packaging with cibuildwheel (manylinux_2_28), Trusted Publishers (OIDC), two-stage release workflow (Test PyPI → Production PyPI)
- 004-categorical-enums: Added standard library Enum for categorical fields (LeapStatus, SourceState, SourceMode)
- 003-multiple-reports-bindings: Added Python 3.10+ (supports 3.10, 3.11, 3.12, 3.13, 3.14) + CFFI + libchrony (system library via CFFI API mode bindings)
