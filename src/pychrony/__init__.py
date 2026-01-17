"""PyChrony: Python bindings for chrony NTP client.

This module provides Python bindings to libchrony for monitoring chrony
time synchronization status. It exposes dataclasses for tracking status,
time sources, source statistics, and RTC data.

Basic Usage:
    >>> from pychrony import get_tracking
    >>> status = get_tracking()
    >>> print(f"Offset: {status.offset:.9f} seconds")
    >>> print(f"Stratum: {status.stratum}")
    >>> if status.is_synchronized():
    ...     print(f"Synchronized to {status.reference_id_name}")

Time Sources:
    >>> from pychrony import get_sources
    >>> sources = get_sources()
    >>> for src in sources:
    ...     print(f"{src.address}: {src.state_name}, stratum {src.stratum}")

Source Statistics:
    >>> from pychrony import get_source_stats
    >>> stats = get_source_stats()
    >>> for s in stats:
    ...     print(f"{s.address}: {s.samples} samples, offset {s.offset:.6f}s")

RTC Data:
    >>> from pychrony import get_rtc_data, ChronyDataError
    >>> try:
    ...     rtc = get_rtc_data()
    ...     print(f"RTC offset: {rtc.offset:.3f}s")
    ... except ChronyDataError:
    ...     print("RTC tracking not available")

Error Handling:
    >>> from pychrony import get_tracking, ChronyError
    >>> try:
    ...     status = get_tracking()
    ... except ChronyLibraryError:
    ...     print("libchrony not installed")
    ... except ChronyConnectionError:
    ...     print("chronyd not running")
    ... except ChronyPermissionError:
    ...     print("permission denied - add user to chrony group")

Custom Socket Path:
    >>> status = get_tracking(socket_path="/custom/path/chronyd.sock")

For more information, see:
- https://github.com/arunderwood/pychrony
- https://chrony-project.org/
"""

from .models import TrackingStatus, Source, SourceStats, RTCData
from .exceptions import (
    ChronyError,
    ChronyConnectionError,
    ChronyPermissionError,
    ChronyDataError,
    ChronyLibraryError,
)
from ._core._bindings import get_tracking, get_sources, get_source_stats, get_rtc_data

__all__ = [
    # Core functions
    "get_tracking",
    "get_sources",
    "get_source_stats",
    "get_rtc_data",
    # Data models
    "TrackingStatus",
    "Source",
    "SourceStats",
    "RTCData",
    # Exceptions
    "ChronyError",
    "ChronyConnectionError",
    "ChronyPermissionError",
    "ChronyDataError",
    "ChronyLibraryError",
]
