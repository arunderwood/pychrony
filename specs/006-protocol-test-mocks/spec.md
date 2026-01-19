# Feature Specification: Protocol-Level Test Mock Infrastructure

**Feature Branch**: `006-protocol-test-mocks`
**Created**: 2026-01-18
**Status**: Draft
**Input**: User description: "Add a protocol-level mock layer for pychrony testing that simulates chronyd responses without requiring hardware (RTC), special system states (leap seconds), or running chronyd."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Testing RTC Functionality Without Hardware (Priority: P1)

As a pychrony test developer, I want to test RTC (Real-Time Clock) functionality without requiring actual RTC hardware, so that I can achieve complete test coverage in CI environments like Docker containers that lack hardware access.

**Why this priority**: RTC testing is currently impossible in Docker/CI environments, making it the highest-value gap to close. This blocks comprehensive testing of a major feature area.

**Independent Test**: Can be fully tested by configuring a mock scenario with RTC available and validating that `get_rtc_data()` returns the expected RTCData object with calibration information.

**Acceptance Scenarios**:

1. **Given** a mock configuration with RTC available and calibrated, **When** I call `get_rtc_data()` through the mocked connection, **Then** I receive an RTCData object with the configured values (samples, offset, frequency offset).
2. **Given** a mock configuration with RTC unavailable, **When** I call `get_rtc_data()`, **Then** I receive `None` as expected.
3. **Given** a mock configuration with RTC available but uncalibrated (samples=0), **When** I call `get_rtc_data()`, **Then** I receive an RTCData object where `is_calibrated()` returns `False`.

---

### User Story 2 - Testing Leap Second States (Priority: P1)

As a pychrony test developer, I want to simulate leap second insertion and deletion states without waiting for actual leap second events, so that I can verify the library correctly handles these rare time synchronization scenarios.

**Why this priority**: Leap seconds occur only once every few years but represent critical NTP functionality. Testing this without mocks is essentially impossible.

**Independent Test**: Can be fully tested by configuring mock scenarios with `LeapStatus.INSERT` or `LeapStatus.DELETE` and verifying `is_leap_pending()` returns True.

**Acceptance Scenarios**:

1. **Given** a mock configuration with leap_status set to INSERT, **When** I call `get_tracking()`, **Then** the returned TrackingStatus has `leap_status == LeapStatus.INSERT` and `is_leap_pending()` returns `True`.
2. **Given** a mock configuration with leap_status set to DELETE, **When** I call `get_tracking()`, **Then** the returned TrackingStatus has `leap_status == LeapStatus.DELETE` and `is_leap_pending()` returns `True`.
3. **Given** a mock configuration with leap_status set to NORMAL, **When** I call `get_tracking()`, **Then** `is_leap_pending()` returns `False`.

---

### User Story 3 - Testing Reference Clock Sources (Priority: P2)

As a pychrony test developer, I want to simulate reference clock sources (GPS, PPS) without hardware, so that I can test stratum-1 source scenarios and verify REFCLOCK mode handling.

**Why this priority**: Reference clocks represent hardware dependencies that cannot be tested in containerized environments. Important for users who deploy pychrony with GPS/PPS sources.

**Independent Test**: Can be fully tested by configuring a source with `SourceMode.REFCLOCK` and a GPS reference ID, then verifying the source appears with correct mode and stratum.

**Acceptance Scenarios**:

1. **Given** a mock configuration with a GPS reference clock source at stratum 1, **When** I call `get_sources()`, **Then** I receive a Source with `mode == SourceMode.REFCLOCK`, stratum 1, and address "GPS".
2. **Given** a mock configuration with a PPS reference clock source, **When** I call `get_sources()`, **Then** I receive a Source with address "PPS" and mode REFCLOCK.

---

### User Story 4 - Testing Multi-Source Selection Scenarios (Priority: P2)

