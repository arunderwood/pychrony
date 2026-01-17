# Quickstart: PyPI Packaging Implementation

**Feature Branch**: `005-pypi-packaging`
**Date**: 2026-01-16

## Overview

This document provides a quickstart guide for implementing PyPI packaging and distribution for pychrony.

## Prerequisites

### For Local Development
- Python 3.10+
- uv package manager
- Docker (for local wheel testing)

### For PyPI Publishing (Maintainer Setup)
1. **Test PyPI Account**: Create at https://test.pypi.org/account/register/
2. **PyPI Account**: Create at https://pypi.org/account/register/
3. **Trusted Publisher Configuration**: See Setup section below

## Setup Steps

### 1. Configure Trusted Publishers

#### Test PyPI
1. Go to https://test.pypi.org/manage/account/publishing/
2. Add new pending publisher:
   - Project name: `pychrony`
   - Owner: `arunderwood`
   - Repository: `pychrony`
   - Workflow name: `release.yml`
   - Environment: `testpypi`

#### Production PyPI
1. Go to https://pypi.org/manage/account/publishing/
2. Add new pending publisher with same settings:
   - Environment: `pypi`

### 2. Configure GitHub Environments

1. Go to repository Settings → Environments
2. Create `testpypi` environment (no restrictions needed)
3. Create `pypi` environment:
   - Add required reviewers (optional, recommended)
   - Add deployment branch rule: only `main` or tags

## File Changes Required

### New Files
```
.github/workflows/release.yml   # Build wheels, publish to Test PyPI
.github/workflows/publish.yml   # Promote to Production PyPI
```

### Modified Files
```
pyproject.toml                  # Add [tool.cibuildwheel] configuration
README.md                       # Update installation instructions
```

## Local Development Commands

### Build Wheel Locally
```bash
# Build sdist and wheel
uv build

# Output in dist/
ls dist/
# pychrony-0.1.0.tar.gz
# pychrony-0.1.0-cp310-cp310-linux_x86_64.whl
```

### Test Local Wheel
```bash
# Install in fresh venv
python -m venv /tmp/test-wheel
source /tmp/test-wheel/bin/activate
pip install dist/pychrony-*.whl

# Verify import
python -c "from pychrony import get_tracking; print(get_tracking)"
```

### Build Manylinux Wheel (requires Docker)
```bash
# Install cibuildwheel
uv pip install cibuildwheel

# Build for current platform
cibuildwheel --platform linux

# Output in wheelhouse/
ls wheelhouse/
```

## Release Process

### 1. Create Version Tag
```bash
git tag -a v0.1.0 -m "Release v0.1.0"
git push origin v0.1.0
```

### 2. Monitor Release Workflow
- GitHub Actions → release.yml triggers automatically
- Builds wheels for x86_64 and arm64
- Publishes to Test PyPI

### 3. Validate on Test PyPI
```bash
pip install --index-url https://test.pypi.org/simple/ pychrony
python -c "from pychrony import get_tracking; print('OK')"
```

### 4. Promote to Production
- GitHub Actions → Manually trigger publish.yml
- Or: Use workflow_dispatch from Actions tab

### 5. Verify on PyPI
```bash
pip install pychrony
python -c "from pychrony import get_tracking; print('OK')"
```

## Troubleshooting

### Wheel Build Fails
- Ensure libchrony-devel is available in manylinux container
- Check CFFI compilation errors in CI logs
- Verify cffi is in build-system.requires

### PyPI Publish Fails with 403
- Verify Trusted Publisher configuration matches exactly
- Check workflow filename matches (release.yml vs publish.yml)
- Ensure environment name matches (pypi vs testpypi)

### Import Fails After Install
- Verify libchrony is installed on target system
- Check wheel platform matches (manylinux vs current system)
- Run `ldd` on _cffi_bindings*.so to check shared library deps

## Key Configuration Reference

### pyproject.toml cibuildwheel section
```toml
[tool.cibuildwheel]
build = "cp310-* cp311-* cp312-* cp313-* cp314-*"

[tool.cibuildwheel.linux]
archs = ["x86_64", "aarch64"]
manylinux-x86_64-image = "manylinux_2_28"
manylinux-aarch64-image = "manylinux_2_28"
before-all = "dnf install -y libchrony-devel libffi-devel"
test-requires = "pytest"
test-command = "python -m pytest {project}/tests/unit {project}/tests/contract -v"
```

### GitHub Actions permissions
```yaml
permissions:
  id-token: write   # Required for OIDC
  contents: read    # Required for checkout
```
