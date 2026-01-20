# Tasks: API Documentation with GitHub Pages

**Input**: Design documents from `/specs/007-api-docs-github-pages/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, quickstart.md, contracts/

**Tests**: No test tasks included - documentation infrastructure does not require traditional unit/integration tests. Validation is done via local build verification and CI workflow.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

- Documentation config: `mkdocs.yml` at repository root
- Documentation source: `docs/` directory
- CI workflow: `.github/workflows/docs.yml`
- No changes to existing source code in `src/pychrony/`

---

## Phase 1: Setup (Documentation Infrastructure)

**Purpose**: Initialize MkDocs project structure and configuration

- [x] T001 Add mike to docs dependency group in pyproject.toml
- [x] T002 Create docs/ directory structure with mkdir -p docs/api
- [x] T003 Create MkDocs configuration file at mkdocs.yml

**Checkpoint**: Documentation project structure exists, ready for content

---

## Phase 2: Foundational (Basic Documentation Build)

**Purpose**: Core documentation content that MUST be complete before versioning or CI can work

**⚠️ CRITICAL**: User story implementation requires documentation to build successfully first

- [x] T004 Create documentation homepage at docs/index.md
- [x] T005 Create API reference page at docs/api/index.md with all public exports
- [x] T006 Verify local documentation build with uv run mkdocs build --strict
- [x] T007 [P] Verify local documentation serves with uv run mkdocs serve

**Checkpoint**: Documentation builds locally and renders all API items correctly

---

## Phase 3: User Story 1 - Developer Discovers API Reference (Priority: P1) 🎯 MVP

**Goal**: A developer can visit the documentation site and view complete API reference with descriptions, parameters, return types, and examples.

**Independent Test**: Navigate to GitHub Pages URL, verify all public classes/methods are documented with their docstring content.

### Implementation for User Story 1

- [x] T008 [US1] Deploy initial documentation to GitHub Pages using mike deploy --push main
- [x] T009 [US1] Set default version redirect with mike set-default --push main
- [x] T010 [US1] Add documentation link to README.md pointing to GitHub Pages URL
- [x] T011 [US1] Verify deployed site shows all API items (ChronyConnection, TrackingStatus, Source, etc.)
- [x] T012 [US1] Verify search functionality works on deployed site

**Checkpoint**: User Story 1 complete - developers can discover and browse API documentation

---

## Phase 4: User Story 2 - Developer Browses Module Structure (Priority: P2)

**Goal**: Documentation shows clear module hierarchy with Connection, Data Models, Exceptions, and Testing Utilities sections.

**Independent Test**: Navigate to documentation site, verify navigation shows organized sections matching pychrony's module structure.

### Implementation for User Story 2

- [x] T013 [US2] Update docs/api/index.md to add section headings (Connection, Data Models, Enums, Exceptions, Testing Utilities)
- [x] T014 [US2] Configure navigation in mkdocs.yml with nested structure for API sections
- [x] T015 [US2] Rebuild and redeploy documentation with updated structure
- [x] T016 [US2] Verify navigation displays organized module hierarchy on deployed site

**Checkpoint**: User Story 2 complete - module structure is clear and navigable

---

## Phase 5: User Story 3 - Developer Views Documentation for Specific Version (Priority: P2)

**Goal**: Documentation site provides version selector with all tagged releases plus "main", defaulting to latest tagged release.

**Independent Test**: Select a specific version from version selector, verify documentation matches that release's API.

### Implementation for User Story 3

- [x] T017 [US3] Configure version provider in mkdocs.yml with extra.version.provider: mike
- [x] T018 [US3] Add theme features for version selector dropdown in mkdocs.yml
- [x] T019 [US3] Rebuild documentation with version configuration
- [x] T020 [US3] Verify version selector appears in deployed documentation header
- [x] T021 [US3] Test version switching functionality (main version initially, then tagged releases when available)

**Checkpoint**: User Story 3 complete - version selector works and displays available versions

---

## Phase 6: User Story 4 - Documentation Stays Current with Releases (Priority: P3)

**Goal**: CI workflow automatically rebuilds and deploys documentation on main branch changes and new tag creation.

**Independent Test**: Push to main or create a tag, verify documentation is updated within 10 minutes.

### Implementation for User Story 4

- [x] T022 [US4] Create GitHub Actions workflow file at .github/workflows/docs.yml
- [x] T023 [US4] Configure workflow trigger for push to main branch
- [x] T024 [US4] Configure workflow trigger for push of v* tags
- [x] T025 [US4] Add workflow job for Python setup and dependency installation
- [x] T026 [US4] Add workflow step to deploy main docs on main branch push
- [x] T027 [US4] Add workflow step to deploy versioned docs on tag push with latest alias
- [x] T028 [US4] Configure workflow permissions for contents: write
- [ ] T029 [US4] Test workflow by pushing to main branch
- [ ] T030 [US4] Verify CI deploys documentation automatically

**Checkpoint**: User Story 4 complete - documentation updates automatically on changes

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Final improvements and validation

- [x] T031 [P] Update README.md with documentation badge/link in prominent position
- [x] T032 [P] Add GitHub repository metadata (About section) with documentation URL
- [x] T033 Validate all success criteria from spec.md (SC-001 through SC-008)
- [x] T034 Run quickstart.md validation steps to confirm deployment

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational - initial deployment
- **User Story 2 (Phase 4)**: Can start after Phase 2, independent of US1
- **User Story 3 (Phase 5)**: Can start after Phase 2, independent of US1/US2
- **User Story 4 (Phase 6)**: Depends on US1 (docs must be deployed first before CI can update)
- **Polish (Phase 7)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Depends on Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Depends on Foundational (Phase 2) - Independent of US1
- **User Story 3 (P2)**: Depends on Foundational (Phase 2) - Independent of US1/US2
- **User Story 4 (P3)**: Depends on US1 (documentation must be deployed before CI can update it)

### Within Each User Story

- Configuration changes before deployment
- Deployment before verification
- Local testing before remote deployment where applicable

### Parallel Opportunities

- T006 and T007 can run in parallel (build vs serve)
- T031 and T032 can run in parallel (different files)
- User Stories 2 and 3 can start in parallel after Foundational phase (if team capacity allows)

---

## Parallel Example: Setup and Foundational

```bash
# Phase 1 tasks are sequential (each builds on previous)
# Phase 2 - after T005 completes:
Task: "T006 Verify local documentation build with uv run mkdocs build --strict"
Task: "T007 [P] Verify local documentation serves with uv run mkdocs serve"
# These can run in parallel
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T003)
2. Complete Phase 2: Foundational (T004-T007)
3. Complete Phase 3: User Story 1 (T008-T012)
4. **STOP and VALIDATE**: API documentation is live and browsable
5. Demo: Developers can now discover and use pychrony API documentation

### Incremental Delivery

1. Setup + Foundational → Documentation builds locally
2. Add User Story 1 → Documentation live on GitHub Pages (MVP!)
3. Add User Story 2 → Better organization and navigation
4. Add User Story 3 → Version selector functional
5. Add User Story 4 → Automated CI deployment
6. Each story adds value without breaking previous stories

### Recommended Execution Order

For single developer:
1. T001 → T002 → T003 (Setup)
2. T004 → T005 → T006/T007 (Foundational)
3. T008 → T009 → T010 → T011 → T012 (US1 - MVP)
4. T013 → T014 → T015 → T016 (US2)
5. T017 → T018 → T019 → T020 → T021 (US3)
6. T022-T030 (US4 - CI automation)
7. T031-T034 (Polish)

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story is independently completable after Foundational phase
- Local verification (mkdocs build --strict) catches most issues before deployment
- mike handles version management automatically - no manual directory management needed
- Avoid: deploying broken docs, skipping local verification, forgetting mike set-default
