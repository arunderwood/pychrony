"""Context manager for patching CFFI bindings with mock infrastructure.

This module provides the patched_chrony_connection context manager that
replaces the real CFFI bindings with mock infrastructure for testing.
"""

from __future__ import annotations

from contextlib import contextmanager
from typing import TYPE_CHECKING, Generator
from unittest.mock import patch

from pychrony import ChronyConnection
from tests.mocks.session import MockChronySession

if TYPE_CHECKING:
    from tests.mocks.config import ChronyStateConfig


__all__ = ["patched_chrony_connection"]


@contextmanager
def patched_chrony_connection(
    config: ChronyStateConfig | None = None,
) -> Generator[ChronyConnection, None, None]:
    """Patch pychrony CFFI bindings with mock infrastructure.

    Creates a MockChronySession based on the provided configuration and
    patches the _lib, _ffi, and _LIBRARY_AVAILABLE values in _bindings.py.

    Args:
        config: Mock configuration. If None, uses SCENARIO_NTP_SYNCED.

    Yields:
        ChronyConnection instance connected to mock session.

    Raises:
        ChronyConnectionError: If error_injection includes connection errors.
        ChronyPermissionError: If error_injection includes -13 (EACCES).
        ChronyDataError: If error_injection includes data errors.

    Example:
        from tests.mocks import patched_chrony_connection, SCENARIO_LEAP_INSERT

        def test_leap_pending():
            with patched_chrony_connection(SCENARIO_LEAP_INSERT) as conn:
                status = conn.get_tracking()
                assert status.is_leap_pending()
    """
    # Import here to avoid circular dependency
    from tests.mocks.scenarios import SCENARIO_NTP_SYNCED

    if config is None:
        config = SCENARIO_NTP_SYNCED

    mock_session = MockChronySession(config)

    with (
        patch("pychrony._core._bindings._lib", mock_session.lib),
        patch("pychrony._core._bindings._ffi", mock_session.ffi),
        patch("pychrony._core._bindings._LIBRARY_AVAILABLE", True),
    ):
        with ChronyConnection() as conn:
            yield conn
