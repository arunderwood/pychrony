# Implementation Plan: Protocol-Level Test Mock Infrastructure

**Branch**: `006-protocol-test-mocks` | **Date**: 2026-01-18 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/006-protocol-test-mocks/spec.md`

## Summary

Add a protocol-level mock layer for pychrony testing that simulates chronyd responses without requiring hardware (RTC), special system states (leap seconds), or running chronyd. The infrastructure will consist of configuration dataclasses (`ChronyStateConfig`, `SourceConfig`, `RTCConfig`) and a `MockChronySession` class that replaces the CFFI `_lib`/`_ffi` objects, enabling declarative test scenarios and error injection.

## Technical Context

**Language/Version**: Python 3.10+ (supports 3.10, 3.11, 3.12, 3.13, 3.14)
**Primary Dependencies**: CFFI (runtime), pytest (testing), standard library dataclasses and enum
**Storage**: N/A (test infrastructure, no persistence)
**Testing**: pytest with unit tests, no external dependencies required for mock tests
**Target Platform**: Linux (primary), any platform for test-only execution
**Project Type**: Single Python library package
**Performance Goals**: N/A (test infrastructure, deterministic behavior over speed)
**Constraints**: Must run without CFFI bindings compiled, without chronyd, deterministic (no timing dependencies)
**Scale/Scope**: Test-only infrastructure in `tests/` directory, 7 user stories covering RTC, leap seconds, REFCLOCK, multi-source, declarative config, error injection, sync states

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### pychrony Constitution Gates

**MUST PASS:**
- ✅ **API scope limited to libchrony read-only capabilities**: Mock infrastructure simulates read-only queries (tracking, sources, sourcestats, rtcdata) - no write operations
- ✅ **Implementation uses CFFI binding to system libchrony**: Mock replaces CFFI objects for testing only; production code unchanged and still uses real CFFI bindings
- ✅ **Full type hints and Pythonic interfaces**: All configuration dataclasses will have full type hints, mock classes will follow Python conventions
- ✅ **Linux-first design with Linux CI**: Mock infrastructure enables testing on any platform, expanding Linux CI coverage to previously untestable scenarios
- ✅ **Test coverage for all new features**: Mock infrastructure itself will be tested, and enables testing of previously uncoverable code paths
- ✅ **No vendoring or reimplementation of libchrony**: Mock simulates the CFFI interface, not libchrony itself - protocol behavior derived from existing `_bindings.py` patterns

**Constitution Compliance Notes:**
- The mock infrastructure lives primarily in `tests/` directory (test-only, not shipped)
- Production code gains `_fields.py` with field type registry - this benefits both production (cleaner _bindings.py) and testing (single source of truth for field names/types)
- Mock behavior mirrors what libchrony's high-level introspection API returns
- Field registry also positions pychrony for future pure Python client mode

## Project Structure

### Documentation (this feature)

```text
specs/006-protocol-test-mocks/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output (configuration dataclasses)
├── quickstart.md        # Phase 1 output (usage examples)
├── contracts/           # Phase 1 output (mock API contract)
└── tasks.md             # Phase 2 output (NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
src/
├── pychrony/
│   ├── __init__.py
│   ├── _core/
│   │   ├── __init__.py
│   │   ├── _bindings.py       # Existing CFFI bindings (refactored to use _fields.py)
│   │   ├── _build_bindings.py # Build script (unchanged)
│   │   └── _fields.py         # NEW: Field type registry for all report types
│   ├── models.py              # Existing dataclasses/enums (unchanged)
│   ├── exceptions.py          # Existing exceptions (unchanged)
│   └── testing.py             # Existing factory functions (unchanged)

tests/
├── conftest.py                # Existing pytest config
├── mocks/                     # NEW: Protocol-level mock infrastructure
│   ├── __init__.py
│   ├── config.py              # ChronyStateConfig, SourceConfig, RTCConfig dataclasses
│   ├── session.py             # MockChronySession class (mock _lib/_ffi)
│   ├── scenarios.py           # Pre-built scenario presets (SCENARIO_*)
│   └── context.py             # patched_chrony_connection context manager
├── contract/                  # Existing contract tests (unchanged)
├── integration/               # Existing integration tests (unchanged)
└── unit/                      # Existing + new unit tests
    ├── test_fields.py         # NEW: Tests for _fields.py field registries
    ├── test_mock_config.py    # NEW: Tests for config dataclasses
    ├── test_mock_session.py   # NEW: Tests for MockChronySession
    ├── test_mock_scenarios.py # NEW: Tests using pre-built scenarios
    ├── test_rtc_scenarios.py  # NEW: RTC testing (User Story 1)
    ├── test_leap_scenarios.py # NEW: Leap second testing (User Story 2)
    └── test_source_scenarios.py # NEW: REFCLOCK/multi-source (User Stories 3-4)
```

**Structure Decision**: Mock infrastructure placed in `tests/mocks/` package to keep test utilities separate from test cases. This follows the pattern of `pychrony.testing` being for factory functions (shipped) while `tests/mocks/` is for protocol-level simulation (not shipped).

## Complexity Tracking

> No constitution violations identified. The mock infrastructure:
> - Mock code stays within test directory (`tests/mocks/`)
> - Production code gains `_fields.py` field registry (Option C) - benefits both production (cleaner `_bindings.py`) and testing (single source of truth)
> - Simulates read-only operations only
> - Uses standard Python patterns (dataclasses, context managers)
> - Enables constitution-mandated test coverage for features that couldn't be tested before
