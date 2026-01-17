# Implementation Plan: Python Enums for Categorical Fields

**Branch**: `004-categorical-enums` | **Date**: 2026-01-16 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/004-categorical-enums/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Add Python Enum classes (LeapStatus, SourceState, SourceMode) to replace integer constants in TrackingStatus and Source dataclasses. This provides type safety, IDE autocomplete, and self-documenting code.

## Technical Context

**Language/Version**: Python 3.10+ (supports 3.10, 3.11, 3.12, 3.13, 3.14)
**Primary Dependencies**: CFFI (API mode), libchrony (system library), standard library Enum
**Storage**: N/A (read-only monitoring library)
**Testing**: pytest, with unit/contract/integration test structure
**Target Platform**: Linux-first (requires libchrony)
**Project Type**: Single project (Python library)
**Performance Goals**: N/A (enum instantiation is negligible overhead)
**Constraints**: None (no backward compatibility required, pre-1.0)
**Scale/Scope**: 3 new enum classes, 2 dataclass field type changes, 2 property removals

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### pychrony Constitution Gates

**MUST PASS:**
- ✅ API scope limited to libchrony read-only capabilities
  - Enums are presentation layer only; data values come from libchrony
- ✅ Implementation uses CFFI binding to system libchrony
  - No CFFI changes required; enums wrap existing integer values
- ✅ Full type hints and Pythonic interfaces
  - Enum provides type safety and Pythonic semantics
- ✅ Linux-first design with Linux CI
  - No platform-specific code; pure Python enum definitions
- ✅ Test coverage for all new features
  - Unit tests for enum instantiation, comparison, and error handling
  - Contract tests for field type verification
  - Integration tests for end-to-end enum values from chronyd
- ✅ No vendoring or reimplementation of libchrony
  - Enums only interpret values; no libchrony code duplicated

**All gates pass. Proceeding to Phase 0.**

## Project Structure

### Documentation (this feature)

```text
specs/004-categorical-enums/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
src/pychrony/
├── __init__.py          # Package exports (add enum exports)
├── models.py            # Dataclasses + enums (add Enum classes)
├── exceptions.py        # Exception hierarchy (no changes)
└── _core/
    ├── __init__.py
    ├── _bindings.py     # CFFI bindings (update to use enums)
    └── _build_bindings.py

tests/
├── unit/                # Enum unit tests
├── contract/            # API stability tests
└── integration/         # End-to-end tests with chronyd
```

**Structure Decision**: Single Python library project. Enums defined in `models.py` alongside dataclasses. CFFI bindings in `_core/_bindings.py` convert integers to enums during dataclass construction.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No violations. All gates pass.
