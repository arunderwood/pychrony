# Research: Extend Bindings to Multiple Reports

**Branch**: `003-multiple-reports-bindings` | **Date**: 2026-01-16
**Verified against**: libchrony source (client.c from gitlab.com/chrony/libchrony)

## Executive Summary

This document captures research findings for implementing `get_sources()`, `get_source_stats()`, and `get_rtc_data()` functions in pychrony. Field definitions have been **verified against libchrony source code** (client.c) to ensure accuracy.

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

**Source**: [libchrony repository](https://gitlab.com/chrony/libchrony) - client.c

### 2. Report Names for libchrony API

**Decision**: Use the following report name strings with `chrony_request_report_number_records()` and `chrony_request_record()`:

| Python Function | Report Name | Record Type |
|-----------------|-------------|-------------|
| `get_tracking()` | `"tracking"` | Single record |
| `get_sources()` | `"sources"` | Multiple records |
| `get_source_stats()` | `"sourcestats"` | Multiple records |
| `get_rtc_data()` | `"rtcdata"` | Single record |

**Rationale**: libchrony supports these ten report types: `activity`, `authdata`, `ntpdata`, `rtcdata`, `selectdata`, `serverstats`, `smoothing`, `sources`, `sourcestats`, `tracking`. The report names match chronyc command names.

**Source**: [libchrony repository](https://gitlab.com/chrony/libchrony) - client.c reports[] array

### 3. Field Names for sources Report (VERIFIED)

**Decision**: Use the following field names (verified from `sources_report_fields[]` in client.c):

| libchrony Field Name | Python Attr | C Type | Description |
|---------------------|-------------|--------|-------------|
| `"address"` or `"reference ID"` | `address` | TYPE_ADDRESS_OR_UINT32_IN_ADDRESS | IP address or refclock ID |
| `"poll"` | `poll` | TYPE_INT16 | Polling interval (log2 seconds) |
| `"stratum"` | `stratum` | TYPE_UINT16 | NTP stratum level (0-15) |
| `"state"` | `state` | TYPE_UINT16 (enum) | Selection state (0-5) |
| `"mode"` | `mode` | TYPE_UINT16 (enum) | Source mode (0-2) |
| `"flags"` | `flags` | TYPE_UINT16 | Source flags bitfield |
| `"reachability"` | `reachability` | TYPE_UINT16 | Reachability register (0-255) |
| `"last sample ago"` | `last_sample_ago` | TYPE_UINT32 | Seconds since last sample |
| `"original last sample offset"` | `orig_latest_meas` | TYPE_FLOAT | Original offset (seconds) |
| `"adjusted last sample offset"` | `latest_meas` | TYPE_FLOAT | Adjusted offset (seconds) |
| `"last sample error"` | `latest_meas_err` | TYPE_FLOAT | Error bound (seconds) |

**State Enum** (from `sources_state_enums[]`):
```c
{ 0, "selected" },
{ 1, "nonselectable" },
{ 2, "falseticker" },
{ 3, "jittery" },
{ 4, "unselected" },
{ 5, "selectable" },
```

**Mode Enum** (from `sources_mode_enums[]`):
```c
{ 0, "client" },
{ 1, "peer" },
{ 2, "reference clock" },
```

**Source**: libchrony client.c lines ~55-85

### 4. Field Names for sourcestats Report (VERIFIED)

**Decision**: Use the following field names (verified from `sourcestats_report_fields[]` in client.c):

| libchrony Field Name | Python Attr | C Type | Description |
|---------------------|-------------|--------|-------------|
| `"reference ID"` | `reference_id` | TYPE_UINT32 | NTP reference identifier |
| `"address"` | `address` | TYPE_ADDRESS | IP address (empty for refclocks) |
| `"samples"` | `n_samples` | TYPE_UINT32 | Number of sample points |
| `"runs"` | `n_runs` | TYPE_UINT32 | Runs of same-sign residuals |
| `"span"` | `span` | TYPE_UINT32 | Sample span (seconds) |
| `"standard deviation"` | `std_dev` | TYPE_FLOAT | Standard deviation (seconds) |
| `"residual frequency"` | `resid_freq` | TYPE_FLOAT | Residual frequency (ppm) |
| `"skew"` | `skew` | TYPE_FLOAT | Frequency skew (ppm) |
| `"offset"` | `offset` | TYPE_FLOAT | Estimated offset (seconds) |
| `"offset error"` | `offset_err` | TYPE_FLOAT | Offset error bound (seconds) |

**Source**: libchrony client.c lines ~87-98

### 5. Field Names for rtcdata Report (VERIFIED)

**Decision**: Use the following field names (verified from `rtcdata_report_fields[]` in client.c):

| libchrony Field Name | Python Attr | C Type | Description |
|---------------------|-------------|--------|-------------|
| `"reference time"` | `ref_time` | TYPE_TIMESPEC | Last RTC measurement time |
| `"samples"` | `n_samples` | TYPE_UINT16 | Number of RTC measurements |
| `"runs"` | `n_runs` | TYPE_UINT16 | Runs of same-sign residuals |
| `"span"` | `span` | TYPE_UINT32 | Sample span (seconds) |
| `"offset"` | `offset` | TYPE_FLOAT | RTC offset (seconds) |
| `"frequency offset"` | `freq_offset` | TYPE_FLOAT | RTC frequency offset (ppm) |

**Source**: libchrony client.c lines ~270-277

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

### 8. Validation Rules (Updated)

**Decision**: Apply validation based on verified C types:

**Source validation**:
- `mode` in [0, 1, 2] (client, peer, reference clock)
- `state` in [0, 1, 2, 3, 4, 5] (selected, nonselectable, falseticker, jittery, unselected, selectable)
- `stratum` in [0, 15]
- `reachability` in [0, 255]
- `last_sample_ago` >= 0 (uint32)
- All floats finite

**SourceStats validation**:
- `n_samples` >= 0 (uint32)
- `n_runs` >= 0 (uint32)
- `span` >= 0 (uint32)
- `skew` >= 0
- `std_dev` >= 0
- `offset_err` >= 0
- All floats finite

**RTCData validation**:
- `n_samples` >= 0 (uint16)
- `n_runs` >= 0 (uint16)
- `span` >= 0 (uint32)
- All floats finite

**Rationale**: FR-009 requires validating numeric fields are finite. Bounds come from libchrony C types.

### 9. Mode and State Constants (CORRECTED)

**Decision**: Expose mode and state as integer constants with helper properties:

**Source Mode** (from libchrony):
- 0: client (chronyc: ^)
- 1: peer (chronyc: =)
- 2: reference clock (chronyc: #)

**Source State** (from libchrony - NOTE: order differs from chronyc display):
- 0: selected (chronyc: *)
- 1: nonselectable
- 2: falseticker (chronyc: x)
- 3: jittery (chronyc: ~)
- 4: unselected
- 5: selectable (chronyc: ?)

**Rationale**: Values taken directly from libchrony source enums. The `is_selected()` helper checks for state == 0.

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

### 12. Key Corrections from Source Verification

The following corrections were made after verifying against libchrony source code:

1. **sources report**:
   - Field `"reachability"` not `"reach"`
   - State enum: 0=selected (not 6), 5=selectable (not 0) - order inverted from initial guess
   - Mode enum: 0=client (not "unspecified")
   - Additional fields: `flags`, `original last sample offset`, `adjusted last sample offset`, `last sample error`
   - `last_sample_ago` is TYPE_UINT32 (int, not float)

2. **sourcestats report**:
   - Field `"samples"` not `"number of samples"`
   - Field `"runs"` not `"number of runs"`
   - Field `"residual frequency"` not `"frequency"`
   - Field `"skew"` not `"frequency skew"`
   - Additional field: `"reference ID"`
   - Additional field: `"offset error"`
   - `span` is TYPE_UINT32 (int, not float)

3. **rtcdata report**:
   - Field `"samples"` not `"number of samples"`
   - Field `"runs"` not `"number of runs"`
   - Field `"frequency offset"` not `"frequency"`
   - `span` is TYPE_UINT32 (int, not float)

## Unresolved Items

None - all field definitions verified against libchrony source.

## References

- [libchrony repository](https://gitlab.com/chrony/libchrony) - **primary source for field definitions**
- [chronyc documentation](https://chrony-project.org/doc/4.4/chronyc.html)
- [chrony FAQ](https://chrony-project.org/faq.html)
- Existing pychrony codebase (`src/pychrony/_core/_bindings.py`)
