# Feature Specification: Extend Bindings to Multiple Reports

**Feature Branch**: `003-multiple-reports-bindings`
**Created**: 2026-01-16
**Status**: Draft
**Input**: User description: "Phase 3: Extend Bindings to Multiple Reports (sources, sourcestats, rtcdata)"

## Clarifications

### Session 2026-01-16

- Q: When RTC tracking is unavailable, what should `get_rtc_data()` return? → A: Raise `ChronyDataError` with descriptive message (consistent with existing patterns)
- Q: How should source/sourcestats correlation work across calls? → A: Each function returns independent snapshot per libchrony behavior; user correlates by address if needed (libchrony is source of truth)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Query Time Sources (Priority: P1)

As a system administrator monitoring chronyd, I want to retrieve a list of all configured time sources (NTP servers/peers) and their current status so that I can verify which sources are being used and their health.

**Why this priority**: Time sources are the fundamental building blocks of NTP synchronization. Without visibility into sources, users cannot diagnose why synchronization is failing or verify that their NTP infrastructure is correctly configured. This is the most commonly needed report after tracking status.

**Independent Test**: Can be fully tested by calling `get_sources()` and verifying it returns a list of source objects with address, state, and stratum information. Delivers value by showing all configured NTP sources and their current states.

**Acceptance Scenarios**:

1. **Given** chronyd is running with one or more NTP sources configured, **When** I call `get_sources()`, **Then** I receive a list containing at least one source with its address, state, stratum, and polling interval
2. **Given** chronyd is running with no sources configured, **When** I call `get_sources()`, **Then** I receive an empty list (not an error)
3. **Given** chronyd is running with multiple sources, **When** I call `get_sources()`, **Then** each source in the list has a unique address and all required fields populated

---

### User Story 2 - Retrieve Source Statistics (Priority: P2)

As a system administrator, I want to retrieve detailed statistical data about each time source (offset measurements, jitter, delay) so that I can analyze the quality and reliability of each NTP source.

**Why this priority**: Source statistics provide deeper insight into source quality beyond basic state. This enables performance tuning and source selection decisions. Depends on understanding sources first (P1).

**Independent Test**: Can be fully tested by calling `get_source_stats()` and verifying statistical fields (offset, jitter, delay, std_dev) are present and contain numeric values within plausible ranges.

**Acceptance Scenarios**:

1. **Given** chronyd is running with sources that have accumulated measurements, **When** I call `get_source_stats()`, **Then** I receive statistics for each source including sample count, offset, and jitter values
2. **Given** chronyd has just started and sources have no measurements yet, **When** I call `get_source_stats()`, **Then** I receive statistics with zero or minimal sample counts (not an error)
3. **Given** chronyd is running, **When** I call `get_source_stats()`, **Then** all numeric fields (offset, jitter, std_dev) are finite numbers (not NaN or Inf)

---

### User Story 3 - Query RTC Data (Priority: P3)

As a system administrator, I want to retrieve Real-Time Clock (RTC) information including its offset from system time so that I can monitor hardware clock drift and calibration status.

**Why this priority**: RTC monitoring is a specialized use case for systems that need hardware clock accuracy (servers without network access, embedded systems). Less commonly needed than source information.

**Independent Test**: Can be fully tested by calling `get_rtc_data()` and verifying RTC fields are returned. Delivers value by showing RTC offset and calibration state.

**Acceptance Scenarios**:

1. **Given** chronyd is configured to track the RTC, **When** I call `get_rtc_data()`, **Then** I receive RTC data including offset and frequency values
2. **Given** chronyd is not configured to track the RTC (common in VMs), **When** I call `get_rtc_data()`, **Then** `ChronyDataError` is raised with a descriptive message indicating RTC tracking is unavailable
3. **Given** chronyd is tracking the RTC, **When** I call `get_rtc_data()`, **Then** the offset value represents the difference between RTC and system time

---

### User Story 4 - Internal API Consistency (Priority: P2)

As a developer using pychrony, I want all report functions to follow a consistent pattern and return data in predictable formats so that I can easily integrate multiple reports into my monitoring application.

**Why this priority**: Consistency reduces the learning curve and prevents bugs. This is an architectural concern that affects all three new functions and should be addressed during implementation.

**Independent Test**: Can be validated by calling all report functions and verifying they follow the same patterns for connection handling, error raising, and data structure conventions.

**Acceptance Scenarios**:

