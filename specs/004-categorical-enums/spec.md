# Feature Specification: Python Enums for Categorical Fields

**Feature Branch**: `004-categorical-enums`
**Created**: 2026-01-16
**Status**: Draft
**Input**: Add Python enum classes (LeapStatus, SourceState, SourceMode) for categorical fields in pychrony dataclasses to improve type safety and IDE autocomplete

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Check Source Synchronization State (Priority: P1)

As a developer using pychrony, I want to check if a time source is currently selected for synchronization using a named enum value, so that my code is self-documenting and I don't need to remember magic numbers.

**Why this priority**: This is the most common operation - determining which source chrony is using for time synchronization. Using magic numbers (e.g., `if source.state == 0`) is error-prone and unclear.

**Independent Test**: Can be fully tested by importing SourceState enum, calling get_sources(), and comparing source.state to SourceState.SELECTED. Delivers clearer, type-safe code.

**Acceptance Scenarios**:

1. **Given** a developer has imported SourceState from pychrony, **When** they access source.state on a Source object, **Then** the value is a SourceState enum member (not an integer)
2. **Given** a source is selected for synchronization, **When** the developer checks `source.state == SourceState.SELECTED`, **Then** the comparison returns True
3. **Given** a developer types `SourceState.` in their IDE, **When** autocomplete triggers, **Then** all valid states (SELECTED, NONSELECTABLE, FALSETICKER, JITTERY, UNSELECTED, SELECTABLE) are shown

---

### User Story 2 - Check Leap Second Status (Priority: P2)

As a developer monitoring chrony, I want to check if a leap second insertion or deletion is pending using named enum values, so I can write clear conditional logic.

**Why this priority**: Leap second handling is important for time-critical applications. The current integer values (0-3) are cryptic without documentation.

**Independent Test**: Can be tested by importing LeapStatus, calling get_tracking(), and checking tracking.leap_status against LeapStatus.INSERT or LeapStatus.DELETE.

**Acceptance Scenarios**:

1. **Given** a developer has imported LeapStatus from pychrony, **When** they access tracking.leap_status on a TrackingStatus object, **Then** the value is a LeapStatus enum member
2. **Given** chrony reports leap_status=1, **When** the developer checks `tracking.leap_status == LeapStatus.INSERT`, **Then** the comparison returns True
3. **Given** a developer uses a switch/match statement on leap_status, **When** type checking runs, **Then** exhaustiveness checking works correctly with all enum members

---

### User Story 3 - Identify Source Type (Priority: P3)

As a developer, I want to distinguish between NTP clients, peers, and reference clocks using the SourceMode enum, so I can filter or display sources by type.

**Why this priority**: Source mode is less frequently queried than state, but still benefits from clear naming.

**Independent Test**: Can be tested by importing SourceMode, iterating sources, and grouping by source.mode values (CLIENT, PEER, REFCLOCK).

**Acceptance Scenarios**:

1. **Given** a source is configured as a reference clock, **When** the developer checks `source.mode == SourceMode.REFCLOCK`, **Then** the comparison returns True
2. **Given** a developer iterates over sources and groups by mode, **When** they use mode.name for display, **Then** meaningful names ("CLIENT", "PEER", "REFCLOCK") are shown

---

### Edge Cases

- What happens when libchrony returns an integer value outside the known enum range (e.g., state=6)?
  - Behavior: Enum construction raises ValueError, caught and re-raised as ChronyDataError with descriptive message

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Library MUST provide LeapStatus enum with members NORMAL (0), INSERT (1), DELETE (2), UNSYNC (3)
- **FR-002**: Library MUST provide SourceState enum with members SELECTED (0), NONSELECTABLE (1), FALSETICKER (2), JITTERY (3), UNSELECTED (4), SELECTABLE (5)
- **FR-003**: Library MUST provide SourceMode enum with members CLIENT (0), PEER (1), REFCLOCK (2)
- **FR-004**: TrackingStatus.leap_status field MUST have type LeapStatus
- **FR-005**: Source.state field MUST have type SourceState
- **FR-006**: Source.mode field MUST have type SourceMode
- **FR-007**: All enum classes MUST be exported from the pychrony package
- **FR-008**: Enum classes MUST use standard library `enum.Enum` (not IntEnum - no backward compatibility needed)
- **FR-009**: Invalid enum values from libchrony MUST raise ChronyDataError with descriptive message
- **FR-010**: Existing Source.mode_name and Source.state_name properties MUST be removed (enum.name provides equivalent functionality; no deprecation period needed for pre-1.0 software)

### Key Entities

- **LeapStatus**: Represents NTP leap second indicator status. Values indicate whether time is normal, or if a leap second will be inserted/deleted at midnight, or if the clock is unsynchronized.
- **SourceState**: Represents the selection state of a time source. Indicates whether chrony has selected this source for synchronization, rejected it, or considers it a candidate.
- **SourceMode**: Represents the operational mode of a time source. Distinguishes between NTP client connections, peer relationships, and local reference clocks.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Developers can identify source selection state without consulting documentation (enum names are self-explanatory)
- **SC-002**: IDE autocomplete shows all valid enum values when typing `SourceState.`
- **SC-003**: All existing unit, contract, and integration tests pass after migration to enums
- **SC-004**: Type checkers (mypy, ty) correctly infer enum types for the affected fields

## Clarifications

### Session 2026-01-16

- Q: Should Source.mode_name and Source.state_name properties be deprecated with warnings or removed completely? → A: Remove completely (clean break, pre-1.0 software has no backward compatibility obligation)

## Assumptions

- Enum from Python's standard library provides sufficient functionality (no third-party enum library needed)
- The integer values assigned by libchrony are stable and match chrony documentation
- Removing mode_name and state_name properties is confirmed acceptable (pre-1.0, enum.name provides equivalent functionality)
- chrony will not add new state/mode values that would break enum definitions (if this happens, the library will raise ChronyDataError)
- No backward compatibility is required (pre-1.0, no consumers yet)
