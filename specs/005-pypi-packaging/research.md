# Research: PyPI Packaging and Distribution

**Feature Branch**: `005-pypi-packaging`
**Date**: 2026-01-16

## Research Topics

1. cibuildwheel configuration for manylinux wheels with CFFI bindings
2. PyPI Trusted Publishers (OIDC) for GitHub Actions
3. Two-stage publishing workflow (Test PyPI → Production PyPI)

---

## 1. cibuildwheel Configuration

### Decision
Use cibuildwheel with manylinux_2_28 images for both x86_64 and arm64 architectures. Install libchrony-devel via `before-all` hook using dnf.

### Rationale
- manylinux_2_28 is the current standard (RHEL 9 / Fedora 40 based)
- Uses `dnf` package manager (not yum)
- Supports both x86_64 and aarch64 natively
- `before-all` runs once per container, ideal for system dependencies
- Auditwheel automatically repairs wheels and bundles system libraries

### Configuration
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

### Alternatives Considered
| Alternative | Reason Rejected |
|-------------|-----------------|
| manylinux2014 | Being deprecated by 2025, uses older yum |
| before-build instead of before-all | Would reinstall system deps per Python version (wasteful) |
| Bundling libchrony statically | LGPL licensing concerns, system integration issues |

---

## 2. PyPI Trusted Publishers (OIDC)

### Decision
Use Trusted Publishers for both Test PyPI and Production PyPI. No API tokens stored in GitHub secrets.

### Rationale
- Eliminates long-lived API tokens (security risk)
- Short-lived OIDC tokens (15-minute validity)
- Cryptographic proof of GitHub origin
- Automatic Sigstore attestations
- Audit trail linking packages to source commits

### Configuration Steps
1. **PyPI Setup** (pypi.org/manage/projects/):
   - Add trusted publisher for `pychrony`
   - Repository: `arunderwood/pychrony`
   - Workflow: `.github/workflows/release.yml`
   - Environment: `pypi`

2. **Test PyPI Setup** (test.pypi.org/manage/projects/):
   - Same configuration with environment: `testpypi`

### Required Permissions
```yaml
permissions:
  id-token: write   # Required for OIDC token generation
  contents: read    # Required to read repository
```

### Alternatives Considered
| Alternative | Reason Rejected |
|-------------|-----------------|
| Long-lived API tokens | Permanent security risk, rotation burden |
| Username/password | Highest security risk, legacy approach |

---

## 3. Two-Stage Publishing Workflow

### Decision
Automatic publish to Test PyPI on version tags. Manual workflow_dispatch trigger for production PyPI promotion.

### Rationale
- Test PyPI catches packaging issues before production
- PyPI rejects duplicate versions (no re-uploads)
- Manual gate provides safety for production releases
- Can validate installation from Test PyPI before promoting

### Workflow Structure
```
1. Tag push (v0.1.0) → triggers release.yml
2. release.yml:
   - Build wheels with cibuildwheel
   - Build sdist
   - Run tests on built wheels
   - Publish to Test PyPI (automatic)
   - Upload artifacts for manual inspection

3. Manual trigger → publish.yml
   - Download artifacts from release run
   - Publish to Production PyPI
```

### Alternatives Considered
| Alternative | Reason Rejected |
|-------------|-----------------|
| Direct to production | Risk of publishing broken packages |
| Parallel publish (both at once) | No validation step before production |
| Separate build in publish workflow | Duplication, risk of version mismatch |

---

## 4. Testing Strategy for Wheels

### Decision
Run unit and contract tests via cibuildwheel's test-command. Integration tests remain in Docker workflow (require running chronyd).

### Rationale
- cibuildwheel tests run in isolated container
- Tests import from installed wheel (not source)
- Integration tests need chronyd service (not available in cibuildwheel containers)
- Unit/contract tests verify packaging correctness

### Configuration
```toml
[tool.cibuildwheel]
test-requires = "pytest"
test-command = "python -m pytest {project}/tests/unit {project}/tests/contract -v"
```

### Alternatives Considered
| Alternative | Reason Rejected |
|-------------|-----------------|
| Run all tests in cibuildwheel | Integration tests require chronyd service |
| Skip testing in CI | Would publish untested wheels |
| venv in test-command | Unnecessary; cibuildwheel already isolates |

---

## 5. Build Artifacts and Versioning

### Decision
Keep existing hatch-vcs configuration for version from git tags. Build both wheel and sdist.

### Rationale
- hatch-vcs already configured and working
- Version derived from git tags (v0.1.0 → 0.1.0)
- sdist required for users building from source
- Wheel provides pre-built distribution

### Existing Configuration (unchanged)
```toml
[build-system]
requires = ["hatchling>=1.24.2", "hatch-vcs>=0.3", "cffi>=1.14.0"]
build-backend = "hatchling.build"

[tool.hatch.version]
source = "vcs"
fallback-version = "0.0.0.dev0"
```

---

## Summary of Decisions

| Aspect | Decision |
|--------|----------|
| **Wheel builder** | cibuildwheel with manylinux_2_28 |
| **Architectures** | x86_64 + aarch64 (arm64) |
| **System deps** | Install via before-all with dnf |
| **Authentication** | Trusted Publishers (OIDC) |
| **Publishing** | Test PyPI auto, Production PyPI manual |
| **Testing** | Unit/contract in cibuildwheel, integration in Docker |
| **Versioning** | hatch-vcs from git tags (existing) |

---

## References

- [cibuildwheel Options Documentation](https://cibuildwheel.pypa.io/en/stable/options/)
- [PyPI Trusted Publishers](https://docs.pypi.org/trusted-publishers/)
- [pypa/gh-action-pypi-publish](https://github.com/pypa/gh-action-pypi-publish)
- [Python Packaging User Guide - GitHub Actions](https://packaging.python.org/guides/publishing-package-distribution-releases-using-github-actions-ci-cd-workflows/)
