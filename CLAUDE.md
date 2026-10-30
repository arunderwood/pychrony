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

# Integration tests (require Docker; image builds libchrony from vendor/)
git submodule update --init --recursive   # vendor/libchrony must be populated
docker build -t pychrony-test -f docker/Dockerfile.test . && \
  docker run --rm --cap-add=SYS_TIME pychrony-test sh -c "chronyd && sleep 2 && pytest tests/integration -v"
```

Keep the `&&` joining build and run. `pychrony-test` is a fixed tag, so if the
build fails and `docker run` still executes, it silently reuses the last image
under that tag — possibly built from a different worktree or an older commit —
and reports a full pass. Confirm the pytest paths name the current worktree.

Never pipe the build through `tail`/`head` to trim output: the pipeline then
exits with the pager's status, which defeats the `&&` and reintroduces exactly
that stale-image failure.

Cross-version testing (Python 3.11-3.15) is handled by CI.

## Before Committing

Always run the test suite and all quality checks before creating a commit:
```bash
uv run pytest
uv run ruff check .
uv run ruff format .
uv run ty check src/
docker build -t pychrony-test -f docker/Dockerfile.test . && \
  docker run --rm --cap-add=SYS_TIME pychrony-test sh -c "chronyd && sleep 2 && pytest tests/integration -v"
```

A green integration run only counts if the build ahead of it succeeded — see the
stale-image note above.

## Architecture

- **Build**: setuptools + setuptools-scm (version from git tags); `setup.py` hooks in the CFFI build
- **CFFI bindings**: `src/pychrony/_core/_bindings.py` wraps libchrony; `ChronyConnection` context manager with `get_tracking()`, `get_sources()`, `get_source_stats()`, `get_rtc_data()`, and `address`/`transport` properties
- **Build script**: `src/pychrony/_core/_build_bindings.py` generates `_cffi_bindings*.so` at install time
- **Field registry**: `src/pychrony/_core/_fields.py` maps libchrony field names to `FieldType` per report (`TRACKING_FIELDS`, `SOURCE_FIELDS`, `SOURCESTATS_FIELDS`, `RTC_FIELDS`); shared by `_bindings.py` and `tests/mocks/`
- **Data models** (`models.py`): frozen dataclasses `TrackingStatus`, `Source`, `SourceStats`, `RTCData`; enums `LeapStatus`, `SourceState`, `SourceMode`, `Transport`
- **Exceptions** (`exceptions.py`): `ChronyError` base with `ChronyConnectionError`, `ChronyPermissionError`, `ChronyDataError`, `ChronyLibraryError`
- **Testing utilities** (`testing.py`): `make_tracking()`/`make_source()`/`make_source_stats()`/`make_rtc_data()` factories and pytest fixtures, registered as a `pytest11` plugin
- **libchrony reference**: `vendor/libchrony/` - submodule with API source (field definitions in `reports.h`)

## Testing Structure

- **Unit tests** (`tests/unit/`): No external dependencies, mock CFFI bindings
- **Protocol mocks** (`tests/mocks/`): Simulated libchrony sessions and scenarios used by unit tests
- **Contract tests** (`tests/contract/`): API stability verification
- **Integration tests** (`tests/integration/`): Require Docker with running chronyd

## Notes

- ty configured to ignore `possibly-missing-attribute` in `_bindings.py` (dynamic CFFI imports)
- This is a read-only monitoring library; it does not control chronyd

## Stack

- CFFI (API mode) over libchrony; pre-built wheels bundle libchrony
- Standard library dataclasses and `Enum` for the data models
- setuptools + setuptools-scm build; cibuildwheel manylinux wheels in CI
- Release via Trusted Publishers (OIDC): Test PyPI, then PyPI
