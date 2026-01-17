# Tasks: Python Enums for Categorical Fields

**Input**: Design documents from `/specs/004-categorical-enums/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md

**Tests**: Included per constitution requirement for test coverage on all new features.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/pychrony/`, `tests/` at repository root

---

## Phase 1: Setup

**Purpose**: No setup required - this feature adds to an existing project

*No tasks in this phase - project structure already exists*

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Create all three enum classes in models.py since they are interdependent and all user stories need them

**⚠️ CRITICAL**: All enum definitions must be complete before any user story implementation

- [x] T001 [P] Define LeapStatus enum class in src/pychrony/models.py
- [x] T002 [P] Define SourceState enum class in src/pychrony/models.py
- [x] T003 [P] Define SourceMode enum class in src/pychrony/models.py
- [x] T004 Export all three enum classes from src/pychrony/__init__.py
- [x] T005 Add enum classes to __all__ list in src/pychrony/models.py

**Checkpoint**: All enum classes defined and exported - user story implementation can now begin

---

## Phase 3: User Story 1 - Check Source Synchronization State (Priority: P1) 🎯 MVP

**Goal**: Enable developers to check if a time source is selected for synchronization using SourceState enum values instead of magic numbers

**Independent Test**: Import SourceState from pychrony, call get_sources(), compare source.state to SourceState.SELECTED

### Tests for User Story 1

- [x] T006 [P] [US1] Unit test for SourceState enum values and .name/.value attributes in tests/unit/test_enums.py
- [x] T007 [P] [US1] Contract test verifying Source.state is SourceState type in tests/contract/test_api_stability.py
- [x] T008 [P] [US1] Unit test for ChronyDataError on invalid state value in tests/unit/test_enums.py

### Implementation for User Story 1

- [x] T009 [US1] Change Source.state field type from int to SourceState in src/pychrony/models.py
- [x] T010 [US1] Update Source.is_selected() method to use SourceState.SELECTED in src/pychrony/models.py
- [x] T011 [US1] Remove Source.state_name property from src/pychrony/models.py
- [x] T012 [US1] Update _get_source_from_record() to convert state integer to SourceState enum in src/pychrony/_core/_bindings.py
- [x] T013 [US1] Add try/except around SourceState conversion raising ChronyDataError for unknown values in src/pychrony/_core/_bindings.py
- [x] T014 [US1] Remove _validate_bounded_int call for state in _validate_source() in src/pychrony/_core/_bindings.py
- [x] T015 [US1] Integration test for Source.state enum values from running chronyd in tests/integration/test_enums.py

**Checkpoint**: User Story 1 complete - SourceState enum fully functional and tested

---

## Phase 4: User Story 2 - Check Leap Second Status (Priority: P2)

**Goal**: Enable developers to check if a leap second insertion or deletion is pending using LeapStatus enum values

**Independent Test**: Import LeapStatus from pychrony, call get_tracking(), check tracking.leap_status against LeapStatus.INSERT or LeapStatus.DELETE

### Tests for User Story 2

- [x] T016 [P] [US2] Unit test for LeapStatus enum values and .name/.value attributes in tests/unit/test_enums.py
- [x] T017 [P] [US2] Contract test verifying TrackingStatus.leap_status is LeapStatus type in tests/contract/test_api_stability.py
- [x] T018 [P] [US2] Unit test for ChronyDataError on invalid leap_status value in tests/unit/test_enums.py

### Implementation for User Story 2

- [x] T019 [US2] Change TrackingStatus.leap_status field type from int to LeapStatus in src/pychrony/models.py
- [x] T020 [US2] Update TrackingStatus.is_leap_pending() method to use LeapStatus.INSERT and LeapStatus.DELETE in src/pychrony/models.py
- [x] T021 [US2] Update _extract_tracking_fields() to convert leap_status integer to LeapStatus enum in src/pychrony/_core/_bindings.py
- [x] T022 [US2] Add try/except around LeapStatus conversion raising ChronyDataError for unknown values in src/pychrony/_core/_bindings.py
- [x] T023 [US2] Remove leap_status bounds check from _validate_tracking() in src/pychrony/_core/_bindings.py
- [x] T024 [US2] Integration test for TrackingStatus.leap_status enum values from running chronyd in tests/integration/test_enums.py

**Checkpoint**: User Story 2 complete - LeapStatus enum fully functional and tested

---

## Phase 5: User Story 3 - Identify Source Type (Priority: P3)

**Goal**: Enable developers to distinguish between NTP clients, peers, and reference clocks using the SourceMode enum

