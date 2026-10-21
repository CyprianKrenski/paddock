from fastapi.testclient import TestClient

from analysis.api.dependencies import get_source
from analysis.entities.errors import CatalogueUnavailable, RaceNotAvailable
from analysis.entities.units import RoundNumber, Season
from analysis.main import create_app

from analysis_tests.fakes import MemorySource


def client_with(source: object) -> TestClient:
    app = create_app()
    app.dependency_overrides[get_source] = lambda: source
    return TestClient(app)


class MissingRaceSource:
    def laps_of(self, season: Season, round_number: RoundNumber) -> tuple[()]:
        raise RaceNotAvailable("season 2025 round 3 has not been ingested")

    def results_of(self, season: Season, round_number: RoundNumber) -> tuple[()]:
        raise RaceNotAvailable("season 2025 round 3 has not been ingested")

    def pit_stops_of(self, season: Season, round_number: RoundNumber) -> tuple[()]:
        raise RaceNotAvailable("season 2025 round 3 has not been ingested")


class DeadSource:
    def laps_of(self, season: Season, round_number: RoundNumber) -> tuple[()]:
        raise CatalogueUnavailable("catalogue unreachable: refused")

    def results_of(self, season: Season, round_number: RoundNumber) -> tuple[()]:
        raise CatalogueUnavailable("catalogue unreachable: refused")

    def pit_stops_of(self, season: Season, round_number: RoundNumber) -> tuple[()]:
        raise CatalogueUnavailable("catalogue unreachable: refused")


def test_trace_as_json() -> None:
    response = client_with(MemorySource()).get("/races/2025/1/trace")

    assert response.status_code == 200
    assert response.json() == {
        "season": 2025,
        "round_number": 1,
        "total_laps": 2,
        "fastest_lap": {"driver_id": "piastri", "lap": 2, "time_ms": 90000},
        "series": [
            {
                "driver_id": "norris",
                "code": "NOR",
                "team": "mclaren",
                "positions": [1, 1],
                "gaps_ms": [0, 0],
                "pit_laps": [],
            },
            {
                "driver_id": "piastri",
                "code": "PIA",
                "team": "mclaren",
                "positions": [2, 2],
                "gaps_ms": [901, 348],
                "pit_laps": [2],
            },
            {
                "driver_id": "hadjar",
                "code": "HAD",
                "team": "rb",
                "positions": [],
                "gaps_ms": [],
                "pit_laps": [],
            },
        ],
    }


def test_frame_requires_a_non_negative_time() -> None:
    assert client_with(MemorySource()).get("/races/2025/1/frame?t=-1").status_code == 422
    assert client_with(MemorySource()).get("/races/2025/1/frame").status_code == 422


def test_frame_as_json() -> None:
    response = client_with(MemorySource()).get("/races/2025/1/frame?t=200")

    assert response.status_code == 200
    body = response.json()
    assert body["at_seconds"] == 200.0
    assert body["fastest_lap"] == {"driver_id": "norris", "lap": 1, "time_ms": 117099}
    assert body["drivers"][1] == {
        "driver_id": "piastri",
        "position": 2,
        "laps_completed": 1,
        "distance": 1 + 82000 / 90000,
        "gap_ms": 395,
        "status": "running",
    }


def test_missing_race_is_404_and_dead_catalogue_is_503() -> None:
    assert client_with(MissingRaceSource()).get("/races/2025/3/trace").status_code == 404
    assert client_with(DeadSource()).get("/races/2025/1/trace").status_code == 503
