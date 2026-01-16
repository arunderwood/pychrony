# Data Model

## Core Entities

### PythonPackage
**Description**: The pychrony package structure containing public API  
**Fields**:
- name: "pychrony" (string)
- version: Semantic version (string, dynamic from VCS)
- description: Package description (string)
- author: Package author information (object)
- license: MIT (string)
- python_requires: >=3.10 (string)

### CLibraryBinding
**Description**: CFFI interface to libchrony system library  
**Fields**:
- library_name: "libchrony" (string)
- library_version: Minimum required version (string)
- ffi_interface: CFFI definition object
- functions: Available C functions (array)
- error_handling: Error mapping strategy (enum)
- memory_management: GC strategy (boolean)

### TestSuite
**Description**: Test configuration and execution framework  
**Fields**:
- framework: "pytest" (string)
- coverage_tool: "pytest-cov" (string)
- environments: Python version matrix (array)
- integration_paths: System library test paths (array)

### CIWorkflow
**Description**: GitHub Actions automation for testing and publishing  
**Fields**:
- python_versions: ["3.10", "3.11", "3.12", "3.13", "3.14"] (array)
- target_platform: "ubuntu-latest" (string)
- fail_fast: true (boolean)
- cache_strategy: UV-based (object)

## Relationships

```
PythonPackage 1..* --contains--> CLibraryBinding
CLibraryBinding 1..1 --binds_to--> libchrony_system
TestSuite 1..* --tests--> PythonPackage
CIWorkflow 1..* --validates--> PythonPackage
```

## Validation Rules

### Package Validation
- name follows Python naming conventions
- version format complies with semantic versioning
- license is compatible with libchrony (LGPL)
- metadata required fields are complete

### CFFI Validation
- library loading handles platform differences
- error codes are properly mapped to Python exceptions
- memory management prevents leaks
- function signatures match libchrony API

### Testing Validation
- test coverage > 80% for new code
- all Python versions in matrix execute
- integration tests use real system library
- unit tests use mocked library

### CI Validation
- all matrix jobs complete successfully
- fail-fast behavior works correctly
- dependency caching functions properly
- publishing only occurs on main branch
