# Implementation Plan: Extend Bindings to Multiple Reports

**Branch**: `003-multiple-reports-bindings` | **Date**: 2026-01-16 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/003-multiple-reports-bindings/spec.md`

## Summary

Extend pychrony's libchrony bindings to support three additional chronyd reports: `sources` (NTP time sources), `sourcestats` (source statistics), and `rtcdata` (Real-Time Clock data). Implementation follows existing `get_tracking()` patterns using CFFI API mode bindings, frozen dataclasses, and the existing exception hierarchy.

## Technical Context

**Language/Version**: Python 3.10+ (supports 3.10, 3.11, 3.12, 3.13, 3.14) + CFFI
**Primary Dependencies**: libchrony (system library via CFFI API mode bindings)
**Storage**: N/A (read-only monitoring, no persistence)
**Testing**: pytest with unit tests (mocked CFFI), contract tests (API stability), integration tests (Docker with chronyd)
**Target Platform**: Linux (primary and only supported)
**Project Type**: Single Python package
**Performance Goals**: N/A (monitoring library, performance bounded by libchrony/chronyd)
**Constraints**: Read-only operations only; expose only what libchrony supports
**Scale/Scope**: Typically <50 sources per chronyd instance; support 100+ without truncation

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### pychrony Constitution Gates

**MUST PASS:**
- ✅ API scope limited to libchrony read-only capabilities — new functions only retrieve data, no control operations
- ✅ Implementation uses CFFI binding to system libchrony — extends existing `_bindings.py` with same patterns
- ✅ Full type hints and Pythonic interfaces — frozen dataclasses with complete type annotations
- ✅ Linux-first design with Linux CI — existing CI workflow, Docker-based integration tests
- ✅ Test coverage for all new features — unit, contract, and integration tests planned
- ✅ No vendoring or reimplementation of libchrony — uses system library via CFFI

## Project Structure

### Documentation (this feature)

```text
specs/003-multiple-reports-bindings/
├── plan.md              # This file
├── research.md          # Phase 0: libchrony report field names
├── data-model.md        # Phase 1: Source, SourceStats, RTCData dataclasses
├── quickstart.md        # Phase 1: Usage examples
├── contracts/           # Phase 1: Function signatures and return types
└── tasks.md             # Phase 2 output (created by /speckit.tasks)
```

### Source Code (repository root)

```text
src/pychrony/
├── __init__.py          # Add exports: get_sources, get_source_stats, get_rtc_data
├── models.py            # Add: Source, SourceStats, RTCData dataclasses
├── exceptions.py        # No changes (use existing ChronyDataError, etc.)
└── _core/
    ├── _bindings.py     # Add: get_sources(), get_source_stats(), get_rtc_data()
    └── _build_bindings.py  # No changes (CFFI build script)

tests/
├── unit/
│   ├── test_models.py       # Add: Source, SourceStats, RTCData tests
│   ├── test_bindings.py     # Add: new function tests with mocked CFFI
│   └── test_validation.py   # Add: validation tests for new report fields
├── contract/
│   └── test_api.py          # Add: API contract tests for new exports
└── integration/
    ├── test_sources.py      # New: integration tests for get_sources()
    ├── test_sourcestats.py  # New: integration tests for get_source_stats()
    └── test_rtc.py          # New: integration tests for get_rtc_data()
```

**Structure Decision**: Single Python package with existing layout. New code extends `_bindings.py` (following existing `get_tracking()` patterns), adds dataclasses to `models.py`, and adds corresponding tests to each test category.

## Complexity Tracking

No violations. Design follows existing patterns exactly:
- Same CFFI binding approach as `get_tracking()`
- Same frozen dataclass pattern as `TrackingStatus`
- Same exception hierarchy
- Same test structure