As a pychrony test developer, I want to simulate multiple time sources with different states (selected, falseticker, jittery), so that I can test source selection logic and filtering.

**Why this priority**: Multi-source testing requires complex setups with multiple NTP servers. Mocking enables rapid testing of various selection scenarios.

**Independent Test**: Can be fully tested by configuring multiple sources with different states and verifying filtering/selection logic.

**Acceptance Scenarios**:

1. **Given** a mock configuration with 3 sources (one SELECTED, one FALSETICKER, one SELECTABLE), **When** I call `get_sources()`, **Then** I receive 3 Source objects with their respective states.
2. **Given** the above configuration, **When** I filter for `source.is_selected()`, **Then** exactly one source matches.
3. **Given** a mock with sources having varied reachability (255, 0, 128), **When** I call `get_sources()` and filter by `is_reachable()`, **Then** the unreachable source (0) is correctly identified.

---

### User Story 5 - Declarative Scenario Configuration (Priority: P2)

As a pychrony test developer, I want to configure test scenarios declaratively via dataclasses, so that I can write readable, maintainable tests without verbose mock setup code.

**Why this priority**: Current mocking requires verbose CFFI mock configuration. Declarative configuration improves test readability and reduces boilerplate.

**Independent Test**: Can be fully tested by creating a configuration dataclass, applying it via context manager, and verifying the connection returns expected data.

**Acceptance Scenarios**:

1. **Given** a ChronyStateConfig with stratum=3 and offset=0.001, **When** I use the patched_chrony_connection context manager, **Then** `get_tracking()` returns a TrackingStatus with those values.
2. **Given** a pre-built scenario constant (e.g., SCENARIO_NTP_SYNCED), **When** I apply it, **Then** I get a predictable synchronized state.

---

### User Story 6 - Error Injection for Exception Testing (Priority: P3)

As a pychrony test developer, I want to inject errors at specific points in the protocol, so that I can verify exception handling and error paths.

**Why this priority**: Error paths are difficult to trigger with real chronyd. Injection enables comprehensive exception coverage.

**Independent Test**: Can be fully tested by configuring error injection for specific operations and verifying the expected exceptions are raised.

**Acceptance Scenarios**:

1. **Given** a mock configured to fail on `chrony_open_socket`, **When** I enter the ChronyConnection context, **Then** ChronyConnectionError is raised.
2. **Given** a mock configured to fail on `chrony_process_response` for tracking, **When** I call `get_tracking()`, **Then** ChronyDataError is raised.

---

### User Story 7 - Sync/Unsync State Transitions (Priority: P3)

As a pychrony test developer, I want to test synchronized and unsynchronized states, so that I can verify the `is_synchronized()` method handles edge cases correctly.

**Why this priority**: Testing unsynchronized state requires either breaking chronyd or a fresh install. Mocking makes this trivial.

**Independent Test**: Can be fully tested by configuring unsynchronized state (stratum 16, reference_id 0) and verifying `is_synchronized()` returns False.

**Acceptance Scenarios**:

1. **Given** a mock configuration with stratum=16 and reference_id=0, **When** I call `get_tracking()`, **Then** `is_synchronized()` returns `False`.
2. **Given** a mock configuration with stratum=2 and valid reference_id, **When** I call `get_tracking()`, **Then** `is_synchronized()` returns `True`.
3. **Given** a mock configuration with stratum=15 (boundary), **When** I call `get_tracking()`, **Then** `is_synchronized()` returns `True`.

---

### Edge Cases