**Independent Test**: Import SourceMode from pychrony, iterate sources, group by source.mode values (CLIENT, PEER, REFCLOCK)

### Tests for User Story 3

- [x] T025 [P] [US3] Unit test for SourceMode enum values and .name/.value attributes in tests/unit/test_enums.py
- [x] T026 [P] [US3] Contract test verifying Source.mode is SourceMode type in tests/contract/test_api_stability.py
- [x] T027 [P] [US3] Unit test for ChronyDataError on invalid mode value in tests/unit/test_enums.py

### Implementation for User Story 3

- [x] T028 [US3] Change Source.mode field type from int to SourceMode in src/pychrony/models.py
- [x] T029 [US3] Remove Source.mode_name property from src/pychrony/models.py
- [x] T030 [US3] Update _get_source_from_record() to convert mode integer to SourceMode enum in src/pychrony/_core/_bindings.py
- [x] T031 [US3] Add try/except around SourceMode conversion raising ChronyDataError for unknown values in src/pychrony/_core/_bindings.py
- [x] T032 [US3] Remove _validate_bounded_int call for mode in _validate_source() in src/pychrony/_core/_bindings.py
- [x] T033 [US3] Integration test for Source.mode enum values from running chronyd in tests/integration/test_enums.py

**Checkpoint**: User Story 3 complete - SourceMode enum fully functional and tested

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final cleanup and verification

- [x] T034 Update Source dataclass docstring to reflect enum types in src/pychrony/models.py
- [x] T035 Update TrackingStatus dataclass docstring to reflect LeapStatus type in src/pychrony/models.py
- [x] T036 [P] Verify all existing tests pass with enum changes by running pytest
- [x] T037 [P] Verify type checker (ty) passes with enum types in src/
- [x] T038 Run full test suite including Docker integration tests

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: N/A - existing project
- **Phase 2 (Foundational)**: No dependencies - creates enum classes
- **User Stories (Phase 3-5)**: All depend on Phase 2 completion
  - User stories can proceed in parallel or sequentially
  - Each user story is independently testable
- **Phase 6 (Polish)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Depends on T001-T005 (enum definitions) - No dependencies on US2/US3
- **User Story 2 (P2)**: Depends on T001-T005 (enum definitions) - No dependencies on US1/US3
- **User Story 3 (P3)**: Depends on T001-T005 (enum definitions) - No dependencies on US1/US2

### Within Each User Story

- Tests MUST be written and FAIL before implementation
- Implementation tasks in order as listed
- Story complete before declaring checkpoint

### Parallel Opportunities

**Phase 2 (Foundational)**:
- T001, T002, T003 can run in parallel (different enum classes, same file but independent sections)

**Within each User Story**:
- All test tasks (T006-T008, T016-T018, T025-T027) marked [P] can run in parallel
- Implementation tasks must be sequential within each story

**Across User Stories**:
- Once Phase 2 completes, US1, US2, US3 can be worked on in parallel

---

## Parallel Example: Foundational Phase

```bash
# Launch all enum definitions together (different classes, same file):
Task: "Define LeapStatus enum class in src/pychrony/models.py"
Task: "Define SourceState enum class in src/pychrony/models.py"
Task: "Define SourceMode enum class in src/pychrony/models.py"
```

## Parallel Example: User Story 1 Tests

```bash
# Launch all US1 tests together:
Task: "Unit test for SourceState enum values in tests/unit/test_enums.py"
Task: "Contract test verifying Source.state is SourceState type in tests/contract/test_api_stability.py"
Task: "Unit test for ChronyDataError on invalid state value in tests/unit/test_enums.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 2: Foundational (define all enums)
2. Complete Phase 3: User Story 1 (SourceState)
3. **STOP and VALIDATE**: Test SourceState independently
4. Most common use case now works with type safety

### Incremental Delivery

1. Phase 2 → All enum classes defined
2. Add User Story 1 → SourceState functional → Test
3. Add User Story 2 → LeapStatus functional → Test
4. Add User Story 3 → SourceMode functional → Test
5. Phase 6 → Polish and final verification

### Single Developer Strategy

Execute in priority order: Phase 2 → US1 → US2 → US3 → Phase 6

---

## Notes

- All enums use standard library `enum.Enum` (not IntEnum)
- Integer comparisons will NOT work - must use enum members
- Removed properties: `Source.mode_name`, `Source.state_name` - use `.name` attribute instead
- Invalid enum values raise ChronyDataError with descriptive message
- Commit after each task or logical group
