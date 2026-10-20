from collections.abc import Callable

import httpx2
import pytest

from analysis.entities.errors import CatalogueUnavailable, RaceNotAvailable
from analysis.entities.rows import LapRow
from analysis.entities.units import LapNumber, Milliseconds, Position, RoundNumber, Season
from analysis.infrastructure.catalogue_client import HttpCatalogue


def catalogue(handler: Callable[[httpx2.Request], httpx2.Response]) -> HttpCatalogue:
    http = httpx2.Client(base_url="http://catalogue:8000", transport=httpx2.MockTransport(handler))
    return HttpCatalogue(http)


def test_laps_are_parsed_into_rows() -> None:
    def handler(request: httpx2.Request) -> httpx2.Response:
        assert request.url.path == "/races/2025/1/laps"
        return httpx2.Response(
            200, json=[{"driver_id": "norris", "lap": 1, "position": 1, "time_ms": 117099}]
        )

    assert catalogue(handler).laps_of(Season(2025), RoundNumber(1)) == (
        LapRow("norris", LapNumber(1), Position(1), Milliseconds(117099)),
    )


def test_catalogue_404_becomes_race_not_available() -> None:
    def handler(request: httpx2.Request) -> httpx2.Response:
        return httpx2.Response(404, json={"detail": "season 2025 round 3 has not been ingested"})

    with pytest.raises(RaceNotAvailable, match="round 3"):
        catalogue(handler).laps_of(Season(2025), RoundNumber(3))


def test_network_failure_becomes_catalogue_unavailable() -> None:
    def handler(request: httpx2.Request) -> httpx2.Response:
        raise httpx2.ConnectError("refused", request=request)

    with pytest.raises(CatalogueUnavailable, match="unreachable"):
        catalogue(handler).results_of(Season(2025), RoundNumber(1))
