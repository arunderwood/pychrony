# Research: Chrony Tracking Binding

**Feature**: 002-tracking-binding
**Date**: 2026-01-15
**Status**: Complete

## Research Questions Resolved

### 1. libchrony API for Tracking Data

**Decision**: Use libchrony's high-level introspection API with session-based access

**Rationale**: libchrony provides a stable high-level API that:
- Returns native C types (double, struct timespec, uint64_t) - no wire-format conversion needed
- Provides field access by name for version resilience
- Handles all protocol details internally
- Offers ABI stability without exposing internal struct layouts

**Alternatives Considered**:
- Direct RPY_Tracking struct access: Rejected - requires manual wire-format conversions, ABI fragile
- Direct protocol implementation: Rejected - reimplements what libchrony already does, violates constitution
- Using chronyc subprocess: Rejected - brittle parsing, inefficient, not Pythonic

### 2. libchrony High-Level API Functions

**Decision**: Use the following libchrony functions via CFFI

**API Surface** (from libchrony chrony.h):

```c
// Connection management
int chrony_open_socket(const char *address);
chrony_err chrony_init_session(chrony_session **session, int fd);
void chrony_deinit_session(chrony_session *session);

// Request tracking data
chrony_err chrony_request_report_number_records(chrony_session *s, const char *report);
chrony_err chrony_process_response(chrony_session *s);

// Field introspection - returns NATIVE C TYPES
int chrony_get_field_index(chrony_session *s, const char *name);
double chrony_get_field_float(chrony_session *s, int field);
struct timespec chrony_get_field_timespec(chrony_session *s, int field);
uint64_t chrony_get_field_uinteger(chrony_session *s, int field);
int64_t chrony_get_field_integer(chrony_session *s, int field);
const char *chrony_get_field_string(chrony_session *s, int field);
```

**Why This API**:
- `chrony_get_field_float()` returns `double` - no custom Float conversion needed
- `chrony_get_field_timespec()` returns `struct timespec` - standard C type
- `chrony_get_field_uinteger()` returns `uint64_t` - no special handling
- Field lookup by name provides resilience to field reordering across versions

**Sources verified:**
- https://gitlab.com/chrony/libchrony/-/blob/main/chrony.h
- https://gitlab.com/chrony/libchrony/-/blob/main/reports.h

### 3. Tracking Report Field Names

**Decision**: Use libchrony's canonical field names for the tracking report

**Field Names** (from libchrony reports.h):

| Field Name | C Type via API | Python Type | Description |
|------------|----------------|-------------|-------------|
| "reference id" | chrony_get_field_uinteger | int | NTP reference source identifier |
| "ip address" | chrony_get_field_string | str | IP address of reference source |
| "stratum" | chrony_get_field_uinteger | int | NTP hierarchy level (0-15) |
| "leap status" | chrony_get_field_uinteger | int | Leap second status |
| "reference time" | chrony_get_field_timespec | float | Last measurement timestamp |
| "current correction" | chrony_get_field_float | float | Current offset from reference |
| "last offset" | chrony_get_field_float | float | Offset at last measurement |
| "rms offset" | chrony_get_field_float | float | RMS of recent offsets |
| "frequency" | chrony_get_field_float | float | Clock frequency error in ppm |
| "residual frequency" | chrony_get_field_float | float | Residual frequency |
| "skew" | chrony_get_field_float | float | Estimated frequency error |
| "root delay" | chrony_get_field_float | float | Network path delay |
| "root dispersion" | chrony_get_field_float | float | Total dispersion |
| "last update interval" | chrony_get_field_float | float | Time since last update |

**No Custom Conversion Functions Required**:
- libchrony handles all wire-format conversions internally
- Float fields return `double` directly
- Timespec fields return `struct timespec` directly
- Integer fields return `uint64_t`/`int64_t` directly

### 4. Session Lifecycle Pattern

**Decision**: New session per `get_tracking()` call (stateless)

