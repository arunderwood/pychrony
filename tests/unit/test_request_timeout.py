"""Unit tests for request timeouts and resends.

libchrony never times out: ChronyConnection waits for each answer itself and
resends an unanswered request. The mock session replaces that wait, so these
tests run without sleeping.
"""

from __future__ import annotations

import math
import socket
import time
from collections.abc import Generator
from contextlib import contextmanager
from dataclasses import replace
from unittest.mock import patch

import pytest

from pychrony import ChronyConnection
from pychrony._core._bindings import (
    CHRONY_RECV_FAILED,
    DEFAULT_TIMEOUT,
    REQUEST_RETRIES,
    _wait_readable,
)
from pychrony.exceptions import ChronyConnectionError
from tests.mocks import (
    SCENARIO_MULTI_SOURCE,
    SCENARIO_NTP_SYNCED,
    SCENARIO_RTC_AVAILABLE,
    ChronyStateConfig,
)
from tests.mocks.session import MockChronySession

ATTEMPTS = REQUEST_RETRIES + 1


@contextmanager
def mock_connection(
    config: ChronyStateConfig, address: str | None = None, timeout: float = 0.5
) -> Generator[tuple[ChronyConnection, MockChronySession], None, None]:
    """Like patched_chrony_connection, also yielding the mock session."""
    session = MockChronySession(config)
    with (
        patch("pychrony._core._bindings._lib", session.lib),
        patch("pychrony._core._bindings._ffi", session.ffi),
        patch("pychrony._core._bindings._LIBRARY_AVAILABLE", True),
        patch("pychrony._core._bindings._wait_readable", session.wait_readable),
        ChronyConnection(address, timeout=timeout) as conn,
    ):
        yield conn, session


def dropped(*requests: int) -> ChronyStateConfig:
    """SCENARIO_NTP_SYNCED with the given requests never answered."""
    return replace(SCENARIO_NTP_SYNCED, dropped_requests=frozenset(requests))


class TestTimeoutParameter:
    """Validation of the timeout argument."""

    def test_default_timeout(self) -> None:
        assert ChronyConnection()._timeout == DEFAULT_TIMEOUT == 1.0

    def test_accepts_positive_timeout(self) -> None:
        assert ChronyConnection(timeout=0.25)._timeout == 0.25

    def test_timeout_is_keyword_only(self) -> None:
        with pytest.raises(TypeError):
            ChronyConnection("127.0.0.1", 2.0)  # type: ignore[misc]

    @pytest.mark.parametrize("timeout", [0, 0.0, -1.0, math.nan, math.inf])
    def test_rejects_non_positive_or_non_finite(self, timeout: float) -> None:
        with pytest.raises(ValueError, match="timeout"):
            ChronyConnection(timeout=timeout)


