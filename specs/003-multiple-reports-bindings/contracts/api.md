# API Contracts: Multiple Reports Bindings

**Date**: 2026-01-16
**Feature**: 003-multiple-reports-bindings

## Overview

This document defines the public API contracts for the three new report functions. Each function follows the same signature pattern as `get_tracking()`.

## Public Functions

### get_sources

```python
def get_sources(socket_path: Optional[str] = None) -> list[Source]:
    """Get list of time sources from chronyd.

    Retrieves information about all NTP servers, peers, and reference
    clocks configured as time sources in chronyd.

    Args:
        socket_path: Path to chronyd Unix socket. Defaults to
            '/run/chrony/chronyd.sock' or '/var/run/chrony/chronyd.sock'.

    Returns:
        List of Source objects representing each time source.
        Returns empty list if no sources are configured.

    Raises:
        ChronyLibraryError: If libchrony is not installed or cannot be loaded.
        ChronyConnectionError: If chronyd is not running or unreachable.
        ChronyPermissionError: If insufficient permissions to access chronyd.
        ChronyDataError: If source data is invalid or incomplete.

    Example:
        >>> from pychrony import get_sources
        >>> sources = get_sources()
        >>> for src in sources:
        ...     print(f"{src.address}: stratum {src.stratum}, state={src.state_name}")
        pool.ntp.org: stratum 2, state=synced
    """
```

### get_source_stats

```python
def get_source_stats(socket_path: Optional[str] = None) -> list[SourceStats]:
    """Get source statistics from chronyd.

    Retrieves statistical measurements for each time source, including
    offset estimation, frequency drift, and sample information.

    Args:
        socket_path: Path to chronyd Unix socket. Defaults to
            '/run/chrony/chronyd.sock' or '/var/run/chrony/chronyd.sock'.

    Returns:
        List of SourceStats objects with statistics for each source.
        Returns empty list if no sources are configured.

    Raises:
        ChronyLibraryError: If libchrony is not installed or cannot be loaded.
        ChronyConnectionError: If chronyd is not running or unreachable.
        ChronyPermissionError: If insufficient permissions to access chronyd.
        ChronyDataError: If statistics data is invalid or incomplete.

    Note:
        Each call returns an independent snapshot. To correlate with
        get_sources(), match by address field.

    Example:
        >>> from pychrony import get_source_stats
        >>> stats = get_source_stats()
        >>> for s in stats:
        ...     print(f"{s.address}: offset={s.offset:.6f}s, samples={s.n_samples}")
        pool.ntp.org: offset=0.000123s, samples=8
    """
```

### get_rtc_data

```python
def get_rtc_data(socket_path: Optional[str] = None) -> RTCData:
    """Get Real-Time Clock data from chronyd.

    Retrieves RTC calibration information including offset and drift rate.

    Args:
        socket_path: Path to chronyd Unix socket. Defaults to
            '/run/chrony/chronyd.sock' or '/var/run/chrony/chronyd.sock'.

    Returns:
        RTCData object with RTC calibration information.

    Raises:
        ChronyLibraryError: If libchrony is not installed or cannot be loaded.
        ChronyConnectionError: If chronyd is not running or unreachable.
        ChronyPermissionError: If insufficient permissions to access chronyd.
        ChronyDataError: If RTC tracking is not available (not configured
            in chronyd or not supported on this system) or data is invalid.

    Note:
        RTC tracking must be enabled in chronyd configuration (rtcsync or
        rtcfile directives). VMs typically do not have RTC tracking available.

    Example:
        >>> from pychrony import get_rtc_data
        >>> rtc = get_rtc_data()
        >>> print(f"RTC offset: {rtc.offset:.3f}s, drift: {rtc.frequency:.3f} ppm")
        RTC offset: 0.123s, drift: 1.234 ppm
    """
```

## Module Exports

### pychrony/__init__.py

The following exports must be added to the public API:

```python
# New exports for 003-multiple-reports-bindings
from pychrony._core._bindings import get_sources, get_source_stats, get_rtc_data
from pychrony.models import Source, SourceStats, RTCData

__all__ = [
    # Existing exports
    "get_tracking",
    "TrackingStatus",
    "ChronyError",
    "ChronyConnectionError",
    "ChronyPermissionError",
    "ChronyDataError",
    "ChronyLibraryError",
    # New exports (003-multiple-reports-bindings)
    "get_sources",
    "get_source_stats",
    "get_rtc_data",
    "Source",
    "SourceStats",
    "RTCData",
]
```

## Contract Tests

The following contract tests verify API stability:

```python
# tests/contract/test_api.py additions

def test_get_sources_signature():
    """Verify get_sources() has correct signature."""
    sig = inspect.signature(get_sources)
    assert "socket_path" in sig.parameters
    assert sig.parameters["socket_path"].default is None
    assert sig.parameters["socket_path"].annotation == Optional[str]

def test_get_source_stats_signature():
    """Verify get_source_stats() has correct signature."""
    sig = inspect.signature(get_source_stats)
    assert "socket_path" in sig.parameters
    assert sig.parameters["socket_path"].default is None
    assert sig.parameters["socket_path"].annotation == Optional[str]

def test_get_rtc_data_signature():
    """Verify get_rtc_data() has correct signature."""
    sig = inspect.signature(get_rtc_data)
    assert "socket_path" in sig.parameters
    assert sig.parameters["socket_path"].default is None
    assert sig.parameters["socket_path"].annotation == Optional[str]

def test_source_is_frozen_dataclass():
    """Verify Source is a frozen dataclass."""
    assert is_dataclass(Source)
    assert Source.__dataclass_fields__

def test_sourcestats_is_frozen_dataclass():
    """Verify SourceStats is a frozen dataclass."""
    assert is_dataclass(SourceStats)
    assert SourceStats.__dataclass_fields__

def test_rtcdata_is_frozen_dataclass():
    """Verify RTCData is a frozen dataclass."""
    assert is_dataclass(RTCData)
    assert RTCData.__dataclass_fields__

def test_source_required_fields():
    """Verify Source has all required fields."""
    required = {"address", "mode", "state", "stratum", "poll", "reach",
                "last_sample_ago", "offset", "offset_err"}
    assert required <= set(Source.__dataclass_fields__.keys())

def test_sourcestats_required_fields():
    """Verify SourceStats has all required fields."""
    required = {"address", "n_samples", "n_runs", "span",
                "frequency", "freq_skew", "offset", "std_dev"}
    assert required <= set(SourceStats.__dataclass_fields__.keys())

def test_rtcdata_required_fields():
    """Verify RTCData has all required fields."""
    required = {"ref_time", "n_samples", "n_runs", "span", "offset", "frequency"}
    assert required <= set(RTCData.__dataclass_fields__.keys())
```

## Error Contracts

| Condition | Exception | Message Pattern |
|-----------|-----------|-----------------|
| libchrony not available | `ChronyLibraryError` | "libchrony bindings not available..." |
| Socket not found | `ChronyConnectionError` | "chronyd socket not found..." |
| Connection failed | `ChronyConnectionError` | "Failed to connect to chronyd..." |
| Permission denied | `ChronyPermissionError` | "Permission denied accessing..." |
| Field not found | `ChronyDataError` | "Field '...' not found..." |
| Invalid field value | `ChronyDataError` | "Invalid ...: ..." |
| RTC not available | `ChronyDataError` | "RTC tracking is not available..." |