1. **Given** any report function is called without chronyd running, **When** the connection fails, **Then** all functions raise `ChronyConnectionError` with consistent error messages
2. **Given** any report function returns data, **When** I inspect the returned objects, **Then** all use frozen dataclasses with documented fields and type hints
3. **Given** any report function is called, **When** an error occurs, **Then** the exception type and message format is consistent with existing `get_tracking()` behavior

---

### Edge Cases

- What happens when a source address is IPv6 vs IPv4? (Should handle both transparently)
- How does the system handle sources with unresolvable hostnames? (Return IP address or hostname as configured)
- What happens when RTC tracking is not compiled into chronyd? (Raise appropriate error)
- How does the system handle partial data if chronyd restarts mid-query? (Raise ChronyConnectionError)
- What happens with very large numbers of sources (100+)? (Return all sources without truncation)

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide a `get_sources()` function that retrieves all configured time sources from chronyd
- **FR-002**: System MUST provide a `get_source_stats()` function that retrieves statistical data for each time source
- **FR-003**: System MUST provide a `get_rtc_data()` function that retrieves Real-Time Clock tracking information
- **FR-004**: Each new function MUST accept an optional `socket_path` parameter consistent with existing `get_tracking()`
- **FR-005**: System MUST return data as frozen dataclasses with full type annotations
- **FR-006**: System MUST expose only read-only libchrony APIs (no modification of chronyd state)
- **FR-007**: System MUST provide full type hints for all public interfaces
- **FR-008**: System MUST work on Linux as primary platform
- **FR-009**: System MUST validate all numeric fields are finite (not NaN or Inf)
- **FR-010**: System MUST raise appropriate exceptions from the existing hierarchy for all error conditions
- **FR-011**: `get_sources()` MUST return a list of source objects, empty list if no sources configured
- **FR-012**: `get_source_stats()` MUST return statistics as provided by libchrony; each call is an independent snapshot (user correlates with sources by address if needed)
- **FR-013**: System MUST document all returned fields with docstrings referencing chrony documentation

### Key Entities

- **Source**: Represents a single NTP time source with attributes: address (IPv4/IPv6), poll (log2 seconds), stratum, state (0-5), mode (0-2), flags, reachability (0-255), last_sample_ago, orig_latest_meas, latest_meas, latest_meas_err
- **SourceStats**: Statistical measurements for a source: reference_id, address, samples, runs, span (seconds), std_dev (seconds), resid_freq (ppm), skew (ppm), offset (seconds), offset_err (seconds)
- **RTCData**: Real-Time Clock information: ref_time (timestamp), samples, runs, span (seconds), offset (seconds), freq_offset (ppm)

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: All three new functions (`get_sources`, `get_source_stats`, `get_rtc_data`) are callable and return appropriate data types
- **SC-002**: Users can retrieve complete chronyd state (tracking + sources + source stats + RTC) with 4 function calls
- **SC-003**: All returned data structures have 100% type hint coverage verified by type checker
- **SC-004**: All functions handle chronyd unavailability gracefully with clear error messages
- **SC-005**: Integration tests pass for each new function in a Docker environment with running chronyd
- **SC-006**: New code maintains test coverage at or above 80% for the pychrony package
- **SC-007**: All public functions have docstrings documenting parameters, return types, and possible exceptions

## Assumptions

- **libchrony is the source of truth**: pychrony only exposes what libchrony supports; no invented abstractions or combined operations beyond what the native API provides
- libchrony provides C API functions for sources, sourcestats, and rtcdata reports similar to tracking
- The libchrony field names for new reports can be discovered through documentation or experimentation
- RTC tracking may not be available in all environments (especially VMs); this is a valid state, not an error
- Source statistics require at least a few polling intervals to populate meaningful data
- The number of sources is bounded by chronyd's practical limits (typically under 50, but supporting 100+ is prudent)

## Dependencies

- Existing `_bindings.py` infrastructure for CFFI communication with libchrony
- Existing exception hierarchy (`ChronyError` and subclasses)
- Existing validation patterns from tracking implementation
- libchrony 0.1+ with support for sources/sourcestats/rtcdata reports

## Out of Scope

- High-level convenience APIs combining multiple reports (deferred to Phase 4)
- "clients" report (not supported by libchrony)
- "manual" report (not supported by libchrony)
- Write/control operations on chronyd (this is a read-only monitoring library)
- Windows or macOS support (Linux-only)
