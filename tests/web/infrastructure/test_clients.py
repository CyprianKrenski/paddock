from collections.abc import Callable
from datetime import date

import httpx2
import pytest

from web.entities.units import Distance, LapNumber, Milliseconds, Position, RoundNumber, Season
from web.entities.views import (
    DriverReplay,
    Keyframe,
    NotFound,
    RaceSummary,
    Replay,
    StandingBefore,
    UpstreamDown,
)
from web.infrastructure.clients import HttpCatalogue

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
        HttpCatalogue(http(refused)).trace_of(Season(2025), RoundNumber(1))


def test_replay_is_parsed_into_keyframes() -> None:
    def handler(request: httpx2.Request) -> httpx2.Response:
        assert request.url.path == "/races/2025/1/replay"
        return httpx2.Response(
            200,
            json={
                "season": 2025,
                "round_number": 1,
                "total_laps": 1,
                "fastest_laps": [],
                "drivers": [
                    {
                        "driver_id": "x",
                        "code": None,
                        "team": None,
                        "grid": 0,
                        "classified": False,
                        "keyframes": [{"at_ms": 0, "distance": 0.0, "in_pit": False}],
                    }
                ],
            },
        )

    assert HttpCatalogue(http(handler)).replay_of(Season(2025), RoundNumber(1)) == Replay(
        Season(2025),
        RoundNumber(1),
        LapNumber(1),
        (),
        (
            DriverReplay(
                "x",
                None,
                None,
                Position(0),
                False,
                (Keyframe(Milliseconds(0), Distance(0.0), False),),
            ),
        ),
    )


def test_standings_before_a_round_are_parsed() -> None:
    def handler(request: httpx2.Request) -> httpx2.Response:
        assert request.url.path == "/seasons/2025/standings/2"
        return httpx2.Response(
            200, json=[{"driver_id": "norris", "position": 1, "points": 44, "wins": 1}]
        )

    assert HttpCatalogue(http(handler)).standings_of(Season(2025), RoundNumber(2)) == (
        StandingBefore("norris", Position(1), 44.0, 1),
    )


def test_ingest_calls_wait_longer_than_reads() -> None:
    read_timeouts: list[float] = []

    def handler(request: httpx2.Request) -> httpx2.Response:
        read_timeouts.append(request.extensions["timeout"]["read"])
        return httpx2.Response(200, json={"seasons": []})

    catalogue = HttpCatalogue(http(handler), ingest_timeout=180.0)
    catalogue.load_season(Season(2025))
    catalogue.seasons()

    assert read_timeouts == [180.0, 5.0]