**Rationale**:
- Simple and robust - no stale connection issues
- Aligns with "monitoring only" principle (stateless queries)
- Socket connection overhead is negligible for monitoring use cases
- Clarified in spec: Session 2026-01-15

**Implementation Pattern**:
```python
def get_tracking(socket_path: str = DEFAULT_SOCKET) -> TrackingStatus:
    """Get current tracking status from chronyd."""
    fd = lib.chrony_open_socket(socket_path.encode())
    if fd < 0:
        raise ChronyConnectionError(f"Failed to connect to {socket_path}")

    session = ffi.new("chrony_session **")
    try:
        err = lib.chrony_init_session(session, fd)
        if err != 0:
            raise ChronyConnectionError(f"Session init failed: {err}")

        err = lib.chrony_request_report_number_records(session[0], b"tracking")
        if err != 0:
            raise ChronyDataError(f"Request failed: {err}")

        err = lib.chrony_process_response(session[0])
        if err != 0:
            raise ChronyDataError(f"Response processing failed: {err}")

        # Extract fields by name
        return _extract_tracking_fields(session[0])
    finally:
        if session[0] != ffi.NULL:
            lib.chrony_deinit_session(session[0])
```

### 5. Field Access Pattern

**Decision**: Lookup field index by name per request (no caching)

**Rationale**:
- Since we create a new session per call, caching provides no benefit
- Field lookup is a simple string comparison, not a performance concern
- Keeps implementation simple
- Clarified in spec: Session 2026-01-15

**Implementation Pattern**:
```python
def _get_float_field(session, name: str) -> float:
    """Get a float field by name, raising on missing field."""
    index = lib.chrony_get_field_index(session, name.encode())
    if index < 0:
        raise ChronyDataError(f"Field '{name}' not found (libchrony version mismatch?)")
    return lib.chrony_get_field_float(session, index)
```

### 6. CFFI Binding Pattern

**Decision**: Use CFFI API mode with ffi.set_source()

**Rationale** (per CFFI documentation recommendations):
- API mode is "massively faster" than ABI mode (compiled wrapper vs libffi)
- Compiler validates function signatures at build time, catching mismatches early
- ABI mode is "fraught with problems, particularly on non-Windows platforms"
- Industry standard approach (used by cryptography, psycopg3)
- Aligns with CFFI developers' recommendation: "C libraries are typically meant to be used with a C compiler"

**Build Requirements**:
- **libchrony-devel** (headers): Required at build/install time
- **gcc/clang**: C compiler for building extension
- **python3-devel**: Python headers for extension module
- **libchrony** (runtime): Required at runtime

**Installation Experience**:
```bash
# Install build and runtime dependencies
sudo dnf install libchrony libchrony-devel gcc python3-devel

# Install pychrony (compiles C extension)
pip install pychrony
```

**CFFI Build Script** (`src/pychrony/_core/_build_bindings.py`):
```python
from cffi import FFI

ffi = FFI()

ffi.cdef("""
// Opaque session handle
typedef struct chrony_session chrony_session;

// Error codes
typedef int chrony_err;

// Connection management
int chrony_open_socket(const char *address);
chrony_err chrony_init_session(chrony_session **session, int fd);
void chrony_deinit_session(chrony_session *session);

// Request/response
chrony_err chrony_request_report_number_records(chrony_session *s, const char *report);
chrony_err chrony_process_response(chrony_session *s);

// Field access - native C types
int chrony_get_field_index(chrony_session *s, const char *name);
double chrony_get_field_float(chrony_session *s, int field);
uint64_t chrony_get_field_uinteger(chrony_session *s, int field);
int64_t chrony_get_field_integer(chrony_session *s, int field);
const char *chrony_get_field_string(chrony_session *s, int field);

// Timespec for reference time
struct timespec {
    long tv_sec;
    long tv_nsec;
};
struct timespec chrony_get_field_timespec(chrony_session *s, int field);
""")

ffi.set_source(
    "pychrony._core._bindings",
    '#include <chrony.h>',
    libraries=["chrony"],
)

if __name__ == "__main__":
    ffi.compile(verbose=True)
```

