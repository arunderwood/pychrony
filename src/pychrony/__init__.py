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
    ... except ChronyPermissionError:
    ...     print("permission denied - try ChronyConnection('127.0.0.1')")
    ... except ChronyConnectionError:
    ...     print("chronyd unreachable")

Choosing a Transport:
    With no argument, each candidate is tried in turn - chronyd's Unix socket
    paths, then its localhost command port - and the first that connects wins.
    These are the candidates chronyc itself uses.

    The two transports differ in privilege. The Unix socket is chronyd's
    control channel, accessible to the root or chrony user only; the command
    port serves monitoring commands only, which covers every report pychrony
    reads. Read-only consumers should prefer the command port. Note that
    joining the chrony group does not grant access to the Unix socket.

    >>> from pychrony import ChronyConnection, Transport
    >>> with ChronyConnection() as conn:
    ...     assert conn.transport is Transport.COMMAND_PORT
    ...     status = conn.get_tracking()

Custom Socket Path:
    >>> with ChronyConnection("/custom/path/chronyd.sock") as conn:
    ...     status = conn.get_tracking()

Remote chronyd via UDP:
    Requires configuration on the remote host: chronyd binds its command port
    to loopback (bindcmdaddress) and accepts monitoring commands only from
    localhost (cmdallow) by default. The command port is unauthenticated.

    >>> with ChronyConnection("192.168.1.100") as conn:
    ...     status = conn.get_tracking()

Thread Safety:
    ChronyConnection is NOT thread-safe. The underlying libchrony session
    maintains stateful request/response cycles that cannot be safely shared
    between threads.

    For multi-threaded applications, use one of these patterns:

    1. Connection per thread (simplest):
        >>> def worker():
        ...     with ChronyConnection() as conn:
        ...         return conn.get_tracking()

    2. Thread-local storage (for connection reuse):
        >>> import threading
        >>> _local = threading.local()
        >>>
        >>> def get_tracking():
        ...     if not hasattr(_local, 'conn'):
        ...         _local.conn = ChronyConnection()
        ...     with _local.conn as conn:
        ...         return conn.get_tracking()

    The returned dataclasses (TrackingStatus, Source, etc.) are frozen and
    immutable, so they can be safely shared across threads after retrieval.

For more information, see:
- https://github.com/arunderwood/pychrony
- https://chrony-project.org/
- https://chrony-project.org/doc/4.9/chronyc.html
"""

from importlib.metadata import PackageNotFoundError, version

from ._core._bindings import ChronyConnection
from .exceptions import (
    ChronyConnectionError,
    ChronyDataError,
    ChronyError,
    ChronyLibraryError,
    ChronyPermissionError,
)
from .models import (
    LeapStatus,
    RTCData,
    Source,
    SourceMode,
    SourceState,
    SourceStats,
    TrackingStatus,
    Transport,
)

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
    "Transport",
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
