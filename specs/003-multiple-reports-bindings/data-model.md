# Data Model: Multiple Reports Bindings

**Date**: 2026-01-16
**Feature**: 003-multiple-reports-bindings
**Verified against**: libchrony source (client.c from gitlab.com/chrony/libchrony)

## Overview

This document defines the Python dataclasses for the three new report types: `Source`, `SourceStats`, and `RTCData`. All follow the existing `TrackingStatus` pattern: frozen dataclasses with full type annotations, documented attributes, and helper methods where appropriate.

## Entity Definitions

### Source

Represents a single NTP time source as reported by chronyd's `sources` report.

```python
@dataclass(frozen=True)
class Source:
    """Chrony source information.

    Represents an NTP server, peer, or reference clock being used
    as a time source by chronyd.

    Attributes:
        address: IP address or reference ID of the source (IPv4, IPv6, or refclock ID)
        poll: Polling interval as log2 seconds (e.g., 6 means 64 seconds)
        stratum: NTP stratum level of the source (0-15)
        state: Selection state (0=selected, 1=nonselectable, 2=falseticker,
               3=jittery, 4=unselected, 5=selectable)
        mode: Source mode (0=client, 1=peer, 2=reference clock)
        flags: Source flags (bitfield)
        reachability: Reachability register (8-bit, 377 octal = all recent polls succeeded)
        last_sample_ago: Seconds since last valid sample was received
        orig_latest_meas: Original last sample offset in seconds
        latest_meas: Adjusted last sample offset in seconds
        latest_meas_err: Last sample error bound in seconds
    """

    address: str
    poll: int
    stratum: int
    state: int
    mode: int
    flags: int
    reachability: int
    last_sample_ago: int  # TYPE_UINT32, not float
    orig_latest_meas: float
    latest_meas: float
    latest_meas_err: float

    def is_reachable(self) -> bool:
        """Check if the source has been reachable recently.

        Returns:
            True if reachability register is non-zero (at least one successful poll).
        """
        return self.reachability > 0

    def is_selected(self) -> bool:
        """Check if this source is currently selected for synchronization.

        Returns:
            True if state is 0 (selected).
        """
        return self.state == 0

    @property
    def mode_name(self) -> str:
        """Human-readable mode name."""
        modes = {0: "client", 1: "peer", 2: "reference clock"}
        return modes.get(self.mode, f"unknown({self.mode})")

    @property
    def state_name(self) -> str:
        """Human-readable state name."""
        states = {
            0: "selected",
            1: "nonselectable",
            2: "falseticker",
            3: "jittery",
            4: "unselected",
            5: "selectable",
        }
        return states.get(self.state, f"unknown({self.state})")
```

### SourceStats

Statistical measurements for a time source from chronyd's `sourcestats` report.

```python
@dataclass(frozen=True)
class SourceStats:
    """Chrony source statistics.

    Represents statistical data about measurements from an NTP source,
    used for drift and offset estimation.

    Attributes:
        reference_id: 32-bit NTP reference identifier
        address: IP address of the source (empty for reference clocks)
        samples: Number of sample points currently retained
        runs: Number of runs of residuals with same sign
        span: Time interval between oldest and newest samples in seconds
        std_dev: Estimated sample standard deviation in seconds
        resid_freq: Residual frequency in parts per million
        skew: Frequency skew (error bound) in ppm
        offset: Estimated offset of the source in seconds
        offset_err: Offset error bound in seconds
    """

    reference_id: int
    address: str
    samples: int
    runs: int
    span: int  # TYPE_UINT32, not float
    std_dev: float
    resid_freq: float
    skew: float
    offset: float
    offset_err: float

    def has_sufficient_samples(self, minimum: int = 4) -> bool:
        """Check if enough samples exist for reliable statistics.

        Args:
            minimum: Minimum number of samples required (default 4)

        Returns:
            True if samples >= minimum.
        """
        return self.samples >= minimum
```

### RTCData

Real-Time Clock information from chronyd's `rtcdata` report.

```python
@dataclass(frozen=True)
class RTCData:
    """Chrony RTC (Real-Time Clock) data.

    Represents information about the hardware RTC and its relationship
    to system time, as tracked by chronyd.

    Note: RTC tracking must be enabled in chronyd configuration.
    If not enabled, get_rtc_data() raises ChronyDataError.

    Attributes:
        ref_time: RTC reading at last error measurement (seconds since epoch)
        samples: Number of previous measurements used for calibration
        runs: Number of runs of residuals (indicates linear model fit quality)
        span: Time period covered by measurements in seconds
        offset: Estimated RTC offset (fast by) in seconds
        freq_offset: RTC frequency offset (drift rate) in parts per million
    """

    ref_time: float
    samples: int
    runs: int
    span: int  # TYPE_UINT32, not float
    offset: float
    freq_offset: float

    def is_calibrated(self) -> bool:
        """Check if RTC has enough calibration data.

        Returns:
            True if samples > 0 (some calibration exists).
        """
        return self.samples > 0
```

## Field Mappings (Verified from libchrony source)

### Source Field Mapping

