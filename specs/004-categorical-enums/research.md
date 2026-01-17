# Research: Python Enums for Categorical Fields

**Branch**: `004-categorical-enums` | **Date**: 2026-01-16

## Research Questions

### 1. Enum vs IntEnum: Which is appropriate?

**Decision**: Use `Enum` from the standard library (not IntEnum)

**Rationale**:
- No consumers exist yet (pre-1.0), so no backward compatibility needed
- Regular Enum is simpler and more type-safe
- Prevents accidental integer comparisons (`state == 0` is always False, forcing proper enum usage)
- Cleaner API design from the start

**Alternatives Considered**:
- `enum.IntEnum`: Adds complexity for backward compatibility we don't need
- `enum.IntFlag`: Inappropriate, these are not bitfields (except `Source.flags`)
- Third-party libraries (aenum, etc.): Adds dependency, not needed

### 2. Where should enum conversion happen?

**Decision**: Convert integers to enums in `_bindings.py` during dataclass construction

**Rationale**:
- Single point of conversion in the data extraction layer
- Validation already happens here via `_validate_tracking()` and `_validate_source()`
- Dataclass fields are typed as enums, providing IDE support

**Implementation**:
```python
# In _bindings.py, after extracting raw integer
data["leap_status"] = LeapStatus(raw_leap_status)
data["state"] = SourceState(raw_state)
data["mode"] = SourceMode(raw_mode)
```

**Alternatives Considered**:
- Convert in model `__post_init__`: Would require mutable dataclass or complex init
- Convert lazily via property: Would change field type signature

### 3. How to handle unknown enum values from libchrony?

**Decision**: Catch `ValueError` from enum construction and re-raise as `ChronyDataError`

**Rationale**:
- Unknown values indicate ABI mismatch between libchrony and pychrony
- Spec FR-009 requires `ChronyDataError` with descriptive message
- User can update pychrony or report issue if new values added to chrony

**Implementation**:
```python
try:
    data["state"] = SourceState(raw_state)
except ValueError:
    raise ChronyDataError(
        f"Unknown source state value {raw_state}. "
        "This may indicate a newer chrony version - please update pychrony."
    )
```

**Alternatives Considered**:
- Return raw integer: Defeats purpose of type safety
- Add `UNKNOWN` member: Complicates exhaustiveness checking
- Use `_missing_` hook: Same as UNKNOWN, loses specific value info

### 4. Existing validation changes

**Decision**: Remove redundant validation for enum-converted fields

**Rationale**:
- Current code validates `0 <= leap_status <= 3`, `0 <= state <= 5`, `0 <= mode <= 2`
- Enum construction inherently validates these bounds (raises ValueError for unknown)
- Validation logic can be simplified

**Implementation**:
- Remove `_validate_bounded_int` calls for leap_status, state, mode
- Enum construction in extraction functions handles validation

### 5. Property removal (mode_name, state_name)

**Decision**: Remove properties completely (per spec clarification)

**Rationale**:
- Pre-1.0 software has no backward compatibility obligation
- `enum.name` provides identical functionality: `source.state.name` → "SELECTED"
- Reduces code surface area

**Impact**:
- Update docstrings to mention `.name` attribute
- No deprecation warnings needed

### 6. Enum member naming conventions

**Decision**: Use uppercase names matching chrony terminology

**Rationale**:
- Python convention for enum members is UPPER_CASE
- Names should match chrony documentation for familiarity
- Existing property implementations confirm naming

**Enum Definitions**:
```python
class LeapStatus(Enum):
    NORMAL = 0      # Time is normal
    INSERT = 1      # Leap second will be inserted
    DELETE = 2      # Leap second will be deleted
    UNSYNC = 3      # Clock is unsynchronized

class SourceState(Enum):
    SELECTED = 0     # Currently selected for sync
    NONSELECTABLE = 1  # Cannot be selected
    FALSETICKER = 2  # Detected as false ticker
    JITTERY = 3      # Too much jitter
    UNSELECTED = 4   # Not currently selected
    SELECTABLE = 5   # Candidate for selection

class SourceMode(Enum):
    CLIENT = 0       # NTP client mode
    PEER = 1         # NTP peer mode
    REFCLOCK = 2     # Reference clock
```

### 7. Test coverage requirements

**Decision**: Comprehensive testing at all levels

**Unit Tests**:
- Enum instantiation from valid integers
- Enum `.name` and `.value` attributes
- ValueError for unknown values
- Exhaustiveness in match statements (Python 3.10+)

**Contract Tests**:
- Field type verification (isinstance checks)
- API stability (enum exports from package)

**Integration Tests**:
- End-to-end enum values from running chronyd
- Verify actual chrony values map correctly

## Dependencies

None - using Python standard library `enum.Enum`

## Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| New chrony versions add enum values | Low | Medium | ChronyDataError with clear message, update pychrony |
| Users depend on mode_name/state_name | Low | Low | Pre-1.0, breaking changes expected; clear changelog |
