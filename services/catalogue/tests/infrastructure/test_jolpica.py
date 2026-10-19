import time
from collections.abc import Callable, Iterator
from email.utils import formatdate

import httpx2
import pytest

from catalogue.infrastructure.jolpica import (
    JolpicaClient,
    MalformedResponse,
    RetriesExhausted,
    UnretryableResponse,
)

from catalogue_tests.factories import EnvelopeFactory

MakeClient = Callable[[Callable[[httpx2.Request], httpx2.Response]], JolpicaClient]


def test_sends_user_agent_and_returns_json(make_client: MakeClient) -> None:
    seen: list[httpx2.Request] = []

    def handler(request: httpx2.Request) -> httpx2.Response:
        seen.append(request)
        return httpx2.Response(200, json=EnvelopeFactory(MRData__total="5"))

    data = make_client(handler).get_json("/2025/1/laps.json", {"limit": 100, "offset": 0})

    assert data["MRData"]["total"] == "5"
    assert seen[0].headers["User-Agent"] == "paddock/0.1"
    assert str(seen[0].url) == "https://api.jolpi.ca/ergast/f1/2025/1/laps.json?limit=100&offset=0"


def test_retries_429_with_growing_delays(make_client: MakeClient, sleeps: list[float]) -> None:
    statuses = iter([429, 429, 200])

    def handler(request: httpx2.Request) -> httpx2.Response:
        return httpx2.Response(next(statuses), json=EnvelopeFactory())

    make_client(handler).get_json("/2025/1/laps.json")

    assert sleeps == [0.75, 1.25]


def test_server_errors_and_network_errors_are_retried(
    make_client: MakeClient, sleeps: list[float]
) -> None:
    outcomes: Iterator[str | int] = iter(["network", 503, 200])

    def handler(request: httpx2.Request) -> httpx2.Response:
        outcome = next(outcomes)
        if isinstance(outcome, str):
            raise httpx2.ConnectError("refused", request=request)
        return httpx2.Response(outcome, json=EnvelopeFactory())

    make_client(handler).get_json("/2025/1/laps.json")

    assert sleeps == [0.75, 1.25]


@pytest.mark.parametrize(
    ("header", "first_delay"),
    [
        ("3", 3.25),
        (formatdate(time.time() + 3600, usegmt=True), 30.25),
        (formatdate(time.time() - 3600, usegmt=True), 0.75),
        ("soon", 0.75),
    ],
    ids=["seconds", "date-in-future-capped", "date-in-past", "garbage"],
)
def test_retry_after_header_sets_a_capped_minimum_delay(
    make_client: MakeClient, sleeps: list[float], header: str, first_delay: float
) -> None:
    responses = iter(
        [
            httpx2.Response(429, headers={"Retry-After": header}),
            httpx2.Response(200, json=EnvelopeFactory()),
        ]
    )

    make_client(lambda request: next(responses)).get_json("/2025/1/laps.json")

    assert sleeps == [first_delay]


def test_gives_up_after_configured_attempts(make_client: MakeClient, sleeps: list[float]) -> None:
    with pytest.raises(RetriesExhausted, match="4 attempts"):
        make_client(lambda request: httpx2.Response(429)).get_json("/2025/1/laps.json")

    assert sleeps == [0.75, 1.25, 2.25]


def test_other_client_errors_are_not_retried(make_client: MakeClient, sleeps: list[float]) -> None:
    with pytest.raises(UnretryableResponse, match="400") as failure:
        make_client(lambda request: httpx2.Response(400)).get_json("/2025/1/laps.json")

    assert failure.value.status_code == 400
    assert sleeps == []


def test_non_json_body_is_malformed_payload(make_client: MakeClient) -> None:
    with pytest.raises(MalformedResponse, match="not JSON"):
        make_client(lambda request: httpx2.Response(200, text="<html>")).get_json("/x.json")
