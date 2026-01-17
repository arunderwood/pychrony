# Tasks: Multiple Reports Bindings

**Input**: Design documents from `/specs/003-multiple-reports-bindings/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Tests are included as this is a library requiring contract and integration test coverage.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

---

## Phase 1: Setup

**Purpose**: No new setup required - this feature extends existing pychrony infrastructure

This feature builds on the existing pychrony project structure:
- CFFI bindings infrastructure exists in `src/pychrony/_core/_bindings.py`
- Data models pattern exists in `src/pychrony/models.py`
- Exception hierarchy exists in `src/pychrony/exceptions.py`
- Test structure exists in `tests/unit/`, `tests/contract/`, `tests/integration/`

**Checkpoint**: Setup phase is already complete from initial project setup

---

## Phase 2: Foundational (Shared Validation Infrastructure)

**Purpose**: Create reusable validation functions that all three new report types will use

**⚠️ CRITICAL**: Validation infrastructure must be complete before any user story implementation

- [ ] T001 Add validation helper `_validate_finite_float()` in src/pychrony/_core/_bindings.py
- [ ] T002 Add validation helper `_validate_bounded_int()` in src/pychrony/_core/_bindings.py
- [ ] T003 Add validation helper `_validate_non_negative_int()` in src/pychrony/_core/_bindings.py

**Checkpoint**: Validation infrastructure ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Query Time Sources (Priority: P1) 🎯 MVP

**Goal**: Provide `get_sources()` function to retrieve all configured time sources from chronyd

**Independent Test**: Call `get_sources()` and verify it returns a list of Source objects with address, state, stratum, and polling information

### Tests for User Story 1

- [ ] T004 [P] [US1] Contract test for Source dataclass in tests/contract/test_api.py
- [ ] T005 [P] [US1] Contract test for get_sources() signature in tests/contract/test_api.py
- [ ] T006 [P] [US1] Unit test for Source dataclass creation in tests/unit/test_models.py
- [ ] T007 [P] [US1] Unit test for Source.is_reachable() method in tests/unit/test_models.py
- [ ] T008 [P] [US1] Unit test for Source.is_selected() method in tests/unit/test_models.py
- [ ] T009 [P] [US1] Unit test for Source.mode_name property in tests/unit/test_models.py
- [ ] T010 [P] [US1] Unit test for Source.state_name property in tests/unit/test_models.py
- [ ] T011 [P] [US1] Unit test for _validate_source() function in tests/unit/test_validation.py
- [ ] T012 [P] [US1] Integration test for get_sources() in tests/integration/test_sources.py

### Implementation for User Story 1

- [ ] T013 [US1] Create Source frozen dataclass in src/pychrony/models.py
- [ ] T014 [US1] Add is_reachable() method to Source in src/pychrony/models.py
- [ ] T015 [US1] Add is_selected() method to Source in src/pychrony/models.py
- [ ] T016 [US1] Add mode_name property to Source in src/pychrony/models.py
- [ ] T017 [US1] Add state_name property to Source in src/pychrony/models.py
- [ ] T018 [US1] Add _validate_source() validation function in src/pychrony/_core/_bindings.py
- [ ] T019 [US1] Add _get_source_from_record() helper to extract Source from libchrony record in src/pychrony/_core/_bindings.py
- [ ] T020 [US1] Implement get_sources() function in src/pychrony/_core/_bindings.py
- [ ] T021 [US1] Export Source from src/pychrony/models.py __all__
- [ ] T022 [US1] Export get_sources and Source from src/pychrony/__init__.py

**Checkpoint**: User Story 1 complete - `get_sources()` is functional and testable independently

---

## Phase 4: User Story 2 - Retrieve Source Statistics (Priority: P2)

**Goal**: Provide `get_source_stats()` function to retrieve statistical data for each time source

**Independent Test**: Call `get_source_stats()` and verify it returns a list of SourceStats objects with samples, offset, std_dev, and other statistical fields

### Tests for User Story 2

- [ ] T023 [P] [US2] Contract test for SourceStats dataclass in tests/contract/test_api.py
- [ ] T024 [P] [US2] Contract test for get_source_stats() signature in tests/contract/test_api.py
- [ ] T025 [P] [US2] Unit test for SourceStats dataclass creation in tests/unit/test_models.py
- [ ] T026 [P] [US2] Unit test for SourceStats.has_sufficient_samples() method in tests/unit/test_models.py
- [ ] T027 [P] [US2] Unit test for _validate_sourcestats() function in tests/unit/test_validation.py
- [ ] T028 [P] [US2] Integration test for get_source_stats() in tests/integration/test_sourcestats.py

### Implementation for User Story 2

- [ ] T029 [US2] Create SourceStats frozen dataclass in src/pychrony/models.py
- [ ] T030 [US2] Add has_sufficient_samples() method to SourceStats in src/pychrony/models.py
- [ ] T031 [US2] Add _validate_sourcestats() validation function in src/pychrony/_core/_bindings.py
- [ ] T032 [US2] Add _get_sourcestats_from_record() helper to extract SourceStats from libchrony record in src/pychrony/_core/_bindings.py
- [ ] T033 [US2] Implement get_source_stats() function in src/pychrony/_core/_bindings.py
- [ ] T034 [US2] Export SourceStats from src/pychrony/models.py __all__
- [ ] T035 [US2] Export get_source_stats and SourceStats from src/pychrony/__init__.py

**Checkpoint**: User Story 2 complete - `get_source_stats()` is functional and testable independently

---

## Phase 5: User Story 3 - Query RTC Data (Priority: P3)

**Goal**: Provide `get_rtc_data()` function to retrieve Real-Time Clock tracking information

**Independent Test**: Call `get_rtc_data()` and verify it returns RTCData object with offset and frequency values, or raises ChronyDataError if RTC tracking unavailable

### Tests for User Story 3

- [ ] T036 [P] [US3] Contract test for RTCData dataclass in tests/contract/test_api.py
- [ ] T037 [P] [US3] Contract test for get_rtc_data() signature in tests/contract/test_api.py
- [ ] T038 [P] [US3] Unit test for RTCData dataclass creation in tests/unit/test_models.py
- [ ] T039 [P] [US3] Unit test for RTCData.is_calibrated() method in tests/unit/test_models.py
- [ ] T040 [P] [US3] Unit test for _validate_rtc() function in tests/unit/test_validation.py
- [ ] T041 [P] [US3] Unit test for get_rtc_data() raising ChronyDataError when unavailable in tests/unit/test_bindings.py
- [ ] T042 [P] [US3] Integration test for get_rtc_data() in tests/integration/test_rtcdata.py

### Implementation for User Story 3

- [ ] T043 [US3] Create RTCData frozen dataclass in src/pychrony/models.py
- [ ] T044 [US3] Add is_calibrated() method to RTCData in src/pychrony/models.py
- [ ] T045 [US3] Add _validate_rtc() validation function in src/pychrony/_core/_bindings.py
- [ ] T046 [US3] Add _get_rtc_from_record() helper to extract RTCData from libchrony record in src/pychrony/_core/_bindings.py
- [ ] T047 [US3] Implement get_rtc_data() function in src/pychrony/_core/_bindings.py
- [ ] T048 [US3] Export RTCData from src/pychrony/models.py __all__
- [ ] T049 [US3] Export get_rtc_data and RTCData from src/pychrony/__init__.py

**Checkpoint**: User Story 3 complete - `get_rtc_data()` is functional and testable independently

---

## Phase 6: User Story 4 - Internal API Consistency (Priority: P2)

**Goal**: Ensure all report functions follow consistent patterns for connection handling, error raising, and data structure conventions

**Independent Test**: Call all report functions and verify they follow the same patterns as `get_tracking()`

### Tests for User Story 4

- [ ] T050 [P] [US4] Contract test verifying all functions accept optional socket_path in tests/contract/test_api.py
- [ ] T051 [P] [US4] Unit test verifying connection error handling consistency in tests/unit/test_bindings.py
- [ ] T052 [P] [US4] Unit test verifying all dataclasses are frozen in tests/unit/test_models.py

### Implementation for User Story 4

- [ ] T053 [US4] Verify socket_path handling matches get_tracking() pattern in all new functions
- [ ] T054 [US4] Verify error messages follow existing patterns (ChronyConnectionError, ChronyDataError)
- [ ] T055 [US4] Add docstrings to all new public functions following existing format
- [ ] T056 [US4] Add docstrings to all new dataclass fields

**Checkpoint**: User Story 4 complete - all functions follow consistent API patterns

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Final validation and documentation

- [ ] T057 Run full test suite: `uv run pytest`
- [ ] T058 Run linting: `uv run ruff check .`
- [ ] T059 Run formatting: `uv run ruff format .`
- [ ] T060 Run type checking: `uv run ty check src/`
- [ ] T061 Build and run integration tests in Docker
- [ ] T062 [P] Validate quickstart.md examples work correctly
- [ ] T063 Verify all public exports are in __all__ lists

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Already complete from initial project
- **Foundational (Phase 2)**: No dependencies - can start immediately, BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational (Phase 2)
- **User Story 2 (Phase 4)**: Depends on Foundational (Phase 2), independent of US1
- **User Story 3 (Phase 5)**: Depends on Foundational (Phase 2), independent of US1 and US2
- **User Story 4 (Phase 6)**: Depends on US1, US2, US3 (validates consistency across all)
- **Polish (Phase 7)**: Depends on all user stories complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational - No dependencies on other stories
- **User Story 3 (P3)**: Can start after Foundational - No dependencies on other stories
- **User Story 4 (P2)**: Depends on US1, US2, US3 completion (validates consistency)

### Within Each User Story

- Tests MUST be written and FAIL before implementation
- Dataclass before helper methods
- Helper methods before validation function
- Validation function before record extraction helper
- Record extraction helper before main function
- Main function before exports
- Exports before story completion

### Parallel Opportunities

- All Foundational tasks (T001-T003) work on the same file - execute sequentially
- All tests for a user story marked [P] can run in parallel
- User Stories 1, 2, 3 can proceed in parallel after Foundational phase (if team capacity allows)
- User Story 4 must wait for US1, US2, US3 to validate consistency

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together:
Task: "Contract test for Source dataclass in tests/contract/test_api.py"
Task: "Contract test for get_sources() signature in tests/contract/test_api.py"
Task: "Unit test for Source dataclass creation in tests/unit/test_models.py"
Task: "Unit test for Source.is_reachable() method in tests/unit/test_models.py"
Task: "Unit test for Source.is_selected() method in tests/unit/test_models.py"
Task: "Unit test for Source.mode_name property in tests/unit/test_models.py"
Task: "Unit test for Source.state_name property in tests/unit/test_models.py"
Task: "Unit test for _validate_source() function in tests/unit/test_validation.py"
Task: "Integration test for get_sources() in tests/integration/test_sources.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 2: Foundational (validation helpers)
2. Complete Phase 3: User Story 1 (get_sources)
3. **STOP and VALIDATE**: Test get_sources() independently
4. Can ship MVP with just get_sources() if needed

### Incremental Delivery

1. Complete Foundational → Validation ready
2. Add User Story 1 (get_sources) → Test independently → Usable MVP
3. Add User Story 2 (get_source_stats) → Test independently → Enhanced monitoring
4. Add User Story 3 (get_rtc_data) → Test independently → Complete report coverage
5. Add User Story 4 (consistency check) → Validate all follow patterns
6. Polish → Ship complete feature

### Sequential Execution (Recommended)

Since this is a single-developer effort building on existing patterns:

1. Phase 2: Foundational (T001-T003)
2. Phase 3: User Story 1 - MVP (T004-T022)
3. Phase 4: User Story 2 (T023-T035)
4. Phase 5: User Story 3 (T036-T049)
5. Phase 6: User Story 4 (T050-T056)
6. Phase 7: Polish (T057-T063)

---

## Notes

- [P] tasks = different files, no dependencies on incomplete tasks
- [Story] label maps task to specific user story for traceability
- Each user story delivers independent value (US1 alone is a valid MVP)
- Verify tests fail before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- All field mappings verified against libchrony source (client.c)
