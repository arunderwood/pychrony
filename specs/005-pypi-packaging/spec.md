# Feature Specification: PyPI Packaging and Distribution

**Feature Branch**: `005-pypi-packaging`
**Created**: 2026-01-16
**Status**: Draft
**Input**: User description: "Phase 5: Packaging and Distribution (Wheels and PyPI) - Finalize the project for distribution by building binary wheels and source distributions, enabling easy installation via pip install. Set up CI workflows to build distribution artifacts on each release and publish to PyPI."

## Clarifications

### Session 2026-01-16

- Q: What package integrity/publishing authentication strategy should be used? → A: Trusted Publishers (OIDC) - no API token needed, cryptographic proof of GitHub origin
- Q: Should releases be staged on Test PyPI before production? → A: Yes - all releases publish to Test PyPI first, then manually promote to PyPI
- Q: Which Linux architectures should be supported in initial release? → A: x86_64 + arm64 - build wheels for both architectures from initial release

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Install Package via pip (Priority: P1)

A developer wants to install pychrony in their Python project without cloning the repository or manually building from source. They should be able to run a single pip command to install the package and immediately use it.

**Why this priority**: This is the core value proposition of packaging - making the library accessible to users via standard Python tooling. Without this, users must build from source.

**Independent Test**: Can be fully tested by running `pip install pychrony` in a fresh virtual environment and importing the package successfully.

**Acceptance Scenarios**:

1. **Given** a fresh Python 3.10+ virtual environment on Linux, **When** user runs `pip install pychrony`, **Then** the package installs successfully without errors
2. **Given** pychrony is installed, **When** user imports `from pychrony import get_tracking`, **Then** the import succeeds and the module is accessible
3. **Given** libchrony is installed on the system, **When** user calls `get_tracking()`, **Then** the function executes without import or linking errors

---

### User Story 2 - Automated Release Publishing (Priority: P2)

A maintainer wants to publish a new version of pychrony by creating a git tag. The CI system should automatically build wheels and source distributions and publish them to PyPI without manual intervention.

**Why this priority**: Automation reduces release friction and human error, enabling faster iteration and consistent releases.

**Independent Test**: Can be tested by creating a version tag and verifying that artifacts appear on PyPI (or Test PyPI for dry runs).

**Acceptance Scenarios**:

1. **Given** a maintainer pushes a version tag (e.g., `v0.1.0`), **When** CI workflow triggers, **Then** wheels and source distribution are built automatically
2. **Given** wheels are built successfully, **When** the release workflow completes, **Then** artifacts are uploaded to Test PyPI for validation
3. **Given** package is validated on Test PyPI, **When** maintainer triggers production promotion, **Then** artifacts are uploaded to production PyPI
4. **Given** the workflow fails, **When** a maintainer checks CI, **Then** clear error messages indicate what went wrong

---

### User Story 3 - Verify Package Works After Installation (Priority: P2)

A developer wants confidence that the installed wheel actually works in their environment. The package should be tested as part of the build process to catch packaging issues before release.

**Why this priority**: Testing installed wheels prevents publishing broken packages that fail at runtime despite passing source-level tests.

**Independent Test**: Can be tested by building a wheel, installing it in an isolated environment, and running the test suite against the installed package.

**Acceptance Scenarios**:

1. **Given** a wheel is built, **When** installed in a clean environment with libchrony, **Then** unit tests pass against the installed package
2. **Given** a source distribution is built, **When** a user installs from sdist, **Then** the package builds and installs correctly
3. **Given** the wheel is installed, **When** `python -c "from pychrony import get_tracking; print(get_tracking)"` runs, **Then** it outputs the function reference without errors

---

### User Story 4 - Build Wheels Locally (Priority: P3)

A developer or contributor wants to build wheels locally to test packaging changes before pushing to CI. They should be able to build distribution artifacts using standard tooling.

**Why this priority**: Local builds enable faster iteration on packaging changes without waiting for CI.

