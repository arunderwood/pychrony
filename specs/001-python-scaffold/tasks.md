---

description: "Task list for Python bindings scaffold and CI setup feature implementation"
---

# Tasks: Python Bindings Scaffold and CI Setup

**Input**: Design documents from `/specs/001-python-scaffold/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Tests are explicitly requested in the feature specification for validating package structure and CI functionality.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root
- Paths shown follow the standard Python package layout from plan.md

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Create Python package structure with src/pychrony/ directory per implementation plan
- [X] T002 Initialize UV package manager with pyproject.toml using hatchling build backend
- [X] T003 [P] Configure ruff for linting and formatting in pyproject.toml
- [X] T004 [P] Configure ty for type checking in pyproject.toml
- [X] T005 [P] Setup pytest and tox configuration for testing framework
- [X] T006 Create placeholder directory structure for future CFFI bindings in src/pychrony/_core/
- [X] T036 [P] Create placeholder module files for future libchrony bindings in src/pychrony/_core/

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T007 Create pyproject.toml with complete project metadata including MIT license
- [X] T008 [P] Create __init__.py with package exports and version handling in src/pychrony/
- [X] T009 [P] Create __about__.py with version and author information in src/pychrony/
- [X] T010 [P] Setup placeholder modules for future libchrony bindings in src/pychrony/_core/
- [X] T011 Create tests/ directory structure with conftest.py configuration
- [X] T012 Create GitHub Actions workflow file for CI matrix testing

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Package Import Validation (Priority: P1) 🎯 MVP

**Goal**: Developers need to verify that the pychrony package structure is correct and can be imported successfully without any libchrony dependencies.

**Independent Test**: Create a fresh Python environment and run `import pychrony` successfully, then verify `pychrony.__version__` returns a valid version string.

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T013 [P] [US1] Test package import success in tests/test_import.py
- [X] T014 [P] [US1] Test version string accessibility in tests/test_import.py
- [X] T015 [P] [US1] Implement package __init__.py with proper imports and __all__ in src/pychrony/__init__.py
- [X] T016 [P] [US1] Implement __about__.py with version and metadata in src/pychrony/__about__.py
- [X] T017 [US1] Setup dynamic version from VCS using hatch-vcs in pyproject.toml

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Local Test Execution (Priority: P1)

**Goal**: Developers need to run tests locally to validate their changes before committing to ensure the testing infrastructure works correctly.

**Independent Test**: Run `pytest tests/` in the repository root and observe all tests pass, including both placeholder and import tests.

### Tests for User Story 2

- [X] T018 [P] [US2] Test pytest discovery works with placeholder tests in tests/test_discovery.py
- [X] T019 [P] [US2] Test test execution completes without errors in tests/test_execution.py
- [X] T020 [P] [US2] Create pytest configuration in pyproject.toml or pytest.ini
- [X] T021 [US2] Setup tox.ini for multi-environment testing configuration
- [X] T022 [US2] Create initial placeholder test file in tests/test_placeholder.py
- [X] T023 [US2] Integrate test discovery with UV workflow in pyproject.toml

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - CI Validation (Priority: P2)

**Goal**: Developers need assurance that their changes work across multiple Python versions through automated CI checks.

**Independent Test**: Submit a PR and observe GitHub Actions successfully run the test matrix across all Python versions (3.10, 3.11, 3.12, 3.13, 3.14).

### Tests for User Story 3

- [X] T024 [P] [US3] Test CI workflow triggers correctly on PR in .github/workflows/ci.yml
- [X] T025 [P] [US3] Test matrix execution passes for all Python versions in .github/workflows/ci.yml
- [X] T026 [P] [US3] Create GitHub Actions workflow with Python version matrix in .github/workflows/ci.yml
- [X] T027 [US3] Configure UV caching in GitHub Actions for faster CI runs
- [X] T028 [US3] Setup fail-fast behavior for matrix jobs in .github/workflows/ci.yml
- [X] T029 [US3] Configure test execution across all Python versions in tox.ini

**Checkpoint**: All user stories should now be independently functional

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [X] T030 [P] Create comprehensive README.md with setup and usage instructions
- [X] T031 Add .gitignore file for Python project standards
- [X] T032 Create .python-version file specifying primary development Python version for UV
- [X] T033 [P] Add LICENSE file with MIT license text
- [X] T034 Validate quickstart.md instructions work end-to-end
- [X] T035 Run final test suite to ensure all functionality works

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P1 → P2)
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P1)**: Can start after Foundational (Phase 2) - Integrates with US1 testing infrastructure but independently testable
- **User Story 3 (P2)**: Can start after Foundational (Phase 2) - Uses tests from US1/US2 but validates independently

### Within Each User Story

- Tests MUST be written and FAIL before implementation
- Core package structure before test infrastructure
- Local testing before CI validation
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- All tests for a user story marked [P] can run in parallel
- Different user stories can be worked on in parallel by different team members

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together:
Task: "Test package import success in tests/test_import.py"
Task: "Test version string accessibility in tests/test_import.py"

# Launch all package files for User Story 1 together:
Task: "Implement package __init__.py with proper imports and __all__ in src/pychrony/__init__.py"
Task: "Implement __about__.py with version and metadata in src/pychrony/__about__.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test User Story 1 independently with `import pychrony`
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo
4. Add User Story 3 → Test independently → Deploy/Demo
5. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (Package structure)
   - Developer B: User Story 2 (Local testing)
   - Developer C: User Story 3 (CI setup)
3. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
