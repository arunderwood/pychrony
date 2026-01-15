# Feature Specification: Python Bindings Scaffold and CI Setup

**Feature Branch**: `001-python-scaffold`  
**Created**: 2025-01-14  
**Status**: Draft  
**Input**: User description: "Phase 1: Initial Scaffold and CI Setup

Goals:

Establish the base repository structure for the Python bindings as an independent project (not embedded in any other repo).

Use uv for Python packaging, lay the groundwork.

Set up a minimal build system and project layout.

Integrate a basic Continuous Integration workflow (GitHub Actions) to run tests on supported Python versions, ensuring the scaffold is sound.

Key Deliverables:

Project Structure: A clear Python package layout under src/pychrony/ with an __init__.py and placeholder modules.

Build Configuration: A pyproject.toml file defining project metadata and build system requirements. This will declare the package name, version, authors, MIT license, modern uv-centric development dependencies (ruff, pytest, tox, ty), and specify a build backend. Even though this project will include a C binding, we will still use pyproject.toml for metadata per modern standards.

UV Version Management: Use .python-version file to specify the primary development Python version, while pyproject.toml defines the supported version matrix (3.10-3.14) for testing and distribution. UV uses .python-version for local development and respects pyproject.toml requires-python for package compatibility.

Testing Infrastructure: A tests/ directory with an initial test (e.g. a trivial test to ensure the package imports successfully). Use pytest as the primary testing framework with tox configuration for multi-environment testing, ensuring test commands work locally and in CI.

CI Workflow: A GitHub Actions workflow file (e.g. .github/workflows/ci.yml) set up to run on pushes/PRs. It should checkout the code, set up Python, install dependencies, and run the test suite. The CI will target Linux (Ubuntu runners) since the initial platform support is Linux. It will test against multiple Python versions (for example, 3.10 through 3.14) to ensure broad compatibility.

Testing Approach:

Focus on basic unit tests to validate the skeleton. For example, the dummy test can simply instantiate a class or call a stub function in the package. This ensures that the testing framework and CI are correctly configured.

No libchrony functionality is implemented in this phase, so tests will not yet touch the C library. Instead, they confirm the package can be built and imported. (If desired, placeholders for future tests can be added, marked as expected to fail or skipped.)

Ensure that test discovery works via pytest locally and via tox across environments, and that a test matrix can run without errors. This establishes a baseline to catch issues early in subsequent phases.

CI (GitHub Actions) Requirements:

Use a matrix of Python versions (e.g. 3.10, 3.11, 3.12, 3.13, 3.14) on Ubuntu to run tests. For each job, install the package (if build is needed) or at least ensure the package can be built. At this scaffold stage, the build may be purely Python (no C extension yet), which simplifies CI.

Configure the CI to run tox to execute the test suite across all Python versions, ensuring one command runs tests across all environments.

Set up status checks: the CI should fail the entire build if any Python version in the matrix fails, ensuring consistent quality across all supported versions. Even at this phase, this gives a baseline "green" build that future changes must uphold."

## Clarifications

### Session 2025-01-14

- Q: What should be the exact package name for the Python bindings? → A: pychrony (aligned with repo/project name for consistency)
- Q: Which testing framework should be used as primary and how should pytest/tox work together? → A: pytest as primary, tox for multi-environment testing
- Q: How should CI handle test failures across the Python version matrix? → A: Fail entire build if any version fails (standard CI practice)
- Q: What development dependencies should be included for the uv-based project? → A: Modern uv-centric stack (ruff, pytest, tox, ty)
- Q: What import statement should be referenced in test scenario for consistency? → A: import pychrony (matches established package name)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Package Import Validation (Priority: P1)

Developers need to verify that the pychrony package structure is correct and can be imported successfully without any libchrony dependencies.

**Why this priority**: This is the foundational requirement that validates the entire scaffold setup. Without successful imports, no further development can proceed.

**Independent Test**: Can be fully tested by creating a fresh Python environment and running `import pychrony` successfully, delivering confidence that the basic package structure works.

**Acceptance Scenarios**:

1. **Given** a fresh Python environment, **When** a developer runs `import pychrony`, **Then** the import succeeds without errors
2. **Given** the package is installed, **When** a developer accesses pychrony.__version__, **Then** a valid version string is returned

---

### User Story 2 - Local Test Execution (Priority: P1)