**Independent Test**: Can be tested by running the build command locally and verifying artifacts are created in the dist/ directory.

**Acceptance Scenarios**:

1. **Given** a developer has the source code, **When** they run the build command, **Then** wheel and sdist files are created in `dist/`
2. **Given** local build completes, **When** developer installs the local wheel, **Then** the package works correctly

---

### Edge Cases

- What happens when libchrony is not installed on the target system?
  - Package should install but provide a clear error message when CFFI binding functions are called
- What happens when attempting to install on unsupported Python versions?
  - pip should reject installation with a clear version incompatibility message
- What happens when building on a non-Linux platform?
  - Build should succeed for source distribution; wheel builds may require platform-specific handling
- What happens when network is unavailable during PyPI publish?
  - CI workflow should fail with a clear error and allow retry
- What happens when a version tag is created that already exists on PyPI?
  - PyPI rejects duplicate versions; CI should catch this and report clearly

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Package MUST be installable via `pip install pychrony` from PyPI
- **FR-002**: Package MUST include source distribution (sdist) and binary wheel artifacts
- **FR-003**: Wheel MUST be compatible with manylinux standard for Linux portability (x86_64 and arm64 architectures)
- **FR-004**: Package MUST include all Python source files, type stubs, and CFFI build scripts
- **FR-005**: Version MUST be derived from git tags using hatch-vcs (already configured)
- **FR-006**: CI MUST automatically build wheels on version tag pushes
- **FR-007**: CI MUST automatically publish to Test PyPI on successful release builds using Trusted Publishers (OIDC) authentication
- **FR-007a**: CI MUST support manual promotion from Test PyPI to production PyPI after validation
- **FR-008**: CI MUST run tests against built wheels before publishing
- **FR-009**: Package MUST declare Python 3.10+ as minimum version requirement
- **FR-010**: Package MUST declare cffi as runtime dependency
- **FR-011**: Package metadata MUST include accurate classifiers, description, and project URLs
- **FR-012**: README MUST provide clear installation instructions for pip users
- **FR-013**: README MUST document libchrony system dependency requirement
- **FR-014**: CI MUST upload build artifacts for inspection even on non-release builds
- **FR-015**: System MUST expose only read-only libchrony APIs
- **FR-016**: System MUST provide full type hints for all public interfaces
- **FR-017**: System MUST work on Linux as primary platform

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can install pychrony with a single `pip install pychrony` command
- **SC-002**: Package installs successfully on any manylinux-compatible Linux distribution
- **SC-003**: Installation completes without requiring users to compile any code (assuming system libchrony is present)
- **SC-004**: Time from git tag creation to PyPI availability is under 15 minutes
- **SC-005**: 100% of unit tests pass when run against the installed wheel
- **SC-006**: Package imports successfully on Python 3.10, 3.11, 3.12, 3.13, and 3.14
- **SC-007**: Source distribution can be built and installed on any Linux system with appropriate build tools
- **SC-008**: Package metadata is correctly displayed on PyPI project page

## Assumptions

- libchrony remains a system-level dependency; the wheel does not bundle it (LGPL licensing concerns and system integration requirements make bundling impractical)
- Users on Linux are expected to have libchrony installed via their package manager
- Initial release includes Linux x86_64 and arm64 architectures; other platforms (Windows, macOS) are out of scope
- Semantic versioning will be used starting at 0.1.0 for initial release
- PyPI publishing uses Trusted Publishers (OIDC) for authentication - no API tokens required; maintainer must configure the GitHub repository as a Trusted Publisher on PyPI
- cibuildwheel is the standard tool for building manylinux wheels in CI

## Out of Scope

- Windows or macOS wheel builds (chronyd is primarily Linux-focused)
- Bundling libchrony into the wheel (licensing and system integration concerns)
- Automatic dependency installation for libchrony (system package management varies)
- Pre-release or nightly build publishing
- Private package index support (PyPI only)
