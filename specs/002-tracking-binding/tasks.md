# Tasks: Chrony Tracking Binding

**Input**: Design documents from `/specs/002-tracking-binding/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/python-api.md, quickstart.md

**Tests**: Test tasks included per constitution requirement "Tests required" and plan.md testing strategy.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- Include exact file paths in descriptions

## Path Conventions

Based on plan.md structure:
- Source: `src/pychrony/`
- Tests: `tests/unit/`, `tests/integration/`, `tests/contract/`
- Docker: `docker/`

---

## Phase 1: Setup (Project Infrastructure)

**Purpose**: Project initialization, build system, and CFFI infrastructure

- [ ] T001 Create project directory structure per plan.md in src/pychrony/
- [ ] T002 [P] Configure pyproject.toml with CFFI build-requires and hatchling
- [ ] T003 [P] Create src/pychrony/__init__.py with __all__ exports stub
- [ ] T004 [P] Create src/pychrony/_core/__init__.py
- [ ] T005 Create CFFI build script in src/pychrony/_core/_build_bindings.py with ffi.set_source()
- [ ] T006 [P] Create tests/conftest.py with pytest fixtures
- [ ] T007 [P] Create docker/Dockerfile.test for Fedora + libchrony + libchrony-devel + chronyd
- [ ] T008 Create docker/docker-compose.test.yml for test orchestration

**Checkpoint**: Build infrastructure ready, CFFI extension can be compiled

---

## Phase 2: Foundational (Exception & Model Infrastructure)

**Purpose**: Core types that ALL user stories depend on - MUST complete before any user story

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T009 Create exception hierarchy in src/pychrony/exceptions.py (ChronyError, ChronyConnectionError, ChronyPermissionError, ChronyDataError, ChronyLibraryError)
- [ ] T010 Create TrackingStatus dataclass in src/pychrony/models.py with all 15 fields
- [ ] T011 Add is_synchronized() method to TrackingStatus in src/pychrony/models.py
- [ ] T012 Add is_leap_pending() method to TrackingStatus in src/pychrony/models.py
- [ ] T013 Add _ref_id_to_name() helper function in src/pychrony/models.py
- [ ] T014 Add _timespec_to_float() helper function in src/pychrony/_core/_bindings.py stub
- [ ] T015 [P] Create tests/unit/test_exceptions.py for exception hierarchy
- [ ] T016 [P] Create tests/unit/test_models.py for TrackingStatus dataclass

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Monitor Chrony Tracking Status (Priority: P1) 🎯 MVP

**Goal**: Application developers can retrieve chrony tracking status with structured data

**Independent Test**: Call get_tracking() on running chronyd and verify returned TrackingStatus contains offset, frequency, stratum, reference_id fields

### Tests for User Story 1

- [ ] T017 [P] [US1] Create tests/unit/test_validation.py for field validation (_validate_tracking)
- [ ] T018 [P] [US1] Create tests/contract/test_api.py for public API contract (imports, signatures, types)
- [ ] T019 [US1] Create tests/integration/test_tracking.py for get_tracking() with real chronyd

### Implementation for User Story 1

- [ ] T020 [US1] Implement _validate_tracking() function in src/pychrony/_core/_bindings.py
- [ ] T021 [US1] Implement field accessor helpers (_get_float_field, _get_uinteger_field, _get_string_field, _get_timespec_field) in src/pychrony/_core/_bindings.py
- [ ] T022 [US1] Implement _extract_tracking_fields() function in src/pychrony/_core/_bindings.py
- [ ] T023 [US1] Implement get_tracking() function in src/pychrony/_core/_bindings.py with session lifecycle
- [ ] T024 [US1] Export get_tracking in src/pychrony/__init__.py
- [ ] T025 [US1] Add socket path fallback logic (check /run/chrony/chronyd.sock then /var/run/chrony/chronyd.sock)

**Checkpoint**: User Story 1 complete - get_tracking() returns TrackingStatus from chronyd

---

## Phase 4: User Story 2 - Verify libchrony Integration (Priority: P2)

**Goal**: System administrators can verify pychrony works correctly and get clear errors when dependencies are missing

**Independent Test**: Import pychrony on system without libchrony and verify ChronyLibraryError is raised with helpful message

### Tests for User Story 2

- [ ] T026 [P] [US2] Create tests/integration/test_connection.py for connection error scenarios
- [ ] T027 [P] [US2] Add tests for ChronyLibraryError when libchrony missing in tests/unit/test_exceptions.py

### Implementation for User Story 2

- [ ] T028 [US2] Add library availability check at import time in src/pychrony/_core/_bindings.py
- [ ] T029 [US2] Implement socket connection error handling with ChronyConnectionError in src/pychrony/_core/_bindings.py
- [ ] T030 [US2] Implement permission error detection with ChronyPermissionError in src/pychrony/_core/_bindings.py
- [ ] T031 [US2] Add error code mapping from chrony_err to Python exceptions in src/pychrony/_core/_bindings.py

**Checkpoint**: User Story 2 complete - clear error messages for all failure scenarios

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Final validation, documentation, and CI setup

- [ ] T032 [P] Update src/pychrony/__init__.py with complete __all__ list and docstring
- [ ] T033 [P] Add py.typed marker file to src/pychrony/
- [ ] T034 Run type checking with mypy/pyright on src/pychrony/
- [ ] T035 [P] Create .github/workflows/test.yml for GitHub Actions CI
- [ ] T036 Run full test suite: uv run pytest tests/unit tests/contract
- [ ] T037 Run Docker integration tests: docker compose -f docker/docker-compose.test.yml run test-all
- [ ] T038 Validate quickstart.md examples work end-to-end

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-4)**: All depend on Foundational phase completion
  - US1 (P1): Independent, no dependencies on other stories
  - US2 (P2): Independent, can run parallel to US1
- **Polish (Phase 5)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Can run parallel to US1

### Within Each User Story

- Tests written first (TDD approach)
- Helper functions before main implementation
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

**Phase 1 (Setup)**:
- T002, T003, T004, T006, T007 can run in parallel

**Phase 2 (Foundational)**:
- T015, T016 (unit tests) can run in parallel after models/exceptions are done

**Phase 3 (US1)**:
- T017, T018 (tests) can run in parallel
- T020-T022 (helpers) must complete before T023 (get_tracking)

**Phase 4 (US2)**:
- T026, T027 (tests) can run in parallel
- Can start in parallel with US1 after Phase 2

---

## Parallel Example: Setup Phase

```bash
# Launch in parallel (no dependencies between these):
Task: "Configure pyproject.toml with CFFI build-requires and hatchling" (T002)
Task: "Create src/pychrony/__init__.py with __all__ exports stub" (T003)
Task: "Create src/pychrony/_core/__init__.py" (T004)
Task: "Create tests/conftest.py with pytest fixtures" (T006)
Task: "Create docker/Dockerfile.test" (T007)
```

## Parallel Example: User Story 1 Tests

```bash
# Launch all US1 tests together:
Task: "Create tests/unit/test_validation.py for field validation" (T017)
Task: "Create tests/contract/test_api.py for public API contract" (T018)
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T008)
2. Complete Phase 2: Foundational (T009-T016)
3. Complete Phase 3: User Story 1 (T017-T025)
4. **STOP and VALIDATE**: Test get_tracking() with real chronyd in Docker
5. Deploy/release if ready - basic functionality complete

### Incremental Delivery

1. Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Can release MVP!
3. Add User Story 2 → Test independently → Better error handling
4. Each story adds value without breaking previous stories

### Single Developer Strategy (Recommended)

1. Complete Setup (Phase 1)
2. Complete Foundational (Phase 2)
3. Complete User Story 1 (Phase 3) - P1 Priority
4. Complete User Story 2 (Phase 4) - P2 Priority
5. Complete Polish (Phase 5)

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Tests included per constitution "Tests required" mandate
- CFFI uses API mode (ffi.set_source) per constitution v1.2.0
- Integration tests must run inside Docker (libchrony is Linux-only)
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
