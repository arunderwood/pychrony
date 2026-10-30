"""Deprecated auto-loaded pytest plugin (``pytest11`` entry point).

Kept for one release so existing test suites keep working. It provides the
prefixed fixtures from `pychrony.pytest_plugin` plus the old unprefixed
names, which emit a DeprecationWarning when used. Both this module and its
entry point will be removed in the next major release; after that the
fixtures are only available by opting in with
``pytest_plugins = ["pychrony.pytest_plugin"]``.

Disable it early with ``-p no:pychrony``.
"""

import warnings

import pytest

from pychrony import RTCData, Source, SourceStats, TrackingStatus
from pychrony.pytest_plugin import (
    chrony_rtc_data,
    chrony_source,
    chrony_source_stats,
    chrony_tracking_status,
)
from pychrony.testing import (
    make_rtc_data,
    make_source,
    make_source_stats,
    make_tracking,
)

__all__ = [
    "chrony_tracking_status",
    "chrony_source",
    "chrony_source_stats",
    "chrony_rtc_data",
    "tracking_status",
    "source",
    "source_stats",
    "rtc_data",
]


def _warn_renamed(old: str, new: str) -> None:
    warnings.warn(
        f"The pychrony '{old}' fixture is deprecated and will be removed in the "
        f"next major release; use '{new}' instead and enable the plugin with "
        'pytest_plugins = ["pychrony.pytest_plugin"] in your conftest.py.',
        DeprecationWarning,
        stacklevel=2,
    )


@pytest.fixture
def tracking_status() -> TrackingStatus:
    """Deprecated alias for ``chrony_tracking_status``."""
    _warn_renamed("tracking_status", "chrony_tracking_status")
    return make_tracking()


@pytest.fixture
def source() -> Source:
    """Deprecated alias for ``chrony_source``."""
    _warn_renamed("source", "chrony_source")
    return make_source()


@pytest.fixture
def source_stats() -> SourceStats:
    """Deprecated alias for ``chrony_source_stats``."""
    _warn_renamed("source_stats", "chrony_source_stats")
    return make_source_stats()


@pytest.fixture
def rtc_data() -> RTCData:
    """Deprecated alias for ``chrony_rtc_data``."""
    _warn_renamed("rtc_data", "chrony_rtc_data")
    return make_rtc_data()
