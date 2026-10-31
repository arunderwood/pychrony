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
uv build                                   # build sdist and wheel in dist/ (the wheel needs libchrony)
uv pip install cibuildwheel               # install cibuildwheel for manylinux builds
cibuildwheel --platform linux             # build manylinux wheels (requires Docker)
                                          # output in wheelhouse/

# Integration tests (require Docker; image builds libchrony from vendor/)
git submodule update --init --recursive   # vendor/libchrony must be populated
docker build -t pychrony-test -f docker/Dockerfile.test . && \
  docker run --rm --cap-add=SYS_TIME pychrony-test sh -c "chronyd && sleep 2 && pytest tests/integration -v"

# Same suite against a built wheel instead of the source tree (wheelhouse/
# must hold a wheel for the image's python3, Fedora 44's 3.14; the cp311 abi3
# wheel covers it). CI runs the source variant per PR; release.yml runs this
# against the shipped wheels.
CIBW_BUILD=cp311-manylinux_x86_64 cibuildwheel --platform linux && \
  docker build -t pychrony-test -f docker/Dockerfile.test \
    --build-arg PYCHRONY_INSTALL=wheel --build-context wheelhouse=wheelhouse/ . && \
  docker run --rm --cap-add=SYS_TIME pychrony-test sh -c "chronyd && sleep 2 && pytest tests/integration -v"
```

The image installs test dependencies from `uv.lock` and installs pychrony
non-editably (source builds compile the bindings via `PYCHRONY_BUILD_CFFI=1`),
so tests import the installed package, never `src/`.

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
- **setup.py** compiles the bindings by default and fails with a clear message without libchrony (found via pkg-config, else default compiler paths). `PYCHRONY_SKIP_CFFI=1` skips them; `[tool.uv]` sets it for `uv sync`/`uv pip`, so dev and the CI test/lint/docs jobs need no libchrony (unit/contract tests mock the bindings). `uv build` ignores it. `PYCHRONY_BUILD_CFFI=1` or `CIBUILDWHEEL=1` overrides it: `docker/Dockerfile.test` depends on that, and `PYCHRONY_BUILD_CFFI=1 uv sync` builds them locally (`cache-keys` triggers the rebuild). Tests: `tests/unit/test_setup.py`.
- **Field registry**: `src/pychrony/_core/_fields.py` maps libchrony field names to `FieldType` per report (`TRACKING_FIELDS`, `SOURCE_FIELDS`, `SOURCESTATS_FIELDS`, `RTC_FIELDS`); shared by `_bindings.py` and `tests/mocks/`
- **Data models** (`models.py`): frozen dataclasses `TrackingStatus`, `Source`, `SourceStats`, `RTCData`; enums `LeapStatus`, `SourceState`, `SourceMode`, `Transport`
- **Exceptions** (`exceptions.py`): `ChronyError` base with `ChronyConnectionError`, `ChronyPermissionError`, `ChronyDataError`, `ChronyLibraryError`
- **Testing utilities** (`testing.py`): `make_tracking()`/`make_source()`/`make_source_stats()`/`make_rtc_data()` factories; no pytest import
- **Pytest plugin** (`pytest_plugin.py`): opt-in `chrony_*` fixtures, enabled with `pytest_plugins = ["pychrony.pytest_plugin"]` (no `pytest11` entry point)
- **libchrony reference**: `vendor/libchrony/` - submodule with API source (field definitions in `reports.h`)

## Testing Structure

- **Unit tests** (`tests/unit/`): No external dependencies, mock CFFI bindings
- **Protocol mocks** (`tests/mocks/`): Simulated libchrony sessions and scenarios used by unit tests
- **Contract tests** (`tests/contract/`): API stability verification
- **Integration tests** (`tests/integration/`): Require Docker with running chronyd

## Notes

- `_core/_cffi_bindings.pyi` types the compiled CFFI module for ty; keep it in step with the cdef in `_build_bindings.py` (checked by `tests/unit/test_cffi_stub.py`)
- This is a read-only monitoring library; it does not control chronyd

## Stack

- CFFI (API mode) over libchrony; pre-built wheels bundle libchrony
- Standard library dataclasses and `Enum` for the data models
- setuptools + setuptools-scm build; cibuildwheel builds one `cp311-abi3` wheel per
  platform (manylinux/musllinux × x86_64/aarch64) plus free-threaded `cp314t`/`cp315t`
- Release via Trusted Publishers (OIDC): Test PyPI, then PyPI
