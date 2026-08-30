"""Exception hierarchy for pychrony.

This module defines typed exceptions for chrony-specific error conditions.
All exceptions inherit from ChronyError.

See Also:
    chronyc man page - how chronyd is reached, and which commands it allows
    over the network: https://chrony-project.org/doc/4.9/chronyc.html
"""


class ChronyError(Exception):
    """Base exception for all chrony-related errors.

    Attributes:
        message: Human-readable error description
        error_code: Optional numeric error code from libchrony
    """

    def __init__(self, message: str, error_code: int | None = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code

    def __str__(self) -> str:
        if self.error_code is not None:
            return f"{self.message} (error code: {self.error_code})"
        return self.message


class ChronyConnectionError(ChronyError):
    """Raised when chronyd cannot be reached.

    Covers a connection that could not be opened and one that opened but was
    never answered. The second is specific to the command port: it is UDP, so
    the socket opens whether or not chronyd is listening.

    Common causes:

    - chronyd is not running
    - No candidate address could be connected to during auto-detect
    - The command port is disabled (``cmdport 0``), bound elsewhere
      (``bindcmdaddress``), or blocked by a firewall
    - The client is not permitted by ``cmdallow`` (chronyd accepts monitoring
      commands only from localhost by default)
    - ``chrony_init_session()`` returns error

    Examples:
        >>> from pychrony import ChronyConnection, ChronyConnectionError
        >>> try:
        ...     with ChronyConnection() as conn:
        ...         status = conn.get_tracking()
        ... except ChronyConnectionError as e:
        ...     print(f"Connection failed: {e}")
    """


class ChronyPermissionError(ChronyError):
    """Raised when chronyd's Unix socket exists but refuses the connection.

    Connecting to a Unix socket needs write permission, and chronyd creates the
    socket owned by the chrony user without group write, so **joining chrony's
    group does not grant access** - only root does. chrony also requires the
    socket's directory to be accessible only by the root or chrony user, so
    widening these permissions works against its design.

    Prefer the command port for read-only monitoring: chronyd enables it on
    localhost by default and serves every report pychrony reads, while refusing
    the control commands the Unix socket would expose.

    Common causes:

    - Running as an unprivileged user against chronyd's Unix socket
    - SELinux/AppArmor restrictions

    See Also:
        https://chrony-project.org/doc/4.9/chronyc.html

    Examples:
        >>> from pychrony import ChronyConnection, ChronyPermissionError
        >>> try:
        ...     with ChronyConnection() as conn:
        ...         status = conn.get_tracking()
        ... except ChronyPermissionError as e:
        ...     print(f"Permission denied: {e}")
        ...     # Read-only fallback; needs chronyd without "cmdport 0"
        ...     with ChronyConnection("127.0.0.1") as conn:
        ...         status = conn.get_tracking()
    """


class ChronyDataError(ChronyError):
    """Raised when a report is retrieved but its data is invalid or incomplete.

    Reserved for problems with the report itself. A failure to reach chronyd,
    including a request sent but never answered, raises `ChronyConnectionError`
    instead, so "chronyd is unreachable" is one exception to catch, not two.

    Common causes:

    - ``chrony_get_field_index()`` returns < 0 (field not found)
    - chronyd rejected the report request (unknown report, unauthorized)
    - Field validation fails (NaN, out of range)
    - Protocol version mismatch

    Examples:
        >>> from pychrony import ChronyConnection, ChronyDataError
        >>> with ChronyConnection() as conn:
        ...     try:
        ...         status = conn.get_tracking()
        ...     except ChronyDataError as e:
        ...         print(f"Invalid data: {e}")
    """


class ChronyLibraryError(ChronyError):
    """Raised when libchrony is not available.

    Common causes:

    - libchrony not installed at runtime
    - CFFI bindings not compiled (missing libchrony-devel at build time)
    - Library version incompatible

    Examples:
        >>> from pychrony import ChronyConnection, ChronyLibraryError
        >>> try:
        ...     with ChronyConnection() as conn:
        ...         status = conn.get_tracking()
        ... except ChronyLibraryError as e:
        ...     print(f"Library not available: {e}")
        ...     print("Install libchrony-devel and rebuild")
    """

    def __init__(self, message: str):
        super().__init__(message, error_code=None)
