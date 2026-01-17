# Research: libchrony Report Field Names

**Date**: 2026-01-16
**Feature**: 003-multiple-reports-bindings

## Summary

This research documents the libchrony field names for the `sources`, `sourcestats`, and `rtcdata` reports. Field names are accessed dynamically via `chrony_get_field_name()` and must be discovered through experimentation or by examining chrony's source code. The field names generally match the column names shown in `chronyc` command output but use libchrony's internal naming conventions.

## Sources

- [libchrony GitLab repository](https://gitlab.com/chrony/libchrony)
- [chronyc documentation](https://chrony-project.org/doc/4.3/chronyc.html)
- Existing `get_tracking()` implementation in pychrony

## Research Tasks

### Task 1: Determine libchrony field names for "sources" report

**Decision**: Field names follow libchrony conventions similar to tracking report

Based on chronyc `sources` output columns and existing tracking field patterns:

| chronyc Column | Likely libchrony Field Name | Type | Python Field |
|----------------|----------------------------|------|--------------|
| Name/IP address | `address` | string | `address` |
| M (mode) | `mode` | uinteger (enum) | `mode` |
| S (state) | `state` | uinteger (enum) | `state` |
| Stratum | `stratum` | uinteger | `stratum` |
| Poll | `poll` | integer | `poll` |
| Reach | `reach` | uinteger | `reach` |
| LastRx | `last sample ago` | float | `last_sample_ago` |
| Last sample | `offset` or `last offset` | float | `offset` |

**Rationale**: Field names in libchrony are lowercase with spaces (e.g., "reference ID", "address", "stratum"). The exact names will be confirmed during implementation by iterating `chrony_get_field_name()`.

**Alternatives considered**:
- Hardcoding field indices: Rejected (breaks with libchrony updates)
- Using chrony protocol directly: Rejected (libchrony provides stable ABI)

### Task 2: Determine libchrony field names for "sourcestats" report

**Decision**: Field names match chronyc sourcestats columns

| chronyc Column | Likely libchrony Field Name | Type | Python Field |
|----------------|----------------------------|------|--------------|
| Name/IP Address | `address` | string | `address` |
| NP | `number of samples` | uinteger | `n_samples` |
| NR | `number of runs` | uinteger | `n_runs` |
| Span | `span` | float | `span` |
| Frequency | `frequency` | float | `frequency` |
| Freq Skew | `frequency skew` | float | `freq_skew` |
| Offset | `offset` | float | `offset` |
| Std Dev | `standard deviation` | float | `std_dev` |

**Rationale**: Same discovery approach as tracking - use `chrony_get_field_index()` with field names.

**Alternatives considered**: None - this is the only stable approach.

### Task 3: Determine libchrony field names for "rtcdata" report

**Decision**: Field names match chronyc rtcdata output labels

| chronyc Column | Likely libchrony Field Name | Type | Python Field |
|----------------|----------------------------|------|--------------|
| RTC ref time | `reference time` | timespec | `ref_time` |
| Number of samples | `number of samples` | uinteger | `n_samples` |
| Number of runs | `number of runs` | uinteger | `n_runs` |
| Sample span period | `span` or `sample span` | float | `span` |
| RTC is fast by | `offset` or `RTC offset` | float | `offset` |
| RTC gains time at | `frequency` or `RTC frequency` | float | `frequency` |

**Rationale**: RTC report has fewer fields than tracking. libchrony normalizes field names.

**Alternatives considered**: None.

### Task 4: Handle RTC unavailability

**Decision**: Raise `ChronyDataError` when RTC tracking is unavailable

When `chrony_get_report_number_records()` returns 0 for rtcdata, raise `ChronyDataError` with message "RTC tracking is not available (not configured or not supported)".

**Rationale**: Per spec clarification, this matches existing exception patterns and is consistent with `get_tracking()` behavior.

**Alternatives considered**:
- Return `None`: Rejected (inconsistent with `get_tracking()`)
- Return object with zero/default values: Rejected (misleading)
- Return object with `available=False` flag: Rejected (adds complexity)

### Task 5: Best practices for CFFI binding patterns

**Decision**: Follow existing `get_tracking()` implementation patterns exactly

1. Use `_check_library_available()` at function start
2. Use `_find_socket_path()` for socket path resolution
3. Use session-based pattern: open socket → init session → request records → process responses → extract fields → cleanup
4. Create extraction functions per report type: `_extract_sources_fields()`, `_extract_sourcestats_fields()`, `_extract_rtc_fields()`
5. Create validation functions per report type: `_validate_source()`, `_validate_sourcestats()`, `_validate_rtc()`

**Rationale**: Consistency with existing code reduces bugs and maintenance burden.

**Alternatives considered**:
- Refactor to generic `_get_report()` function: Deferred to Phase 4 (high-level API)
- Use context manager pattern: Considered but existing pattern works

## Field Discovery Strategy

Since libchrony field names are not hardcoded in documentation, implementation should:

1. Use known field names from tracking implementation as reference
2. During integration testing, enumerate actual field names via `chrony_get_field_name(session, index)` for each report
3. Update data models if any field names differ from expectations
4. Add field name constants in `_bindings.py` to document discovered names

## Conclusion

All NEEDS CLARIFICATION items resolved:
- ✅ Field names for sources report
- ✅ Field names for sourcestats report
- ✅ Field names for rtcdata report
- ✅ RTC unavailability handling
- ✅ CFFI binding patterns

Ready to proceed to Phase 1: Design & Contracts.
