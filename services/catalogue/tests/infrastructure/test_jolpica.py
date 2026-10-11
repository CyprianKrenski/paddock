from collections.abc import Callable

import httpx2
import pytest

from catalogue.infrastructure.jolpica import JolpicaClient, UpstreamUnavailable

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


def test_retry_after_header_extends_the_delay(make_client: MakeClient, sleeps: list[float]) -> None:
    responses = iter(
        [
            httpx2.Response(429, headers={"Retry-After": "3"}),
            httpx2.Response(200, json=EnvelopeFactory()),
        ]
    )

    make_client(lambda request: next(responses)).get_json("/2025/1/laps.json")

    assert sleeps == [3.25]


def test_gives_up_after_configured_attempts(make_client: MakeClient, sleeps: list[float]) -> None:
    with pytest.raises(UpstreamUnavailable, match="4 attempts"):
        make_client(lambda request: httpx2.Response(429)).get_json("/2025/1/laps.json")

    assert sleeps == [0.75, 1.25, 2.25]


def test_client_errors_are_not_retried(make_client: MakeClient, sleeps: list[float]) -> None:
    with pytest.raises(UpstreamUnavailable, match="404"):
        make_client(lambda request: httpx2.Response(404)).get_json("/1950/99/laps.json")

    assert sleeps == []
