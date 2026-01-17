# Implementation Plan: Extend Bindings to Multiple Reports

**Branch**: `003-multiple-reports-bindings` | **Date**: 2026-01-16 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/003-multiple-reports-bindings/spec.md`

## Summary

Extend pychrony with three new functions (`get_sources()`, `get_source_stats()`, `get_rtc_data()`) to expose additional chronyd reports via libchrony's introspection API. Implementation follows the existing `get_tracking()` pattern using CFFI API mode bindings, field introspection for ABI stability, and frozen dataclasses for return types.

## Technical Context

**Language/Version**: Python 3.10+ (supports 3.10, 3.11, 3.12, 3.13, 3.14)
**Primary Dependencies**: CFFI (API mode), libchrony (system library via CFFI bindings)
**Storage**: N/A (read-only monitoring, no persistence)
**Testing**: pytest (unit, contract, integration in Docker)
**Target Platform**: Linux (primary), other platforms if libchrony available
**Project Type**: Single Python package
**Performance Goals**: N/A (simple synchronous API calls)
**Constraints**: Must use libchrony introspection API, no direct struct access
**Scale/Scope**: 3 new public functions, 3 new dataclasses, matching existing patterns

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### pychrony Constitution Gates

**MUST PASS:**
- ✅ API scope limited to libchrony read-only capabilities (sources, sourcestats, rtcdata are read-only reports)
- ✅ Implementation uses CFFI binding to system libchrony (CFFI API mode with ffi.set_source)
- ✅ Full type hints and Pythonic interfaces (frozen dataclasses, Optional[str] parameters)
- ✅ Linux-first design with Linux CI (Docker integration tests)
- ✅ Test coverage for all new features (unit, contract, integration tests planned)
- ✅ No vendoring or reimplementation of libchrony (uses system libchrony via introspection API)

**Post-Design Re-check:**
- ✅ Data model verified against libchrony source (client.c)
- ✅ Field names match libchrony's introspection API exactly
- ✅ API follows existing get_tracking() pattern

## Project Structure

### Documentation (this feature)

```text
specs/003-multiple-reports-bindings/
├── plan.md              # This file
├── research.md          # Phase 0 output (complete)
├── data-model.md        # Phase 1 output (complete)
├── quickstart.md        # Phase 1 output (complete)
├── contracts/           # Phase 1 output (complete)
│   ├── api.md
│   └── python-api.md
└── tasks.md             # Phase 2 output (complete)
```

### Source Code (repository root)

```text
src/pychrony/
├── __init__.py          # Public exports (add new functions/classes)
├── models.py            # Dataclasses (add Source, SourceStats, RTCData)
├── exceptions.py        # Exception hierarchy (no changes needed)
└── _core/
    ├── __init__.py
    ├── _bindings.py     # CFFI bindings (add new functions)
    └── _build_bindings.py

tests/
├── unit/
│   ├── test_models.py   # Dataclass tests (add new tests)
│   ├── test_bindings.py # Binding tests (add new tests)
│   └── test_validation.py # Validation tests (new file)
├── contract/
│   └── test_api.py      # API contract tests (add new tests)
└── integration/
    ├── test_sources.py      # New: get_sources() tests
    ├── test_sourcestats.py  # New: get_source_stats() tests
    └── test_rtcdata.py      # New: get_rtc_data() tests
```

**Structure Decision**: Extends existing single-package structure. New code integrates into existing files (models.py, _bindings.py, __init__.py) following established patterns. New integration test files for each report type.

## Complexity Tracking

> No complexity violations. Implementation follows established patterns.

| Aspect | Approach | Justification |
|--------|----------|---------------|
| Field access | libchrony introspection API | ABI stability per constitution |
| Data structures | Frozen dataclasses | Matches existing TrackingStatus pattern |
| Multi-record handling | Loop with chrony_request_record() | libchrony's designed usage pattern |

## Phase Outputs

### Phase 0: Research (Complete)

- **Output**: [research.md](./research.md)
- **Key decisions**:
  - Use field introspection API for ABI stability
  - Report names: "sources", "sourcestats", "rtcdata"
  - All field names verified against libchrony client.c source
  - Multi-record reports use request_record() loop pattern

### Phase 1: Design (Complete)

- **Data Model**: [data-model.md](./data-model.md)
  - Source: 11 fields (address, poll, stratum, state, mode, flags, reachability, last_sample_ago, orig_latest_meas, latest_meas, latest_meas_err)
  - SourceStats: 10 fields (reference_id, address, samples, runs, span, std_dev, resid_freq, skew, offset, offset_err)
  - RTCData: 6 fields (ref_time, samples, runs, span, offset, freq_offset)

- **Contracts**: [contracts/](./contracts/)
  - python-api.md: Function signatures, dataclass definitions
  - api.md: Public API documentation

- **Quickstart**: [quickstart.md](./quickstart.md)
  - Usage examples for all three new functions
  - Error handling patterns
  - Field correlation examples

### Phase 2: Tasks (Complete)

- **Output**: [tasks.md](./tasks.md)
- **Summary**: 63 tasks across 7 phases
- **MVP**: User Story 1 (get_sources) - 22 tasks total
