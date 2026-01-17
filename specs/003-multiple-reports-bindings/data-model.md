# Data Model: Multiple Reports Bindings

**Date**: 2026-01-16
**Feature**: 003-multiple-reports-bindings

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
        mode: Source mode (0=unspecified, 1=server, 2=peer, 3=local refclock)
        state: Selection state (0=selectable, 1=unselectable, 2=falseticker,
               3=jittery, 4=candidate, 5=combined, 6=selected/best)
        stratum: NTP stratum level of the source (0-15)
        poll: Polling interval as log2 seconds (e.g., 6 means 64 seconds)
        reach: Reachability register (8-bit shift register, 377 octal = all recent polls succeeded)
        last_sample_ago: Seconds since last valid sample was received
        offset: Offset of source relative to local clock in seconds
        offset_err: Estimated error bound on offset in seconds
    """

    address: str
    mode: int
    state: int
    stratum: int
    poll: int
    reach: int
    last_sample_ago: float
    offset: float
    offset_err: float

    def is_reachable(self) -> bool:
        """Check if the source has been reachable recently.

        Returns:
            True if reach register is non-zero (at least one successful poll).
        """
        return self.reach > 0

    def is_selected(self) -> bool:
        """Check if this source is currently selected for synchronization.

        Returns:
            True if state indicates combined (5) or selected/best (6).
        """
        return self.state in (5, 6)

    @property
    def mode_name(self) -> str:
        """Human-readable mode name."""
        modes = {0: "unspecified", 1: "server", 2: "peer", 3: "refclock"}
        return modes.get(self.mode, f"unknown({self.mode})")

    @property
    def state_name(self) -> str:
        """Human-readable state name."""
        states = {
            0: "selectable",
            1: "unselectable",
            2: "falseticker",
            3: "jittery",
            4: "candidate",
            5: "combined",
            6: "selected",
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
        address: IP address or reference ID of the source
        n_samples: Number of sample points currently retained
        n_runs: Number of runs of residuals with same sign
        span: Time interval between oldest and newest samples in seconds
        frequency: Estimated residual frequency in parts per million
        freq_skew: Estimated error bounds on frequency in ppm
        offset: Estimated offset of the source in seconds
        std_dev: Estimated sample standard deviation in seconds
    """

    address: str
    n_samples: int
    n_runs: int
    span: float
    frequency: float
    freq_skew: float
    offset: float
    std_dev: float

    def has_sufficient_samples(self, minimum: int = 4) -> bool:
        """Check if enough samples exist for reliable statistics.

        Args:
            minimum: Minimum number of samples required (default 4)

        Returns:
            True if n_samples >= minimum.
        """
        return self.n_samples >= minimum
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
        n_samples: Number of previous measurements used for calibration
        n_runs: Number of runs of residuals (indicates linear model fit quality)
        span: Time period covered by measurements in seconds
        offset: Estimated RTC offset (fast by) in seconds
        frequency: RTC drift rate in parts per million
    """

    ref_time: float
    n_samples: int
    n_runs: int
    span: float
    offset: float
    frequency: float

    def is_calibrated(self) -> bool:
        """Check if RTC has enough calibration data.

        Returns:
            True if n_samples > 0 (some calibration exists).
        """
        return self.n_samples > 0
```

## Field Mappings

### Source Field Mapping

| libchrony Field | Type | Python Field | Validation |
|-----------------|------|--------------|------------|
| `address` | string | `address` | Non-empty string |
| `mode` | uinteger | `mode` | 0-3 |
| `state` | uinteger | `state` | 0-6 |
| `stratum` | uinteger | `stratum` | 0-15 |
| `poll` | integer | `poll` | Any integer |
| `reach` | uinteger | `reach` | 0-255 |
| `last sample ago` | float | `last_sample_ago` | >= 0 |
| `offset` | float | `offset` | Finite |
| `offset error` | float | `offset_err` | >= 0, finite |

### SourceStats Field Mapping

| libchrony Field | Type | Python Field | Validation |
|-----------------|------|--------------|------------|
| `address` | string | `address` | Non-empty string |
| `number of samples` | uinteger | `n_samples` | >= 0 |
| `number of runs` | uinteger | `n_runs` | >= 0 |
| `span` | float | `span` | >= 0 |
| `frequency` | float | `frequency` | Finite |
| `frequency skew` | float | `freq_skew` | >= 0, finite |
| `offset` | float | `offset` | Finite |
| `standard deviation` | float | `std_dev` | >= 0, finite |

### RTCData Field Mapping

| libchrony Field | Type | Python Field | Validation |
|-----------------|------|--------------|------------|
| `reference time` | timespec | `ref_time` | >= 0 |
| `number of samples` | uinteger | `n_samples` | >= 0 |
| `number of runs` | uinteger | `n_runs` | >= 0 |
| `span` | float | `span` | >= 0 |
| `offset` | float | `offset` | Finite |
| `frequency` | float | `frequency` | Finite |

## Validation Rules

Each dataclass requires field validation before construction:

1. **Integer bounds**: mode (0-3), state (0-6), stratum (0-15), reach (0-255)
2. **Non-negative floats**: last_sample_ago, offset_err, span, freq_skew, std_dev
3. **Finite floats**: All float fields must not be NaN or Inf
4. **Non-empty strings**: address must have length > 0

Validation follows existing `_validate_tracking()` pattern with report-specific functions:
- `_validate_source(data: dict) -> None`
- `_validate_sourcestats(data: dict) -> None`
- `_validate_rtc(data: dict) -> None`

## Relationships

- `Source` and `SourceStats` are related by `address` field
- User correlates sources with their stats by matching addresses
- Each function call returns an independent snapshot (per spec clarification)
- No cross-report atomicity guarantee (per libchrony design)
