# Tasks: PyPI Packaging and Distribution

**Input**: Design documents from `/specs/005-pypi-packaging/`
**Prerequisites**: plan.md, spec.md, research.md, quickstart.md

**Tests**: No test tasks included (not explicitly requested in specification). Wheel testing is handled by cibuildwheel's built-in test-command.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Package metadata and cibuildwheel configuration

- [ ] T001 Verify pyproject.toml has complete package metadata (classifiers, URLs, description)
- [ ] T002 Add [tool.cibuildwheel] configuration to pyproject.toml
- [ ] T003 Add [tool.cibuildwheel.linux] configuration for manylinux_2_28 in pyproject.toml
- [ ] T004 [P] Add dist/ and wheelhouse/ to .gitignore

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: GitHub environments and Trusted Publisher setup (MANUAL - must be done before CI can publish)

**⚠️ CRITICAL**: These are manual setup tasks that MUST be complete before release workflows can publish

- [ ] T005 Create GitHub environment `testpypi` in repository Settings → Environments
- [ ] T006 Create GitHub environment `pypi` in repository Settings → Environments with deployment protection
- [ ] T007 Configure Test PyPI Trusted Publisher at test.pypi.org/manage/account/publishing/
- [ ] T008 Configure Production PyPI Trusted Publisher at pypi.org/manage/account/publishing/

**Checkpoint**: Trusted Publishers configured - release workflows can now authenticate to PyPI

---

## Phase 3: User Story 1 - Install Package via pip (Priority: P1) 🎯 MVP

**Goal**: Package can be installed via `pip install pychrony` from PyPI

**Independent Test**: Run `pip install pychrony` in fresh venv and verify `from pychrony import get_tracking` works

### Implementation for User Story 1

- [ ] T009 [US1] Update README.md with pip installation instructions
- [ ] T010 [US1] Update README.md to document libchrony system dependency requirement
- [ ] T011 [US1] Verify package metadata displays correctly with `uv build && uv pip show pychrony`

**Checkpoint**: Package metadata and documentation complete for pip users

---

## Phase 4: User Story 2 - Automated Release Publishing (Priority: P2)

**Goal**: Maintainer can push version tag to automatically build and publish to Test PyPI

**Independent Test**: Push tag `v0.1.0-test` and verify wheels appear on Test PyPI

### Implementation for User Story 2

- [ ] T012 [US2] Create .github/workflows/release.yml with version tag trigger
- [ ] T013 [US2] Add checkout step with fetch-depth: 0 for hatch-vcs versioning
- [ ] T014 [US2] Add QEMU setup step for arm64 emulation in .github/workflows/release.yml
- [ ] T015 [US2] Add cibuildwheel build step in .github/workflows/release.yml
- [ ] T016 [US2] Add sdist build step using uv build --sdist in .github/workflows/release.yml
- [ ] T017 [US2] Add artifact upload step in .github/workflows/release.yml
- [ ] T018 [US2] Add Test PyPI publish step with id-token: write permission in .github/workflows/release.yml
- [ ] T019 [US2] Create .github/workflows/publish.yml for manual production PyPI promotion
- [ ] T020 [US2] Add workflow_dispatch trigger with artifact download in .github/workflows/publish.yml
- [ ] T021 [US2] Add production PyPI publish step with pypi environment in .github/workflows/publish.yml

**Checkpoint**: Full release automation configured - tag push → Test PyPI → manual promote → Production PyPI

---

## Phase 5: User Story 3 - Verify Package Works After Installation (Priority: P2)

**Goal**: Wheels are tested before publishing to catch packaging issues

**Independent Test**: Build wheel locally, install in isolated venv, run unit tests against installed package

### Implementation for User Story 3

- [ ] T022 [US3] Configure test-requires in [tool.cibuildwheel] section of pyproject.toml
- [ ] T023 [US3] Configure test-command to run unit and contract tests in pyproject.toml
- [ ] T024 [US3] Verify tests run successfully in cibuildwheel container (local test with cibuildwheel --platform linux)

**Checkpoint**: Built wheels are tested before publishing

---

## Phase 6: User Story 4 - Build Wheels Locally (Priority: P3)

**Goal**: Developers can build wheels locally to test packaging changes

**Independent Test**: Run `uv build` and verify dist/ contains .whl and .tar.gz files

### Implementation for User Story 4

- [ ] T025 [P] [US4] Document local wheel build commands in CLAUDE.md commands section
- [ ] T026 [P] [US4] Document cibuildwheel local testing in CLAUDE.md commands section

**Checkpoint**: Local build workflow documented for contributors

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Final validation and documentation

- [ ] T027 Run full quality checks: ruff check, ruff format, ty check
- [ ] T028 Build wheel locally and verify import works: uv build && pip install dist/*.whl
- [ ] T029 Validate all GitHub Actions workflows with act or push to test branch
- [ ] T030 Update CLAUDE.md Recent Changes section with packaging feature

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup - MANUAL steps that block PyPI publishing
- **User Story 1 (Phase 3)**: Can start after Setup - documentation only, no CI dependency
- **User Story 2 (Phase 4)**: Can start after Setup - CI workflows
- **User Story 3 (Phase 5)**: Depends on User Story 2 (test-command runs in release workflow)
- **User Story 4 (Phase 6)**: Can start after Setup - documentation only
- **Polish (Phase 7)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Independent - README updates only
- **User Story 2 (P2)**: Independent - CI workflow creation
- **User Story 3 (P2)**: Partially depends on US2 (test-command runs in cibuildwheel)
- **User Story 4 (P3)**: Independent - documentation only

### Parallel Opportunities

Within Setup:
- T004 can run parallel to T001-T003

Within User Story 2:
- T012-T018 are sequential (same file: release.yml)
- T019-T021 are sequential (same file: publish.yml)
- release.yml and publish.yml can be developed in parallel

Within User Story 4:
- T025 and T026 can run in parallel (documentation updates)

Across User Stories:
- US1, US2, and US4 can proceed in parallel after Setup
- US3 configuration (pyproject.toml) can start immediately, but testing requires US2

---

## Parallel Example: User Story 2

```bash
# These two workflow files can be created in parallel:
Task: "Create .github/workflows/release.yml with version tag trigger"
Task: "Create .github/workflows/publish.yml for manual production PyPI promotion"
```

---

## Implementation Strategy

### MVP First (User Story 1 + 2)

1. Complete Phase 1: Setup (pyproject.toml configuration)
2. Complete Phase 2: Foundational (Trusted Publisher setup - MANUAL)
3. Complete Phase 3: User Story 1 (README documentation)
4. Complete Phase 4: User Story 2 (release workflows)
5. **STOP and VALIDATE**: Push test tag, verify Test PyPI upload works
6. Promote to Production PyPI

### Incremental Delivery

1. Setup + Foundational → Package ready for distribution
2. Add US1 (documentation) → Users know how to install
3. Add US2 (CI workflows) → Automated releases
4. Add US3 (wheel testing) → Quality gate before publish
5. Add US4 (local build docs) → Contributors can test locally
6. Polish → Final cleanup

### Single Developer Strategy

Recommended order:
1. T001-T004 (Setup)
2. T005-T008 (Foundational - MANUAL, do these in browser)
3. T009-T011 (US1 - README)
4. T012-T021 (US2 - CI workflows)
5. T022-T024 (US3 - test configuration)
6. T025-T026 (US4 - documentation)
7. T027-T030 (Polish)

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Foundational phase (T005-T008) requires manual web browser interaction
- Test tag (e.g., v0.0.1-test) recommended before first real release
- Commit after each task or logical group
- Verify CI workflows work with test tags before relying on them
