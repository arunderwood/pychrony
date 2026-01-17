# Research: Extend Bindings to Multiple Reports

**Branch**: `003-multiple-reports-bindings` | **Date**: 2026-01-16

## Executive Summary

This document captures research findings for implementing `get_sources()`, `get_source_stats()`, and `get_rtc_data()` functions in pychrony. The research confirms that libchrony's introspection API provides all necessary functionality, and we can follow the established `get_tracking()` pattern.

## Research Tasks

### 1. libchrony Report Types and Field Access

**Decision**: Use libchrony's field introspection API (`chrony_get_field_name()`, `chrony_get_field_index()`) to discover and access fields dynamically.

**Rationale**:
- libchrony exposes a generic introspection API rather than hardcoded field accessors
- Field names are case-sensitive strings matching chrony's internal naming
- This approach provides ABI stability across libchrony versions

**Alternatives Considered**:
- Direct struct access: Rejected (ABI fragile, against constitution principle)
- Hardcoded field indices: Rejected (version-specific, maintenance burden)

**Source**: [libchrony README](https://gitlab.com/chrony/libchrony) indicates using `chrony_get_field_*` functions with field names.

### 2. Report Names for libchrony API

**Decision**: Use the following report name strings with `chrony_request_report_number_records()` and `chrony_request_record()`:

| Python Function | Report Name | Record Type |
|-----------------|-------------|-------------|
| `get_tracking()` | `"tracking"` | Single record |
| `get_sources()` | `"sources"` | Multiple records |
| `get_source_stats()` | `"sourcestats"` | Multiple records |
| `get_rtc_data()` | `"rtcdata"` | Single record |

**Rationale**: libchrony supports these ten report types: `activity`, `authdata`, `ntpdata`, `rtcdata`, `selectdata`, `serverstats`, `smoothing`, `sources`, `sourcestats`, `tracking`. The report names match chronyc command names.

**Source**: [libchrony README](https://gitlab.com/chrony/libchrony)

### 3. Field Names for sources Report

**Decision**: Use the following field names (case-sensitive, based on chronyc sources output and existing tracking patterns):

| libchrony Field Name | Python Attr | Type | Description |
|---------------------|-------------|------|-------------|
| `"address"` | `address` | string | IP address or hostname of source |
| `"mode"` | `mode` | uint | 0=server, 1=peer, 2=reference clock |
| `"state"` | `state` | uint | Selection state (0-6) |
| `"stratum"` | `stratum` | uint | NTP stratum level (0-15) |
| `"poll"` | `poll` | int | Polling interval (log2 seconds) |
| `"reach"` | `reach` | uint | Reachability register (octal, 0-255) |
| `"last sample ago"` | `last_sample_ago` | float | Seconds since last sample |
| `"offset"` | `offset` | float | Current offset (seconds) |
| `"offset error"` | `offset_err` | float | Offset error margin (seconds) |

**Rationale**: Field names match those used by tracking report (e.g., `"address"` not `"ip address"`). Names discovered via `chrony_get_field_name()` introspection at runtime.

**Source**: [chronyc documentation](https://chrony-project.org/doc/4.4/chronyc.html)

### 4. Field Names for sourcestats Report

**Decision**: Use the following field names:

| libchrony Field Name | Python Attr | Type | Description |
|---------------------|-------------|------|-------------|
| `"address"` | `address` | string | Source identifier |
| `"number of samples"` | `n_samples` | uint | Number of sample points |
| `"number of runs"` | `n_runs` | uint | Number of same-sign residual runs |
| `"span"` | `span` | float | Time span of samples (seconds) |
| `"frequency"` | `frequency` | float | Estimated residual frequency (ppm) |
| `"frequency skew"` | `freq_skew` | float | Error bounds on frequency (ppm) |
| `"offset"` | `offset` | float | Estimated source offset (seconds) |
| `"standard deviation"` | `std_dev` | float | Sample standard deviation (seconds) |

**Rationale**: Field names follow libchrony's verbose naming convention with spaces. Map to Pythonic snake_case attributes.

**Source**: [chronyc documentation](https://chrony-project.org/doc/4.4/chronyc.html)

### 5. Field Names for rtcdata Report

**Decision**: Use the following field names:

| libchrony Field Name | Python Attr | Type | Description |
|---------------------|-------------|------|-------------|
| `"reference time"` | `ref_time` | timespec | Last RTC measurement time |
| `"number of samples"` | `n_samples` | uint | Number of RTC measurements |
| `"number of runs"` | `n_runs` | uint | Number of same-sign residual runs |
| `"span"` | `span` | float | Sample span period (seconds) |
| `"offset"` | `offset` | float | RTC fast-by amount (seconds) |
| `"frequency"` | `frequency` | float | RTC gain rate (ppm) |

**Rationale**: RTC data is simpler than other reports. Maps directly to single dataclass.

**Source**: [chronyc documentation](https://chrony-project.org/doc/4.4/chronyc.html)

### 6. Multi-Record Report Handling

**Decision**: For reports with multiple records (sources, sourcestats):
1. Request number of records: `chrony_request_report_number_records(session, b"sources")`
2. Process response loop
3. Get count: `chrony_get_report_number_records(session)`
4. Loop through records 0 to count-1:
   - Request record: `chrony_request_record(session, b"sources", i)`
   - Process response loop
   - Extract fields and create dataclass instance
5. Return list of dataclass instances

**Rationale**: Follows libchrony's designed usage pattern. Each record is a separate request/response cycle.

**Alternative Considered**:
- Single bulk request: Not supported by libchrony API

### 7. Error Handling Strategy

**Decision**: Follow existing `get_tracking()` error mapping:

| Error Condition | Exception Type |
|-----------------|---------------|
| libchrony not available | `ChronyLibraryError` |
| Socket not found | `ChronyConnectionError` |
| Permission denied | `ChronyPermissionError` |
| Connection failed | `ChronyConnectionError` |
| Session init failed | `ChronyConnectionError` |
| Request/response error | `ChronyDataError` |
| No records available | Empty list (sources/sourcestats) or `ChronyDataError` (rtcdata) |
| Invalid field data | `ChronyDataError` |

**Rationale**: Consistency with existing API. RTC unavailability raises error per spec clarification.

### 8. Validation Rules

**Decision**: Apply validation similar to tracking:

**Source validation**:
- `mode` in [0, 1, 2] (server, peer, local)
- `state` in [0, 1, 2, 3, 4, 5, 6] (see state codes below)
- `stratum` in [0, 15]
- `reach` in [0, 255]
- All floats finite

**SourceStats validation**:
- `n_samples` >= 0
- `n_runs` >= 0
- `span` >= 0
- `freq_skew` >= 0
- `std_dev` >= 0
- All floats finite

**RTCData validation**:
- `n_samples` >= 0
- `n_runs` >= 0
- `span` >= 0
- All floats finite

**Rationale**: FR-009 requires validating numeric fields are finite. Bounds come from NTP/chrony specifications.

### 9. Mode and State Constants

**Decision**: Expose mode and state as integer constants with helper properties:

**Source Mode**:
- 0: Server (chronyc: ^)
- 1: Peer (chronyc: =)
- 2: Reference clock (chronyc: #)

**Source State**:
- 0: Selectable (chronyc: ?)
- 1: Unselectable (bad samples)
- 2: Falseticker (chronyc: x)
- 3: Jittery (chronyc: ~)
- 4: Candidate (chronyc: +)
- 5: Combined (chronyc: -)
- 6: Best/Selected (chronyc: *)

**Rationale**: Keep raw integer for programmatic access; add `mode_name` and `state_name` properties for display.

### 10. Testing Strategy

**Decision**: Follow existing test structure:

| Test Type | Location | What to Test |
|-----------|----------|--------------|
| Unit | `tests/unit/test_models.py` | Dataclass creation, frozen, methods |
| Unit | `tests/unit/test_validation.py` | Validation functions for each type |
| Contract | `tests/contract/test_api.py` | Public exports, signatures, types |
| Integration | `tests/integration/test_*.py` | Real chronyd interaction |

**Rationale**: Matches existing project structure. Integration tests require Docker.

### 11. API Consistency

**Decision**: All new functions follow `get_tracking()` signature pattern:

```python
def get_sources(socket_path: Optional[str] = None) -> list[Source]
def get_source_stats(socket_path: Optional[str] = None) -> list[SourceStats]
def get_rtc_data(socket_path: Optional[str] = None) -> RTCData
```

**Rationale**: FR-004 requires optional socket_path. List return for multi-record reports.

### 12. Field Name Discovery Strategy

**Decision**: During integration testing, enumerate actual field names via `chrony_get_field_name(session, index)` for each report to confirm field names.

**Rationale**: libchrony field names are not hardcoded in documentation. Implementation should verify field names match expectations and document any discrepancies.

**Implementation approach**:
1. Use known field names from tracking implementation as reference
2. During integration testing, log all available field names per report
3. Update data models if any field names differ from expectations
4. Add field name comments in `_bindings.py` to document discovered names

## Unresolved Items

None - all clarifications from spec addressed.

## References

- [chronyc documentation](https://chrony-project.org/doc/4.4/chronyc.html)
- [libchrony repository](https://gitlab.com/chrony/libchrony)
- [chrony FAQ](https://chrony-project.org/faq.html)
- Existing pychrony codebase (`src/pychrony/_core/_bindings.py`)
