# Implementation Plan: PyPI Packaging and Distribution

**Branch**: `005-pypi-packaging` | **Date**: 2026-01-16 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/005-pypi-packaging/spec.md`

## Summary

Configure pychrony for PyPI distribution with automated CI/CD release workflows. Build manylinux-compatible wheels for Linux x86_64 and arm64 architectures using cibuildwheel. Implement two-stage publishing (Test PyPI → Production PyPI) with Trusted Publishers (OIDC) authentication for secure, token-free releases.

## Technical Context

**Language/Version**: Python 3.10+ (supports 3.10, 3.11, 3.12, 3.13, 3.14)
**Primary Dependencies**: hatchling (build), hatch-vcs (versioning), cffi (runtime), cibuildwheel (CI wheel builds)
**Storage**: N/A (library package, no persistence)
**Testing**: pytest with unit/contract/integration test structure
**Target Platform**: Linux (manylinux x86_64 and arm64)
**Project Type**: Single library package
**Performance Goals**: Wheel build + publish pipeline completes in <15 minutes
**Constraints**: libchrony must be installed on target system; wheel does not bundle it
**Scale/Scope**: Single Python package, ~6 source files, ~18 test files

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### pychrony Constitution Gates

**MUST PASS:**
- ✅ API scope limited to libchrony read-only capabilities (packaging does not change API)
- ✅ Implementation uses CFFI binding to system libchrony (existing, unchanged)
- ✅ Full type hints and Pythonic interfaces (existing, unchanged)
- ✅ Linux-first design with Linux CI (manylinux wheels, GitHub Actions)
- ✅ Test coverage for all new features (wheel tests via cibuildwheel test command)
- ✅ No vendoring or reimplementation of libchrony (libchrony remains system dependency)

## Project Structure

### Documentation (this feature)

```text
specs/005-pypi-packaging/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output (N/A - no data model changes)
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output (N/A - no API contracts)
└── tasks.md             # Phase 2 output (/speckit.tasks command)
```

### Source Code (repository root)

```text
src/pychrony/
├── __init__.py          # Package entry point, exports
├── models.py            # Data models (TrackingStatus, etc.)
├── exceptions.py        # Exception classes
└── _core/
    ├── __init__.py
    ├── _bindings.py     # CFFI bindings to libchrony
    └── _build_bindings.py  # CFFI build script

tests/
├── conftest.py
├── test_import.py
├── contract/            # API stability tests
├── integration/         # Tests requiring chronyd
└── unit/                # Isolated unit tests

.github/workflows/
├── ci.yml               # Existing CI (lint, type-check, test)
├── release.yml          # NEW: Build wheels, publish to Test PyPI
└── publish.yml          # NEW: Promote to production PyPI
```

**Structure Decision**: Existing single-project structure is maintained. New GitHub Actions workflows added for release automation. No changes to source code structure.

## Complexity Tracking

> No constitution violations. Feature is purely CI/CD and packaging configuration.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| (none)    | N/A        | N/A                                 |