**Usage** (compiled module):
```python
from pychrony._core._bindings import lib, ffi
```

**pyproject.toml Changes**:
```toml
[build-system]
requires = ["hatchling", "cffi>=1.14.0"]
build-backend = "hatchling.build"

[tool.hatch.build.hooks.custom]
# Build hook to compile CFFI extension
```

**CI/CD Requirements**:
- **cibuildwheel**: For building platform-specific wheels (Fedora 39/40, EPEL 9)
- **Pre-built wheels**: For users without build tools

**Alternatives Considered**:
- ABI mode (ffi.dlopen): Rejected - CFFI docs warn it's "fraught with problems", slower, no compile-time validation
- ctypes: Rejected - CFFI is constitution-mandated
- Direct struct access: Rejected - ABI fragile, requires manual conversions

### 7. Error Handling Strategy

**Decision**: Specific Python exception hierarchy with chrony_err mapping

**Rationale**:
- Spec requires "specific Python exceptions with clear error messages and error codes"
- chrony_err enum provides error codes from libchrony
- Missing fields (index < 0) indicate version mismatch
- Clarified in spec: Raise ChronyDataError on missing fields

**Exception Hierarchy**:
```
ChronyError (base)
├── ChronyConnectionError - socket/session failures
├── ChronyPermissionError - insufficient access rights
├── ChronyDataError - missing fields, invalid responses
└── ChronyLibraryError - libchrony not installed
```

### 8. Socket Connection Strategy

**Decision**: Default to Unix domain socket at `/run/chrony/chronyd.sock`

**Rationale**:
- Unix socket is standard local communication method
- Requires appropriate permissions (root or chrony group)
- Most secure option (local only)
- Fastest path (no network overhead)

**Fallback Path**: `/var/run/chrony/chronyd.sock` (older systems)

### 9. Testing Strategy (Docker-Based Integration)

**Decision**: Unit tests for pure Python logic + Docker-based integration tests with **tests running inside container**

**Rationale**:
- libchrony is NOT available for macOS (Linux packages only: Fedora, EPEL)
- Tests must run **inside** the container where libchrony is available
- Simple docker-compose preferred over TestContainers

**Testing Architecture**:
```
Local (macOS/Linux):
├── Unit tests        → Run natively with `uv run pytest tests/unit`
├── Contract tests    → Run natively with `uv run pytest tests/contract`
└── Integration tests → Run in Docker with `docker compose run test-integration`

CI (GitHub Actions):
└── All tests         → Run in Docker container with full libchrony environment
```

## Dependencies

### Build-Time Dependencies
- **CFFI**: Required to compile bindings (add to pyproject.toml build-requires)
- **libchrony-devel**: System headers for chrony.h (dnf install libchrony-devel)
- **gcc**: C compiler for building extension module
- **python3-devel**: Python headers for building extension

### Runtime Dependencies
- **CFFI**: Required for compiled bindings (add to pyproject.toml dependencies)
- **libchrony**: System library (dynamically linked at runtime)

### Development Dependencies
- **pytest**: Testing framework (already present)
- **pytest-cov**: Coverage reporting (already present)
- **cibuildwheel**: For building platform-specific wheels in CI

## Open Questions (None)

All technical questions resolved through research.

## References

- [libchrony GitLab Repository](https://gitlab.com/chrony/libchrony)
- [libchrony chrony.h API](https://gitlab.com/chrony/libchrony/-/blob/main/chrony.h)
- [libchrony reports.h](https://gitlab.com/chrony/libchrony/-/blob/main/reports.h)
- [libchrony-devel package (EPEL)](https://rpmfind.net/linux/RPM/epel/9/x86_64/Packages/l/libchrony-devel-0.1-1.el9.x86_64.html)
- [chrony Documentation](https://chrony-project.org/doc/4.3/chronyc.html)
- [CFFI Documentation](https://cffi.readthedocs.io/en/latest/using.html)
- [CFFI ABI vs API Mode](https://cffi.readthedocs.io/en/stable/overview.html#id27) - Recommends API mode