| libchrony Field | C Type | Python Field | Python Type | Validation |
|-----------------|--------|--------------|-------------|------------|
| `address` or `reference ID` | TYPE_ADDRESS_OR_UINT32_IN_ADDRESS | `address` | str | Non-empty |
| `poll` | TYPE_INT16 | `poll` | int | Any integer |
| `stratum` | TYPE_UINT16 | `stratum` | int | 0-15 |
| `state` | TYPE_UINT16 (enum) | `state` | int | 0-5 |
| `mode` | TYPE_UINT16 (enum) | `mode` | int | 0-2 |
| `flags` | TYPE_UINT16 | `flags` | int | 0-65535 |
| `reachability` | TYPE_UINT16 | `reachability` | int | 0-255 |
| `last sample ago` | TYPE_UINT32 | `last_sample_ago` | int | >= 0 |
| `original last sample offset` | TYPE_FLOAT | `orig_latest_meas` | float | Finite |
| `adjusted last sample offset` | TYPE_FLOAT | `latest_meas` | float | Finite |
| `last sample error` | TYPE_FLOAT | `latest_meas_err` | float | >= 0, finite |

### SourceStats Field Mapping

| libchrony Field | C Type | Python Field | Python Type | Validation |
|-----------------|--------|--------------|-------------|------------|
| `reference ID` | TYPE_UINT32 | `reference_id` | int | Any uint32 |
| `address` | TYPE_ADDRESS | `address` | str | May be empty |
| `samples` | TYPE_UINT32 | `samples` | int | >= 0 |
| `runs` | TYPE_UINT32 | `runs` | int | >= 0 |
| `span` | TYPE_UINT32 | `span` | int | >= 0 |
| `standard deviation` | TYPE_FLOAT | `std_dev` | float | >= 0, finite |
| `residual frequency` | TYPE_FLOAT | `resid_freq` | float | Finite |
| `skew` | TYPE_FLOAT | `skew` | float | >= 0, finite |
| `offset` | TYPE_FLOAT | `offset` | float | Finite |
| `offset error` | TYPE_FLOAT | `offset_err` | float | >= 0, finite |

### RTCData Field Mapping

| libchrony Field | C Type | Python Field | Python Type | Validation |
|-----------------|--------|--------------|-------------|------------|
| `reference time` | TYPE_TIMESPEC | `ref_time` | float | >= 0 |
| `samples` | TYPE_UINT16 | `samples` | int | >= 0 |
| `runs` | TYPE_UINT16 | `runs` | int | >= 0 |
| `span` | TYPE_UINT32 | `span` | int | >= 0 |
| `offset` | TYPE_FLOAT | `offset` | float | Finite |
| `frequency offset` | TYPE_FLOAT | `freq_offset` | float | Finite |

## State and Mode Enums (from libchrony source)

### sources_state_enums
```c
{ 0, "selected" },
{ 1, "nonselectable" },
{ 2, "falseticker" },
{ 3, "jittery" },
{ 4, "unselected" },
{ 5, "selectable" },
```

### sources_mode_enums
```c
{ 0, "client" },
{ 1, "peer" },
{ 2, "reference clock" },
```

## Validation Rules

Each dataclass requires field validation before construction:

1. **Integer bounds**: mode (0-2), state (0-5), stratum (0-15), reachability (0-255)
2. **Non-negative integers**: last_sample_ago, samples, runs, span
3. **Non-negative floats**: latest_meas_err, std_dev, skew, offset_err
4. **Finite floats**: All float fields must not be NaN or Inf
5. **Strings**: address may be empty for reference clocks in sourcestats

Validation follows existing `_validate_tracking()` pattern with report-specific functions:
- `_validate_source(data: dict) -> None`
- `_validate_sourcestats(data: dict) -> None`
- `_validate_rtc(data: dict) -> None`

## Key Differences from Initial Research

The following corrections were made after verifying against libchrony source code:

### Sources Report
1. **Field names differ**: `reachability` not `reach`, `last sample ago` is correct
2. **Additional fields**: `flags`, `original last sample offset`, `adjusted last sample offset`, `last sample error` (not just `offset` and `offset_err`)
3. **State enum values inverted**: 0=selected (best), 5=selectable (was documented backwards)
4. **Mode enum values**: 0=client (not "unspecified"), 1=peer, 2=reference clock
5. **Type corrections**: `last_sample_ago` is TYPE_UINT32 (int), not float

### SourceStats Report
1. **Field names differ**: `samples` not `number of samples`, `runs` not `number of runs`
2. **Additional field**: `reference ID` (uint32)
3. **Field name**: `residual frequency` and `skew` (not `frequency` and `frequency skew`)
4. **Additional field**: `offset error`
5. **Type correction**: `span` is TYPE_UINT32 (int), not float

### RTCData Report
1. **Field names differ**: `samples` not `number of samples`, `runs` not `number of runs`
2. **Field name**: `frequency offset` not just `frequency`
3. **Type correction**: `span` is TYPE_UINT32 (int), not float

## Relationships

- `Source` and `SourceStats` are related by `address` field (or `reference_id` for refclocks)
- User correlates sources with their stats by matching addresses
- Each function call returns an independent snapshot (per spec clarification)
- No cross-report atomicity guarantee (per libchrony design)

## Source Reference

Field definitions verified from:
- Repository: https://gitlab.com/chrony/libchrony
- File: client.c (reports.h is just declarations)
- Commit: main branch as of 2026-01-16