class TestUnansweredRequests:
    """A request that is never answered is resent, then given up on."""

    def test_answered_request_is_sent_once(self) -> None:
        with mock_connection(SCENARIO_NTP_SYNCED) as (conn, session):
            conn.get_tracking()
        # One count request and one record request
        assert session.requests_sent == 2

    def test_unanswered_report_request_raises_connection_error(self) -> None:
        with (
            pytest.raises(ChronyConnectionError) as exc_info,
            mock_connection(dropped(*range(ATTEMPTS))) as (conn, session),
        ):
            conn.get_tracking()

        assert session.requests_sent == ATTEMPTS
        assert exc_info.value.error_code == CHRONY_RECV_FAILED
        message = str(exc_info.value)
        assert "Timed out waiting for tracking report" in message
        assert f"{ATTEMPTS} attempts, 0.5 s each" in message

    def test_unanswered_record_request_raises_connection_error(self) -> None:
        # Request 0 is the count; every copy of the record request is lost.
        config = dropped(*range(1, 1 + ATTEMPTS))
        with (
            pytest.raises(ChronyConnectionError, match="tracking record 0"),
            mock_connection(config) as (conn, session),
        ):
            conn.get_tracking()
        assert session.requests_sent == 1 + ATTEMPTS

    def test_resend_recovers_from_lost_answers(self) -> None:
        # All but the last attempt of the count request is lost.
        config = dropped(*range(ATTEMPTS - 1))
        with mock_connection(config) as (conn, session):
            status = conn.get_tracking()
        assert status.stratum == SCENARIO_NTP_SYNCED.stratum
        assert session.requests_sent == ATTEMPTS + 1

    def test_resend_recovers_source_record(self) -> None:
        config = replace(SCENARIO_MULTI_SOURCE, dropped_requests=frozenset({2}))
        with mock_connection(config) as (conn, session):
            sources = conn.get_sources()
        assert len(sources) == len(SCENARIO_MULTI_SOURCE.sources)
        assert session.requests_sent == 1 + len(sources) + 1

    def test_resend_recovers_rtc_record(self) -> None:
        # Request 0 is the rtcdata count, request 1 its record.
        config = replace(SCENARIO_RTC_AVAILABLE, dropped_requests=frozenset({1}))
        with mock_connection(config) as (conn, session):
            rtc = conn.get_rtc_data()
        assert rtc is not None
        assert session.requests_sent == 3

    def test_each_wait_is_bounded_by_timeout(self) -> None:
        with (
            pytest.raises(ChronyConnectionError),
            mock_connection(dropped(*range(ATTEMPTS)), timeout=0.25) as (
                conn,
                session,
            ),
        ):
            conn.get_tracking()
        assert len(session.waits) == ATTEMPTS
        assert all(0 < wait <= 0.25 for wait in session.waits)

    def test_timeout_keeps_command_port_guidance(self) -> None:
        with (
            pytest.raises(ChronyConnectionError) as exc_info,
            mock_connection(dropped(*range(ATTEMPTS)), "127.0.0.1:323") as (
                conn,
                _,
            ),
        ):
            conn.get_tracking()
        message = str(exc_info.value)
        assert "did not respond on 127.0.0.1:323" in message
        assert "cmdport 0" in message

    def test_timeout_on_unix_socket_has_no_command_port_guidance(self) -> None:
        with (
            pytest.raises(ChronyConnectionError) as exc_info,
            mock_connection(dropped(*range(ATTEMPTS)), "/run/chrony/x.sock") as (
                conn,
                _,
            ),
        ):
            conn.get_tracking()
        assert "cmdport 0" not in str(exc_info.value)


class TestLateAnswers:
    """An answer that arrives after its request was resent is skipped."""

    def test_late_answer_is_skipped_for_the_resent_one(self) -> None:
        config = replace(SCENARIO_NTP_SYNCED, late_requests=frozenset({0}))
        with mock_connection(config) as (conn, session):
            status = conn.get_tracking()
        assert status.stratum == SCENARIO_NTP_SYNCED.stratum
        # The count request went out twice; both answers were received.
        assert session.requests_sent == 3
        assert session.inbox == []

    def test_late_answers_alone_do_not_satisfy_a_request(self) -> None:
        # Every copy is answered, but each only after its resend went out:
        # the last copy's answer never comes before the deadline.
        config = replace(SCENARIO_NTP_SYNCED, late_requests=frozenset({0, 1, 2}))
        with (
            pytest.raises(ChronyConnectionError, match="tracking report"),
            mock_connection(config) as (conn, _),
        ):
            conn.get_tracking()


class TestWaitReadable:
    """_wait_readable against a real socket."""

    def test_times_out_with_nothing_to_read(self) -> None:
        a, b = socket.socketpair(socket.AF_UNIX, socket.SOCK_DGRAM)
        with a, b:
            start = time.monotonic()
            assert _wait_readable(a.fileno(), 0.05) is False
            assert time.monotonic() - start >= 0.04

    def test_returns_when_data_arrives(self) -> None:
        a, b = socket.socketpair(socket.AF_UNIX, socket.SOCK_DGRAM)
        with a, b:
            b.send(b"x")
            assert _wait_readable(a.fileno(), 5.0) is True


class TestMockConfigValidation:
    """Validation of the mock's unanswered-request settings."""

    def test_rejects_request_both_dropped_and_late(self) -> None:
        with pytest.raises(ValueError, match="both dropped and late"):
            ChronyStateConfig(
                dropped_requests=frozenset({0}), late_requests=frozenset({0})
            )

    def test_rejects_negative_request_number(self) -> None:
        with pytest.raises(ValueError, match="non-negative"):
            ChronyStateConfig(dropped_requests=frozenset({-1}))
