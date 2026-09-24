"""Tests for reading per-source reports while chronyd's source list changes.

chronyd adds and removes sources while it resolves pool and server names, and
when it replaces unreachable pool servers. A record count read before such a
change can point past the end of the list, and chronyd then refuses the record
request with a status libchrony reports as CHRONY_UNEXPECTED_STATUS.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any
from unittest.mock import patch

import pytest

from pychrony import ChronyConnection
from pychrony._core._bindings import (
    CHRONY_SEND_FAILED,
    CHRONY_UNEXPECTED_STATUS,
    SOURCE_LIST_READ_ATTEMPTS,
)
from pychrony.exceptions import ChronyConnectionError, ChronyDataError
from tests.mocks import ChronyStateConfig, SourceConfig, patched_chrony_connection

READERS: dict[str, Callable[[ChronyConnection], list[Any]]] = {
    "sources": ChronyConnection.get_sources,
    "sourcestats": ChronyConnection.get_source_stats,
}

pytestmark = pytest.mark.parametrize("report", list(READERS))


def _sources(count: int) -> list[SourceConfig]:
    return [SourceConfig(address=f"192.168.1.{i + 1}") for i in range(count)]


def _shrinking_config(shrinks: int) -> ChronyStateConfig:
    """Config whose list loses one source after each of the first `shrinks` counts.

    After that the list holds steady, so the read that follows succeeds with
    two sources.
    """
    initial = _sources(shrinks + 2)
    changes = [initial[: len(initial) - step] for step in range(1, shrinks + 1)]
    return ChronyStateConfig(
        sources=initial,
        source_list_changes=[*changes, changes[-1]] if changes else [],
    )


def _read(
    config: ChronyStateConfig, report: str
) -> tuple[list[Any] | BaseException, int]:
    """Read `report`, returning its result or exception and the count requests."""
    with patched_chrony_connection(config) as conn:
        with patch.object(
            conn, "_request_report", wraps=conn._request_report
        ) as count_requests:
            try:
                result: list[Any] | BaseException = READERS[report](conn)
            except Exception as e:  # noqa: BLE001
                result = e
        return result, count_requests.call_count


def test_steady_list_reads_once(report: str) -> None:
    result, counts = _read(_shrinking_config(0), report)

    assert isinstance(result, list)
    assert len(result) == 2
    assert counts == 1


def test_shrink_during_read_rereads_the_new_list(report: str) -> None:
    config = ChronyStateConfig(sources=_sources(3), source_list_changes=[_sources(2)])

    result, counts = _read(config, report)

    assert isinstance(result, list)
    assert [r.address for r in result] == ["192.168.1.1", "192.168.1.2"]
    assert counts == 2


def test_removed_middle_source_is_not_read_twice(report: str) -> None:
    initial = _sources(3)
    after = [initial[0], initial[2]]
    config = ChronyStateConfig(sources=initial, source_list_changes=[after])

    result, _ = _read(config, report)

    assert isinstance(result, list)
    assert [r.address for r in result] == ["192.168.1.1", "192.168.1.3"]


def test_list_settling_on_last_attempt_succeeds(report: str) -> None:
    result, counts = _read(_shrinking_config(SOURCE_LIST_READ_ATTEMPTS - 1), report)

    assert isinstance(result, list)
    assert len(result) == 2
    assert counts == SOURCE_LIST_READ_ATTEMPTS


def test_list_still_changing_after_last_attempt_raises(report: str) -> None:
    result, counts = _read(_shrinking_config(SOURCE_LIST_READ_ATTEMPTS), report)

    assert isinstance(result, ChronyDataError)
    assert result.error_code == CHRONY_UNEXPECTED_STATUS
    assert counts == SOURCE_LIST_READ_ATTEMPTS


def test_list_growing_during_read_returns_counted_sources(report: str) -> None:
    config = ChronyStateConfig(sources=_sources(1), source_list_changes=[_sources(6)])

    result, counts = _read(config, report)

    assert isinstance(result, list)
    assert len(result) == 1
    assert counts == 1


def test_other_data_error_is_not_retried(report: str) -> None:
    config = ChronyStateConfig(
        sources=_sources(2), error_injection={"chrony_request_record": 3}
    )

    result, counts = _read(config, report)

    assert isinstance(result, ChronyDataError)
    assert result.error_code == 3
    assert counts == 1


def test_connection_error_is_not_retried(report: str) -> None:
    config = ChronyStateConfig(
        sources=_sources(2),
        error_injection={"chrony_request_record": CHRONY_SEND_FAILED},
    )

    result, counts = _read(config, report)

    assert isinstance(result, ChronyConnectionError)
    assert counts == 1