Developers need to run tests locally to validate their changes before committing to ensure the testing infrastructure works correctly.

**Why this priority**: Local testing is essential for developer productivity and CI reliability. Developers must be able to catch issues early.

**Independent Test**: Can be fully tested by running `pytest tests/` in the repository root and observing all tests pass, delivering a working local development workflow.

**Acceptance Scenarios**:

1. **Given** the project setup is complete, **When** a developer runs `pytest tests/`, **Then** all tests execute and pass
2. **Given** the testing infrastructure, **When** tests discover the test suite, **Then** both placeholder and import tests are found and executed

---

### User Story 3 - CI Validation (Priority: P2)

Developers need assurance that their changes work across multiple Python versions through automated CI checks.

**Why this priority**: Ensures cross-Python compatibility and provides automated quality gates, though local testing is more critical for initial development.

**Independent Test**: Can be fully tested by submitting a PR and observing GitHub Actions successfully run the test matrix across all Python versions, delivering confidence in cross-version compatibility.

**Acceptance Scenarios**:

1. **Given** a pull request is submitted, **When** GitHub Actions workflow runs, **Then** tests pass on all specified Python versions
2. **Given** the CI workflow, **When** the Python version matrix executes, **Then** each version installs dependencies and runs tests successfully

---

### Edge Cases

**Unsupported Python Version**:
- **Detection**: pyproject.toml requires-python field validation during install
- **Handling**: Clear error message: `[pychrony] Build: Python X.Y not supported - requires Python 3.10-3.14`
- **Test Coverage**: Verify install fails on Python 3.9 and succeeds on 3.10+

**CI Test Failures**:
- **Detection**: GitHub Actions matrix job failure
- **Handling**: Fail-fast behavior stops entire build, log job-specific failure
- **Test Coverage**: Simulate failure in one Python version, verify build stops

**Malformed Package Structure**:
- **Detection**: Import errors during package initialization
- **Handling**: Structured error with missing component details
- **Test Coverage**: Test with missing __init__.py and other critical files

**Missing Dependencies**:
- **Detection**: Import-time dependency resolution failure
- **Handling**: Error indicates specific missing dependency and installation command
- **Test Coverage**: Test behavior with pytest, ruff, tox unavailable

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide a proper Python package structure under src/pychrony/
- **FR-002**: System MUST include an __init__.py file with package metadata
- **FR-003**: System MUST provide a pyproject.toml file with complete project metadata including MIT license and uv-centric development dependencies
- **FR-004**: System MUST use uv as the Python packaging tool
- **FR-005**: System MUST provide a tests/ directory with pytest configuration as primary framework
- **FR-006**: System MUST include at least one working test that validates package import
- **FR-007**: System MUST provide a GitHub Actions workflow file for CI
- **FR-008**: System MUST test against Python versions 3.10, 3.11, 3.12, 3.13, and 3.14
- **FR-009**: System MUST run on Ubuntu runners in CI environment with fail-fast behavior on any version failure
- **FR-010**: System MUST support local test execution via pytest
- **FR-011**: System MUST include placeholder modules for future libchrony bindings
- **FR-012**: System MUST provide clear error messages following pychrony error format standards

#### Error Message Standards
- **Format**: `[pychrony] <component>: <specific error message>`
- **Component**: Import, Test, Build, or CI
- **Examples**: 
  - `[pychrony] Import: Failed to load pychrony package - check installation`
  - `[pychrony] Test: No tests found in tests/ directory`
  - `[pychrony] Build: pyproject.toml missing required metadata`
- **Consistency**: All error messages follow this pattern for easy parsing

### Key Entities *(include if feature involves data)*

- **Python Package**: The pychrony package structure containing the public API
- **Build Configuration**: pyproject.toml metadata and build system setup
- **Test Suite**: pytest-based tests validating package functionality
- **CI Workflow**: GitHub Actions configuration for automated testing
- **Package Metadata**: Version, author, MIT license, and uv-centric development dependency information

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Developers can successfully import the pychrony package within 30 seconds in a fresh environment
- **SC-002**: Local test execution completes in under 2 minutes on a standard development machine
- **SC-003**: CI workflow successfully runs the full test matrix across all 5 Python versions within 10 minutes
- **SC-004**: Package structure follows Python packaging standards without errors
- **SC-005**: Zero test failures in the initial scaffold when running on all supported Python versions
