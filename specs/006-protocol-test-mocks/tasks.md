# Tasks: Protocol-Level Test Mock Infrastructure

**Input**: Design documents from `/specs/006-protocol-test-mocks/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/mock-api.md

**Tests**: Tests are included as this is a test infrastructure feature - the mock itself needs validation.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Mock infrastructure**: `tests/mocks/` package
- **Field registry**: `src/pychrony/_core/_fields.py` (shared between production and tests)
- **Unit tests**: `tests/unit/` directory
- Following single project structure from plan.md

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Create the tests/mocks package structure and foundational types

- [ ] T001 Create tests/mocks/ package directory structure with __init__.py
- [ ] T002 [P] Create MockTimespec dataclass for timespec simulation in tests/mocks/session.py
- [ ] T003 [P] Create FieldType enum in src/pychrony/_core/_fields.py with FLOAT, UINTEGER, INTEGER, STRING, TIMESPEC values

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core field registry, configuration dataclasses, and mock infrastructure that ALL user stories depend on

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Field Registry (src/pychrony/_core/_fields.py)

- [ ] T004 [P] Create TRACKING_FIELDS dict mapping field names to FieldType in src/pychrony/_core/_fields.py
- [ ] T005 [P] Create SOURCE_FIELDS dict mapping field names to FieldType in src/pychrony/_core/_fields.py
- [ ] T006 [P] Create SOURCESTATS_FIELDS dict mapping field names to FieldType in src/pychrony/_core/_fields.py
- [ ] T007 [P] Create RTC_FIELDS dict mapping field names to FieldType in src/pychrony/_core/_fields.py
- [ ] T008 Refactor _bindings.py to use field registry from _fields.py for tracking report
- [ ] T009 Refactor _bindings.py to use field registry from _fields.py for sources report
- [ ] T010 Refactor _bindings.py to use field registry from _fields.py for sourcestats report
- [ ] T011 Refactor _bindings.py to use field registry from _fields.py for rtcdata report
- [ ] T012 Add unit tests for _fields.py field registries in tests/unit/test_fields.py

### Mock Configuration Dataclasses (tests/mocks/config.py)

- [ ] T013 Implement ChronyStateConfig dataclass with all tracking fields in tests/mocks/config.py
- [ ] T014 Implement SourceConfig dataclass with source and sourcestats fields in tests/mocks/config.py
- [ ] T015 Implement RTCConfig dataclass with RTC fields in tests/mocks/config.py
- [ ] T016 Add __post_init__ validation to ChronyStateConfig in tests/mocks/config.py
- [ ] T017 Add __post_init__ validation to SourceConfig in tests/mocks/config.py
- [ ] T018 Add __post_init__ validation to RTCConfig in tests/mocks/config.py
- [ ] T019 Implement reference_id_name() derived method on ChronyStateConfig in tests/mocks/config.py
- [ ] T020 Implement compute_reference_id() method for SourceConfig in tests/mocks/config.py

### Mock Session Infrastructure (tests/mocks/session.py)

- [ ] T021 Create MockFFI class with NULL, new(), string() methods in tests/mocks/session.py
- [ ] T022 Create MockLib class skeleton with all 15 CFFI function stubs in tests/mocks/session.py
- [ ] T023 Implement MockChronySession class that holds config and creates MockLib/MockFFI in tests/mocks/session.py
- [ ] T024 Implement protocol state machine (current_report, current_record_index, pending_responses) in tests/mocks/session.py
- [ ] T025 Implement chrony_open_socket mock with error injection support in tests/mocks/session.py
- [ ] T026 Implement chrony_init_session mock with error injection support in tests/mocks/session.py
- [ ] T027 Implement chrony_close_socket and chrony_deinit_session mocks in tests/mocks/session.py
- [ ] T028 Implement chrony_request_report_number_records mock in tests/mocks/session.py
- [ ] T029 Implement chrony_needs_response and chrony_process_response mocks in tests/mocks/session.py
- [ ] T030 Implement chrony_get_report_number_records mock in tests/mocks/session.py
- [ ] T031 Implement chrony_request_record mock in tests/mocks/session.py
- [ ] T032 Implement chrony_get_field_index mock with field name lookup (using _fields.py) in tests/mocks/session.py
- [ ] T033 Implement chrony_get_field_float mock in tests/mocks/session.py
- [ ] T034 Implement chrony_get_field_uinteger mock in tests/mocks/session.py
- [ ] T035 Implement chrony_get_field_integer mock in tests/mocks/session.py
- [ ] T036 Implement chrony_get_field_string mock in tests/mocks/session.py
- [ ] T037 Implement chrony_get_field_timespec mock in tests/mocks/session.py

### Context Manager (tests/mocks/context.py)

- [ ] T038 Implement patched_chrony_connection context manager in tests/mocks/context.py
- [ ] T039 Export public API from tests/mocks/__init__.py

**Checkpoint**: Foundation ready - MockChronySession can simulate basic chrony protocol

---

## Phase 3: User Story 5 - Declarative Scenario Configuration (Priority: P2) 🎯 MVP

**Goal**: Enable declarative configuration of test scenarios via dataclasses and context manager

**Independent Test**: Create a ChronyStateConfig with custom stratum and offset, apply via patched_chrony_connection, verify get_tracking() returns those values

**Why MVP**: US5 provides the foundational context manager and configuration that all other user stories depend on for their tests.

### Tests for User Story 5

- [ ] T040 [P] [US5] Test ChronyStateConfig with custom stratum returns correct value in tests/unit/test_mock_config.py
- [ ] T041 [P] [US5] Test ChronyStateConfig validation rejects invalid stratum in tests/unit/test_mock_config.py
- [ ] T042 [P] [US5] Test patched_chrony_connection yields working ChronyConnection in tests/unit/test_mock_scenarios.py
- [ ] T043 [P] [US5] Test patched_chrony_connection restores original bindings on exit in tests/unit/test_mock_scenarios.py

### Implementation for User Story 5

- [ ] T044 [US5] Create SCENARIO_NTP_SYNCED preset constant in tests/mocks/scenarios.py
- [ ] T045 [US5] Verify patched_chrony_connection default uses SCENARIO_NTP_SYNCED in tests/mocks/context.py
- [ ] T046 [US5] Add integration test: custom config → get_tracking() → verify fields in tests/unit/test_mock_scenarios.py

**Checkpoint**: User Story 5 complete - declarative configuration works end-to-end

---

## Phase 4: User Story 1 - Testing RTC Functionality Without Hardware (Priority: P1)

**Goal**: Enable testing of RTC functionality without hardware access

**Independent Test**: Configure mock with RTCConfig(available=True, samples=15), call get_rtc_data(), verify RTCData returned with correct values

### Tests for User Story 1

- [ ] T047 [P] [US1] Test RTCConfig validation rejects negative samples in tests/unit/test_mock_config.py
- [ ] T048 [P] [US1] Test get_rtc_data returns RTCData when rtc.available=True in tests/unit/test_rtc_scenarios.py
- [ ] T049 [P] [US1] Test get_rtc_data returns None when rtc=None in tests/unit/test_rtc_scenarios.py
- [ ] T050 [P] [US1] Test get_rtc_data returns None when rtc.available=False in tests/unit/test_rtc_scenarios.py
- [ ] T051 [P] [US1] Test RTCData.is_calibrated() returns False when samples=0 in tests/unit/test_rtc_scenarios.py

### Implementation for User Story 1

- [ ] T052 [US1] Implement rtcdata report handling in chrony_get_report_number_records in tests/mocks/session.py
- [ ] T053 [US1] Implement rtcdata field extraction in chrony_get_field_* methods in tests/mocks/session.py
- [ ] T054 [US1] Create SCENARIO_RTC_AVAILABLE preset in tests/mocks/scenarios.py
- [ ] T055 [US1] Add SCENARIO_RTC_UNAVAILABLE preset (rtc=None) in tests/mocks/scenarios.py

**Checkpoint**: User Story 1 complete - RTC testing works without hardware

---

## Phase 5: User Story 2 - Testing Leap Second States (Priority: P1)

**Goal**: Enable testing of leap second INSERT and DELETE states

**Independent Test**: Configure mock with leap_status=LeapStatus.INSERT, call get_tracking(), verify is_leap_pending() returns True

### Tests for User Story 2

- [ ] T056 [P] [US2] Test leap_status INSERT returns is_leap_pending True in tests/unit/test_leap_scenarios.py
- [ ] T057 [P] [US2] Test leap_status DELETE returns is_leap_pending True in tests/unit/test_leap_scenarios.py
- [ ] T058 [P] [US2] Test leap_status NORMAL returns is_leap_pending False in tests/unit/test_leap_scenarios.py
- [ ] T059 [P] [US2] Test leap_status UNSYNC returns is_leap_pending False in tests/unit/test_leap_scenarios.py

### Implementation for User Story 2

- [ ] T060 [US2] Verify tracking report includes leap_status field extraction in tests/mocks/session.py
- [ ] T061 [US2] Create SCENARIO_LEAP_INSERT preset in tests/mocks/scenarios.py
- [ ] T062 [US2] Create SCENARIO_LEAP_DELETE preset in tests/mocks/scenarios.py

**Checkpoint**: User Story 2 complete - Leap second states testable

---

## Phase 6: User Story 7 - Sync/Unsync State Transitions (Priority: P3)

**Goal**: Enable testing of synchronized and unsynchronized states

**Independent Test**: Configure mock with stratum=16 and reference_id=0, verify is_synchronized() returns False

### Tests for User Story 7

- [ ] T063 [P] [US7] Test stratum=16 reference_id=0 returns is_synchronized False in tests/unit/test_mock_scenarios.py
- [ ] T064 [P] [US7] Test stratum=2 valid reference_id returns is_synchronized True in tests/unit/test_mock_scenarios.py
- [ ] T065 [P] [US7] Test stratum=15 boundary returns is_synchronized True in tests/unit/test_mock_scenarios.py
- [ ] T066 [P] [US7] Test stratum=0 (reference clock) returns is_synchronized True in tests/unit/test_mock_scenarios.py

### Implementation for User Story 7

- [ ] T067 [US7] Verify stratum and reference_id fields extracted correctly in tracking report in tests/mocks/session.py
- [ ] T068 [US7] Create SCENARIO_UNSYNC preset (stratum=16, reference_id=0) in tests/mocks/scenarios.py

**Checkpoint**: User Story 7 complete - Sync state testing works

---

## Phase 7: User Story 3 - Testing Reference Clock Sources (Priority: P2)

**Goal**: Enable testing of GPS, PPS reference clock sources

**Independent Test**: Configure source with mode=SourceMode.REFCLOCK and address="GPS", call get_sources(), verify Source has REFCLOCK mode

### Tests for User Story 3

- [ ] T069 [P] [US3] Test source with REFCLOCK mode appears correctly in tests/unit/test_source_scenarios.py
- [ ] T070 [P] [US3] Test GPS reference clock source has address "GPS" in tests/unit/test_source_scenarios.py
- [ ] T071 [P] [US3] Test PPS reference clock source works in tests/unit/test_source_scenarios.py
- [ ] T072 [P] [US3] Test stratum 0 source (reference clock) in tests/unit/test_source_scenarios.py

### Implementation for User Story 3

- [ ] T073 [US3] Implement sources report handling in chrony_get_report_number_records in tests/mocks/session.py
- [ ] T074 [US3] Implement sources field extraction for all source fields in tests/mocks/session.py
- [ ] T075 [US3] Create SCENARIO_GPS_REFCLOCK preset in tests/mocks/scenarios.py
- [ ] T076 [US3] Add SCENARIO_PPS_REFCLOCK preset in tests/mocks/scenarios.py

**Checkpoint**: User Story 3 complete - Reference clock testing works

---

## Phase 8: User Story 4 - Testing Multi-Source Selection Scenarios (Priority: P2)

**Goal**: Enable testing of multiple sources with different states

**Independent Test**: Configure 3 sources with SELECTED, FALSETICKER, SELECTABLE states, verify filtering by is_selected() returns exactly one

### Tests for User Story 4

- [ ] T077 [P] [US4] Test multiple sources returned from get_sources() in tests/unit/test_source_scenarios.py
- [ ] T078 [P] [US4] Test filtering sources by is_selected() returns exactly one in tests/unit/test_source_scenarios.py
- [ ] T079 [P] [US4] Test filtering sources by state FALSETICKER works in tests/unit/test_source_scenarios.py
- [ ] T080 [P] [US4] Test source reachability 255 vs 0 vs 128 in tests/unit/test_source_scenarios.py
- [ ] T081 [P] [US4] Test is_reachable() returns False for reachability=0 in tests/unit/test_source_scenarios.py
- [ ] T082 [P] [US4] Test get_sources() returns empty list when sources=[] in tests/unit/test_source_scenarios.py

### Implementation for User Story 4

- [ ] T083 [US4] Verify multiple sources iteration works in sources report in tests/mocks/session.py
- [ ] T084 [US4] Implement sourcestats report handling for multiple sources in tests/mocks/session.py
- [ ] T085 [US4] Create SCENARIO_MULTI_SOURCE preset in tests/mocks/scenarios.py
- [ ] T086 [US4] Add get_source_stats() integration test with multiple sources in tests/unit/test_source_scenarios.py

**Checkpoint**: User Story 4 complete - Multi-source testing works

---

## Phase 9: User Story 6 - Error Injection for Exception Testing (Priority: P3)

**Goal**: Enable injecting errors to test exception handling paths

**Independent Test**: Configure error_injection={"chrony_open_socket": -13}, verify ChronyPermissionError raised

### Tests for User Story 6

- [ ] T087 [P] [US6] Test chrony_open_socket error raises ChronyConnectionError in tests/unit/test_mock_session.py
- [ ] T088 [P] [US6] Test chrony_open_socket -13 raises ChronyPermissionError in tests/unit/test_mock_session.py
- [ ] T089 [P] [US6] Test chrony_init_session error raises ChronyConnectionError in tests/unit/test_mock_session.py
- [ ] T090 [P] [US6] Test chrony_process_response error raises ChronyDataError in tests/unit/test_mock_session.py
- [ ] T091 [P] [US6] Test chrony_request_record error raises ChronyDataError in tests/unit/test_mock_session.py

### Implementation for User Story 6

- [ ] T092 [US6] Verify all error injection points work in MockLib methods in tests/mocks/session.py
- [ ] T093 [US6] Add error_injection validation to ChronyStateConfig in tests/mocks/config.py
- [ ] T094 [US6] Document error injection keys in tests/mocks/__init__.py docstring

**Checkpoint**: User Story 6 complete - Error injection testing works

---

## Phase 10: Polish & Cross-Cutting Concerns

**Purpose**: Validation, documentation, and compatibility verification

- [ ] T095 [P] Run existing unit tests to verify no breakage (uv run pytest tests/unit -v)
- [ ] T096 [P] Run existing contract tests to verify no breakage (uv run pytest tests/contract -v)
- [ ] T097 Verify mock tests run without CFFI bindings (test in fresh environment)
- [ ] T098 Run quickstart.md examples to validate documentation accuracy
- [ ] T099 [P] Add type hints to all public functions in tests/mocks/ modules
- [ ] T100 Run ruff check and ruff format on all modified files
- [ ] T101 Verify all 7 scenarios from FR-005 are implemented in tests/mocks/scenarios.py
- [ ] T102 [P] Test maximum/minimum float values for offset and frequency fields in tests/unit/test_mock_config.py

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup - BLOCKS all user stories
  - Field registry (T004-T012) must complete before mock session can use it
  - _bindings.py refactor (T008-T011) can proceed in parallel with mock config
- **User Story 5 (Phase 3)**: Depends on Foundational - MVP for context manager
- **User Stories 1,2,7 (Phases 4-6)**: Depend on US5 - can proceed in parallel
- **User Stories 3,4 (Phases 7-8)**: Depend on US5 - can proceed in parallel
- **User Story 6 (Phase 9)**: Depends on US5 - error injection tests
- **Polish (Phase 10)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 5 (MVP)**: Foundation - provides patched_chrony_connection context manager
- **User Story 1 (P1)**: Independent after US5 - RTC testing
- **User Story 2 (P1)**: Independent after US5 - Leap second testing
- **User Story 3 (P2)**: Independent after US5 - REFCLOCK testing
- **User Story 4 (P2)**: Independent after US5 - Multi-source testing
- **User Story 6 (P3)**: Independent after US5 - Error injection
- **User Story 7 (P3)**: Independent after US5 - Sync state testing

### Within Each User Story

- Tests written FIRST (TDD approach for test infrastructure)
- Implementation follows tests
- Scenarios created after implementation verified

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- Field registry tasks T004-T007 can run in parallel
- All test tasks marked [P] within a user story can run in parallel
- After US5 complete: US1, US2, US3, US4, US6, US7 can all proceed in parallel
- Polish tasks marked [P] can run in parallel

---

## Parallel Example: User Story 1 (RTC)

```bash
# Launch all tests for User Story 1 together:
Task: "Test RTCConfig validation rejects negative samples in tests/unit/test_mock_config.py"
Task: "Test get_rtc_data returns RTCData when rtc.available=True in tests/unit/test_rtc_scenarios.py"
Task: "Test get_rtc_data returns None when rtc=None in tests/unit/test_rtc_scenarios.py"
Task: "Test get_rtc_data returns None when rtc.available=False in tests/unit/test_rtc_scenarios.py"
Task: "Test RTCData.is_calibrated() returns False when samples=0 in tests/unit/test_rtc_scenarios.py"
```

---

## Implementation Strategy

### MVP First (User Story 5 + Foundation)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - provides field registry AND MockChronySession)
3. Complete Phase 3: User Story 5 (context manager working)
4. **STOP and VALIDATE**: patched_chrony_connection works with basic config
5. Deploy/demo if ready

### Incremental Delivery

1. Setup + Foundational → Field registry + Mock infrastructure ready
2. Add User Story 5 → Context manager works → MVP!
3. Add User Story 1 → RTC testing works
4. Add User Story 2 → Leap second testing works
5. Continue with remaining stories by priority

### Parallel Team Strategy

With multiple developers after Foundational phase:

1. Team completes Setup + Foundational + US5 together
2. Once US5 is done:
   - Developer A: User Story 1 (RTC) + User Story 2 (Leap)
   - Developer B: User Story 3 (REFCLOCK) + User Story 4 (Multi-source)
   - Developer C: User Story 6 (Errors) + User Story 7 (Sync states)
3. All stories complete independently, then Polish phase

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Tests are TDD style - write test, verify fail, implement, verify pass
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Run `uv run pytest tests/unit -v` frequently to catch regressions
- Field registry in _fields.py is shared between production _bindings.py and test mocks
