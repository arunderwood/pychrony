"""Exception hierarchy for pychrony.

This module defines typed exceptions for chrony-specific error conditions.
All exceptions inherit from ChronyError.
"""

from typing import Optional


class ChronyError(Exception):
    """Base exception for all chrony-related errors.

    Attributes:
        message: Human-readable error description
        error_code: Optional numeric error code from libchrony
    """

    def __init__(self, message: str, error_code: Optional[int] = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code

    def __str__(self) -> str:
        if self.error_code is not None:
            return f"{self.message} (error code: {self.error_code})"
        return self.message


class ChronyConnectionError(ChronyError):
    """Raised when connection to chronyd fails.

    Common causes:

    - chronyd is not running
    - Socket path does not exist
    - ``chrony_open_socket()`` returns < 0
    - ``chrony_init_session()`` returns error

    Examples:
        >>> from pychrony import ChronyConnection, ChronyConnectionError
        >>> try:
        ...     with ChronyConnection() as conn:
        ...         status = conn.get_tracking()
        ... except ChronyConnectionError as e:
        ...     print(f"Connection failed: {e}")
    """

    pass


class ChronyPermissionError(ChronyError):
    """Raised when access to chronyd is denied.

    Common causes:

    - User not in chrony group
    - Running as unprivileged user
    - SELinux/AppArmor restrictions

    Examples:
        >>> from pychrony import ChronyConnection, ChronyPermissionError
        >>> try:
        ...     with ChronyConnection() as conn:
        ...         status = conn.get_tracking()
        ... except ChronyPermissionError as e:
        ...     print(f"Permission denied: {e}")
        ...     print("Add user to chrony group or run as root")
    """

    pass


class ChronyDataError(ChronyError):
    """Raised when tracking data is invalid or incomplete.

    Common causes:

    - ``chrony_get_field_index()`` returns < 0 (field not found)
    - ``chrony_process_response()`` returns error
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

    pass


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