- What happens when a source has maximum reachability (255) vs minimum (0)?
- How does the system handle stratum boundary values (0, 15)?
- What happens with maximum/minimum float values for offset fields?
- How are empty source lists handled?
- What happens when RTC reports zero samples (uncalibrated)?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide a MockChronySession class that simulates all CFFI functions used by `_bindings.py`
- **FR-002**: System MUST implement mock versions of: `chrony_open_socket`, `chrony_close_socket`, `chrony_init_session`, `chrony_deinit_session`, `chrony_request_report_number_records`, `chrony_needs_response`, `chrony_process_response`, `chrony_get_report_number_records`, `chrony_request_record`, `chrony_get_field_index`, `chrony_get_field_float`, `chrony_get_field_uinteger`, `chrony_get_field_integer`, `chrony_get_field_string`, `chrony_get_field_timespec`
- **FR-003**: System MUST provide a ChronyStateConfig dataclass for declarative configuration of: synchronization state (stratum, reference_id, leap_status, offset), source configuration (address, state, mode, reachability), RTC availability and calibration state, error injection points
- **FR-004**: System MUST provide SourceConfig and RTCConfig dataclasses for configuring sources and RTC data respectively
- **FR-005**: System MUST provide pre-built scenario presets: SCENARIO_NTP_SYNCED (standard synchronized), SCENARIO_UNSYNC (stratum 16), SCENARIO_LEAP_INSERT (leap second pending insert), SCENARIO_LEAP_DELETE (leap second pending delete), SCENARIO_GPS_REFCLOCK (GPS reference clock at stratum 1), SCENARIO_RTC_AVAILABLE (RTC configured and calibrated), SCENARIO_MULTI_SOURCE (multiple sources with different states)
- **FR-006**: System MUST provide a `patched_chrony_connection` context manager that patches `_lib`, `_ffi`, and `_LIBRARY_AVAILABLE` in `_bindings.py`
- **FR-007**: Tests using the mock infrastructure MUST run without compiled CFFI bindings
- **FR-008**: Tests using the mock infrastructure MUST run without chronyd running
- **FR-009**: Tests using the mock infrastructure MUST be deterministic (no timing dependencies)
- **FR-010**: Existing unit tests MUST continue to pass without modification
- **FR-011**: Existing integration tests MUST continue to pass without modification
- **FR-012**: Mock infrastructure MUST support error injection via a dictionary mapping operation names to error codes

### Key Entities

- **ChronyStateConfig**: Root configuration dataclass representing the complete state of a simulated chronyd connection. Contains tracking fields, source list, RTC configuration, and error injection settings.
- **SourceConfig**: Configuration for a single time source, including address, stratum, state, mode, reachability, and measurement values.
- **RTCConfig**: Configuration for RTC data, including reference time, samples, runs, span, offset, and frequency offset.
- **MockChronySession**: The mock implementation that maintains protocol state and returns configured data via mock `_lib` and `_ffi` objects.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: All previously untestable scenarios (RTC, leap seconds, REFCLOCK, multi-source) have dedicated unit tests that pass
- **SC-002**: New scenario-based unit tests achieve code path coverage for all branches in `_bindings.py` that were previously unreachable
- **SC-003**: Test setup code for mock scenarios requires no more than 3 lines (context manager + config)
- **SC-004**: Existing unit test suite passes without any modifications to test code
- **SC-005**: Existing integration test suite passes without any modifications
- **SC-006**: New unit tests run successfully without CFFI bindings installed or chronyd running
- **SC-007**: Pre-built scenarios cover at least 6 distinct chrony states (synced, unsynced, leap insert, leap delete, GPS refclock, RTC available)

## Assumptions

- The mock infrastructure is for testing purposes only and lives in the `tests/` directory
- Mock behavior closely mirrors libchrony behavior as documented in the vendor submodule
- Field names used in mocks match exactly those used in `_bindings.py` (e.g., "reference ID", "stratum", "leap status")
- The mock does not need to simulate network latency or timing behavior
- Error codes returned by mocks follow the same conventions as libchrony (negative values for errors)

## Out of Scope

- Pure Python client mode implementation (future work enabled by this infrastructure)
- Performance testing or benchmarking infrastructure
- Mocking for write operations (pychrony is read-only)
- Simulation of chronyd configuration changes during a session
