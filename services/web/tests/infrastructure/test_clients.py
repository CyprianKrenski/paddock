from collections.abc import Callable
from datetime import date

import httpx2
import pytest

from web.entities.errors import NotFound, UpstreamDown
from web.entities.units import RoundNumber, Season
from web.entities.views import RaceSummary
from web.infrastructure.clients import HttpAnalysis, HttpCatalogue

Handler = Callable[[httpx2.Request], httpx2.Response]


def http(handler: Handler) -> httpx2.Client:
    return httpx2.Client(base_url="http://catalogue:8000", transport=httpx2.MockTransport(handler))


def test_races_are_parsed_into_summaries() -> None:
    def handler(request: httpx2.Request) -> httpx2.Response:
        assert request.url.path == "/seasons/2025/races"
        return httpx2.Response(
            200,
            json=[
                {
                    "season": 2025,
                    "round_number": 1,
                    "name": "Australian Grand Prix",
                    "circuit_name": "Albert Park",
                    "date": "2025-03-16",
                    "ingested": True,
                }
            ],
        )

    assert HttpCatalogue(http(handler)).races_of(Season(2025)) == (
        RaceSummary(
            Season(2025),
            RoundNumber(1),
            "Australian Grand Prix",
            "Albert Park",
            date(2025, 3, 16),
            True,
        ),
    )


def test_load_race_posts_and_ignores_the_body() -> None:
    seen: list[str] = []

    def handler(request: httpx2.Request) -> httpx2.Response:
        seen.append(f"{request.method} {request.url.path}")
        return httpx2.Response(200, json={"drivers": 20, "laps": 921, "pit_stops": 82})

    HttpCatalogue(http(handler)).load_race(Season(2025), RoundNumber(1))

    assert seen == ["POST /races/2025/1/ingest"]


def test_404_becomes_not_found_and_network_errors_become_upstream_down() -> None:
    with pytest.raises(NotFound, match="not been loaded"):
        HttpCatalogue(
            http(lambda r: httpx2.Response(404, json={"detail": "season 1900 has not been loaded"}))
        ).races_of(Season(1900))

    def refused(request: httpx2.Request) -> httpx2.Response:
        raise httpx2.ConnectError("refused", request=request)

    with pytest.raises(UpstreamDown, match="unreachable"):
        HttpAnalysis(http(refused)).frame_of(Season(2025), RoundNumber(1), 1.0)


def test_frame_query_carries_t() -> None:
    def handler(request: httpx2.Request) -> httpx2.Response:
        assert request.url.path == "/races/2025/1/frame" and request.url.params["t"] == "200.0"
        return httpx2.Response(200, json={"at_seconds": 200.0, "drivers": []})

    assert HttpAnalysis(http(handler)).frame_of(Season(2025), RoundNumber(1), 200.0) == {
        "at_seconds": 200.0,
        "drivers": [],
    }
