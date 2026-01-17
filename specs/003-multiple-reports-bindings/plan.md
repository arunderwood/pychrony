# Implementation Plan: Extend Bindings to Multiple Reports

**Branch**: `003-multiple-reports-bindings` | **Date**: 2026-01-16 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/003-multiple-reports-bindings/spec.md`

## Summary

Extend pychrony's CFFI bindings to support three additional libchrony reports: sources, sourcestats, and rtcdata. Following the established pattern from `get_tracking()`, implement `get_sources()`, `get_source_stats()`, and `get_rtc_data()` functions that return frozen dataclasses with full type annotations. All functions use libchrony's field introspection API for ABI stability.

## Technical Context

**Language/Version**: Python 3.10+ (supports 3.10, 3.11, 3.12, 3.13, 3.14)
**Primary Dependencies**: CFFI + libchrony (system library via CFFI API mode bindings)
**Storage**: N/A (read-only monitoring, no persistence)
**Testing**: pytest with unit/contract/integration test hierarchy
**Target Platform**: Linux (primary), other platforms if libchrony available
**Project Type**: Single Python package
**Performance Goals**: Minimal overhead per report query (<10ms typical)
**Constraints**: Read-only access only; no modification of chronyd state
**Scale/Scope**: Monitor chronyd instances with up to 100+ NTP sources

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### pychrony Constitution Gates

**MUST PASS:**
- ✅ API scope limited to libchrony read-only capabilities (sources/sourcestats/rtcdata are read-only reports)
- ✅ Implementation uses CFFI binding to system libchrony (follows existing API mode pattern)
- ✅ Full type hints and Pythonic interfaces (frozen dataclasses with annotations)
- ✅ Linux-first design with Linux CI (Docker-based integration tests)
- ✅ Test coverage for all new features (unit, contract, integration tests planned)
- ✅ No vendoring or reimplementation of libchrony (direct bindings only)

**All gates pass. Proceeding to Phase 0.**

## Project Structure

### Documentation (this feature)

```text
specs/003-multiple-reports-bindings/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
└── tasks.md             # Phase 2 output (via /speckit.tasks)
```

### Source Code (repository root)

```text
src/pychrony/
├── __init__.py          # Public API exports (add new functions/classes)
├── models.py            # Dataclasses (add Source, SourceStats, RTCData)
├── exceptions.py        # Exception hierarchy (no changes needed)
└── _core/
    ├── _bindings.py     # CFFI wrapper (add new functions)
    └── _build_bindings.py  # Build script (no changes expected)

tests/
├── conftest.py          # Fixtures (add sample data for new types)
├── unit/
│   ├── test_models.py   # Add Source, SourceStats, RTCData tests
│   ├── test_bindings.py # Add extraction/validation tests
│   └── test_validation.py  # Add validation tests for new types
├── contract/
│   └── test_api.py      # Add new public API contract tests
└── integration/
    ├── test_sources.py      # New: get_sources() integration
    ├── test_sourcestats.py  # New: get_source_stats() integration
    └── test_rtcdata.py      # New: get_rtc_data() integration
```

**Structure Decision**: Single Python package structure matching existing codebase. New code extends existing modules rather than creating new directories.

## Complexity Tracking

No constitution violations identified. Standard extension of existing patterns.

## Post-Design Constitution Re-Check

*Evaluated after Phase 1 design completion.*

### pychrony Constitution Gates (Post-Design)

**VERIFIED PASS:**
- ✅ **API scope limited to libchrony read-only capabilities**
  - Design uses only `sources`, `sourcestats`, `rtcdata` reports (all read-only)
  - No control operations added
  - Data models are read-only frozen dataclasses

- ✅ **Implementation uses CFFI binding to system libchrony**
  - Uses existing CFFI API mode infrastructure
  - Uses `chrony_get_field_*` introspection functions
  - No direct struct access or protocol implementation

- ✅ **Full type hints and Pythonic interfaces**
  - All dataclasses have complete type annotations
  - All functions have typed parameters and return types
  - Helper methods follow Python conventions (snake_case, properties)

- ✅ **Linux-first design with Linux CI**
  - Integration tests run in Docker with chronyd
  - Socket path defaults work on Linux systems
  - No Windows/macOS-specific code

- ✅ **Test coverage for all new features**
  - Unit tests for dataclasses and validation
  - Contract tests for public API
  - Integration tests for real chronyd interaction

- ✅ **No vendoring or reimplementation of libchrony**
  - Pure binding layer, no protocol reimplementation
  - Field names discovered via introspection API
  - No hardcoded wire formats

**All gates verified. Ready for Phase 2 task generation.**

## Generated Artifacts

| Artifact | Path | Status |
|----------|------|--------|
| Implementation Plan | `specs/003-multiple-reports-bindings/plan.md` | ✅ Complete |
| Research | `specs/003-multiple-reports-bindings/research.md` | ✅ Complete |
| Data Model | `specs/003-multiple-reports-bindings/data-model.md` | ✅ Complete |
| API Contract | `specs/003-multiple-reports-bindings/contracts/python-api.md` | ✅ Complete |
| Quickstart | `specs/003-multiple-reports-bindings/quickstart.md` | ✅ Complete |

## Next Steps

Run `/speckit.tasks` to generate the implementation task list from this plan.
