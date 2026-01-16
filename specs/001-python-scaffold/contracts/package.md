# API Contracts

## PyChrony Package API

### Package Interface

#### Package Metadata
```python
# src/pychrony/__init__.py
__version__: str  # Semantic version string
__author__: str   # Package author information
```

#### Import Validation
```python
def validate_import() -> bool:
    """Validate that pychrony package can be imported successfully"""
    return True  # Implementation placeholder
```

## Core Bindings Interface

### Library Connection
```python
class ChronyLibrary:
    """CFFI interface to libchrony system library"""
    
    def __init__(self, library_path: Optional[str] = None):
        """Initialize connection to libchrony"""
        
    def get_version(self) -> int:
        """Get libchrony version number"""
        
    def check_connection(self) -> bool:
        """Test if library is responsive"""
```

### Error Handling
```python
class ChronyError(Exception):
    """Base exception for pychrony errors"""
    
    def __init__(self, message: str, error_code: Optional[int] = None):
        super().__init__(message)
        self.error_code = error_code
```

## Testing Contracts

### Test Structure
```python
# tests/conftest.py
@pytest.fixture
def mock_chrony_library():
    """Mock libchrony for unit testing"""
    
@pytest.fixture
def temp_config_dir():
    """Temporary configuration for integration tests"""
```

### Test Scenarios
```python
def test_package_import():
    """Test 1: Package imports successfully"""
    
def test_version_accessibility():
    """Test 1: Version string accessible"""
    
def test_mock_library_interaction():
    """Test 2: Mock C library interaction"""
    
def test_error_handling():
    """Test 2: Error propagation works"""
```

## CI/CD Contracts

### Workflow Triggers
```yaml
on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]
```

### Job Contracts
```yaml
jobs:
  test:
    strategy:
      matrix:
        python-version: ["3.10", "3.11", "3.12", "3.13", "3.14"]
      fail-fast: true
    
    outputs:
      test-results: ${{ steps.test.outcome }}
```

### Quality Gates
```yaml
- name: Lint check
  if: success()
  
- name: Type check  
  if: success()
  
- name: Test coverage
  if: success()
```

## Development Tools Contracts

### Ruff Configuration
```toml
[tool.ruff]
target-version = "py310"
line-length = 88
```

### Ty Configuration
```toml
[tool.ty]
python_version = "3.10"
strict = true
```

### Pytest Configuration
```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py", "*_test.py"]
addopts = ["--cov=src", "--cov-report=term-missing"]
```

These contracts define the expected interfaces and behaviors for the pychrony package implementation.