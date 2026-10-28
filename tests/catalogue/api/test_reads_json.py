from fastapi.testclient import TestClient

from catalogue.api.dependencies import get_race_reader
from catalogue.features.read_races import RaceReader
from catalogue.main import create_app

from tests.catalogue.fakes import MemorySource, unreachable_settings


def client_with_reader(reader: RaceReader) -> TestClient:
    app = create_app(unreachable_settings())
    app.dependency_overrides[get_race_reader] = lambda: reader
    return TestClient(app)


def test_trace_as_json() -> None:
    response = client_with_reader(MemorySource()).get("/races/2025/1/trace")

    assert response.status_code == 200
    assert response.json() == {
        "season": 2025,
        "round_number": 1,
        "total_laps": 2,
        "race_time_ms": 207652,
        "fastest_by_lap": [
            {"driver_id": "norris", "lap": 1, "time_ms": 117099},
            {"driver_id": "piastri", "lap": 2, "time_ms": 90000},
        ],
        "series": [
            {
                "driver_id": "norris",
                "code": "NOR",
                "team": "mclaren",
                "grid": 1,
                "classified": True,
                "positions": [1, 1],
                "gaps_ms": [0, 0],
                "laps_down": [0, 0],
                "pit_laps": [],
            },
            {
                "driver_id": "piastri",
                "code": "PIA",
                "team": "mclaren",
                "grid": 2,
                "classified": True,
                "positions": [2, 2],
                "gaps_ms": [901, 348],
                "laps_down": [0, 0],
                "pit_laps": [2],
            },
            {
                "driver_id": "hadjar",
                "code": "HAD",
                "team": "rb",
                "grid": 11,
                "classified": False,
                "positions": [],
                "gaps_ms": [],
                "laps_down": [],
                "pit_laps": [],
            },
        ],
    }


def test_replay_as_json() -> None:
    response = client_with_reader(MemorySource()).get("/races/2025/1/replay")

    assert response.status_code == 200
    assert response.json() == {
        "season": 2025,
        "round_number": 1,
        "total_laps": 2,
        "fastest_laps": [
            {"at_ms": 117099, "driver_id": "norris", "lap": 1, "time_ms": 117099},
            {"at_ms": 207652, "driver_id": "norris", "lap": 2, "time_ms": 90553},
            {"at_ms": 208000, "driver_id": "piastri", "lap": 2, "time_ms": 90000},
        ],
        "drivers": [
            {
                "driver_id": "norris",
                "code": "NOR",
                "team": "mclaren",
                "grid": 1,
                "classified": True,
                "keyframes": [
                    {"at_ms": 0, "distance": 0.0, "in_pit": False},
                    {"at_ms": 117099, "distance": 1.0, "in_pit": False},
                    {"at_ms": 207652, "distance": 2.0, "in_pit": False},
                ],
            },
            {
                "driver_id": "piastri",
                "code": "PIA",
                "team": "mclaren",
                "grid": 2,
                "classified": True,
                "keyframes": [
                    {"at_ms": 0, "distance": 0.0, "in_pit": False},
                    {"at_ms": 118000, "distance": 1.0, "in_pit": False},
                    {"at_ms": 194659, "distance": 1.97, "in_pit": True},
                    {"at_ms": 208000, "distance": 1.97, "in_pit": True},
                    {"at_ms": 208000, "distance": 2.0, "in_pit": False},
                ],
            },
            {
                "driver_id": "hadjar",
                "code": "HAD",
                "team": "rb",
                "grid": 11,
                "classified": False,
                "keyframes": [{"at_ms": 0, "distance": 0.0, "in_pit": False}],
            },
        ],
    }


def test_trace_of_a_round_that_is_not_ingested_is_404() -> None:
    response = client_with_reader(MemorySource()).get("/races/2025/9/trace")

    assert response.status_code == 404
