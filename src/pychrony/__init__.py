"""PyChrony: Python bindings for chrony NTP client.

This module provides Python bindings to libchrony for monitoring chrony
time synchronization status. It exposes the TrackingStatus dataclass
containing offset, frequency, stratum, and reference information.

Basic Usage:
    >>> from pychrony import get_tracking
    >>> status = get_tracking()
    >>> print(f"Offset: {status.offset:.9f} seconds")
    >>> print(f"Stratum: {status.stratum}")
    >>> if status.is_synchronized():
    ...     print(f"Synchronized to {status.reference_id_name}")

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

from .models import TrackingStatus
from .exceptions import (
    ChronyError,
    ChronyConnectionError,
    ChronyPermissionError,
    ChronyDataError,
    ChronyLibraryError,
)
from ._core._bindings import get_tracking

__all__ = [
    # Core function
    "get_tracking",
    # Data model
    "TrackingStatus",
    # Exceptions
    "ChronyError",
    "ChronyConnectionError",
    "ChronyPermissionError",
    "ChronyDataError",
    "ChronyLibraryError",
]
