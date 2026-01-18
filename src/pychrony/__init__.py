"""PyChrony: Python bindings for chrony NTP client.

This module provides Python bindings to libchrony for monitoring chrony
time synchronization status. It exposes a ChronyConnection context manager
for retrieving tracking status, time sources, source statistics, and RTC data.

Basic Usage:
    >>> from pychrony import ChronyConnection
    >>> with ChronyConnection() as conn:
    ...     status = conn.get_tracking()
    ...     print(f"Offset: {status.offset:.9f} seconds")
    ...     print(f"Stratum: {status.stratum}")
    ...     if status.is_synchronized():
    ...         print(f"Synchronized to {status.reference_id_name}")

Multiple Queries (Connection Reuse):
    >>> from pychrony import ChronyConnection
    >>> with ChronyConnection() as conn:
    ...     tracking = conn.get_tracking()
    ...     sources = conn.get_sources()
    ...     stats = conn.get_source_stats()
    ...     rtc = conn.get_rtc_data()

Time Sources:
    >>> from pychrony import ChronyConnection
    >>> with ChronyConnection() as conn:
    ...     sources = conn.get_sources()
    ...     for src in sources:
    ...         print(f"{src.address}: {src.state.name}, stratum {src.stratum}")

Source Statistics:
    >>> from pychrony import ChronyConnection
    >>> with ChronyConnection() as conn:
    ...     stats = conn.get_source_stats()
    ...     for s in stats:
    ...         print(f"{s.address}: {s.samples} samples, offset {s.offset:.6f}s")

RTC Data:
    >>> from pychrony import ChronyConnection
    >>> with ChronyConnection() as conn:
    ...     rtc = conn.get_rtc_data()
    ...     if rtc:
    ...         print(f"RTC offset: {rtc.offset:.3f}s")
    ...     else:
    ...         print("RTC tracking not configured")

Error Handling:
    >>> from pychrony import ChronyConnection, ChronyError
    >>> try:
    ...     with ChronyConnection() as conn:
    ...         status = conn.get_tracking()
    ... except ChronyLibraryError:
    ...     print("libchrony not installed")
    ... except ChronyConnectionError:
    ...     print("chronyd not running")
    ... except ChronyPermissionError:
    ...     print("permission denied - add user to chrony group")

Custom Socket Path:
    >>> with ChronyConnection("/custom/path/chronyd.sock") as conn:
    ...     status = conn.get_tracking()

Remote chronyd via UDP:
    >>> with ChronyConnection("192.168.1.100") as conn:
    ...     status = conn.get_tracking()

For more information, see:
- https://github.com/arunderwood/pychrony
- https://chrony-project.org/
"""

from importlib.metadata import version, PackageNotFoundError

from .models import (
    TrackingStatus,
    Source,
    SourceStats,
    RTCData,
    LeapStatus,
    SourceState,
    SourceMode,
)
from .exceptions import (
    ChronyError,
    ChronyConnectionError,
    ChronyPermissionError,
    ChronyDataError,
    ChronyLibraryError,
)
from ._core._bindings import ChronyConnection

try:
    __version__ = version("pychrony")
except PackageNotFoundError:
    __version__ = "0.0.0.dev0"

__all__ = [
    # Version
    "__version__",
    # Core connection class
    "ChronyConnection",
    # Enums
    "LeapStatus",
    "SourceState",
    "SourceMode",
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
