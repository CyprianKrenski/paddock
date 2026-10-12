from collections.abc import Mapping
from typing import Any

from fastapi.testclient import TestClient
from pydantic import SecretStr

from catalogue.api.dependencies import get_fetch, get_race_store, get_session
from catalogue.entities.race_snapshot import RaceSnapshot
from catalogue.infrastructure.jolpica import RetriesExhausted
from catalogue.infrastructure.settings import Settings
from catalogue.main import create_app

from catalogue_tests.factories import EnvelopeFactory, ResultFactory, ResultsRaceFactory

UNREACHABLE = Settings(
    postgres_user="x", postgres_password=SecretStr("x"), postgres_db="x", postgres_port=1
)


class RecordingStore:
    def __init__(self) -> None:
        self.saved: list[RaceSnapshot] = []

    def save(self, snapshot: RaceSnapshot) -> None:
        self.saved.append(snapshot)


def client_with(fetch: Any, store: RecordingStore) -> TestClient:
    app = create_app(UNREACHABLE)
    app.dependency_overrides[get_fetch] = lambda: fetch
    app.dependency_overrides[get_race_store] = lambda: store
    return TestClient(app)


def scripted(by_path: Mapping[str, dict[str, Any]]) -> Any:
    def fetch(path: str, params: Mapping[str, str | int] | None = None) -> dict[str, Any]:
        return by_path[path]

    return fetch


def test_ingest_returns_counts() -> None:
    race = ResultsRaceFactory.build(Results=[ResultFactory.build()])
    fetch = scripted(
        {
            "/2025/1/results.json": EnvelopeFactory.build(MRData__RaceTable__Races=[race]),
            "/2025/1/laps.json": EnvelopeFactory.build(MRData__total="0"),
            "/2025/1/pitstops.json": EnvelopeFactory.build(MRData__total="0"),
        }
    )
    store = RecordingStore()

    response = client_with(fetch, store).post("/races/2025/1/ingest")

    assert response.status_code == 200
    assert response.json() == {"drivers": 1, "laps": 0, "pit_stops": 0}
    assert len(store.saved) == 1


def test_unknown_round_is_404() -> None:
    fetch = scripted({"/2025/99/results.json": EnvelopeFactory.build(MRData__total="0")})

    response = client_with(fetch, RecordingStore()).post("/races/2025/99/ingest")

    assert response.status_code == 404
    assert response.json() == {"detail": "season 2025 round 99 is unknown to the source"}


def test_source_failure_is_502() -> None:
    def failing(path: str, params: Mapping[str, str | int] | None = None) -> dict[str, Any]:
        raise RetriesExhausted("gave up after 4 attempts on /2025/1/results.json")

    response = client_with(failing, RecordingStore()).post("/races/2025/1/ingest")

    assert response.status_code == 502
    assert response.json() == {
        "detail": "source failed: gave up after 4 attempts on /2025/1/results.json"
    }


class SessionWhoseCommitFails:
    def commit(self) -> None:
        raise RuntimeError("connection lost during commit")


def test_failed_commit_is_a_server_error_not_a_silent_200() -> None:
    race = ResultsRaceFactory.build(Results=[ResultFactory.build()])
    fetch = scripted(
        {
            "/2025/1/results.json": EnvelopeFactory.build(MRData__RaceTable__Races=[race]),
            "/2025/1/laps.json": EnvelopeFactory.build(MRData__total="0"),
            "/2025/1/pitstops.json": EnvelopeFactory.build(MRData__total="0"),
        }
    )
    app = create_app(UNREACHABLE)
    app.dependency_overrides[get_fetch] = lambda: fetch
    app.dependency_overrides[get_race_store] = lambda: RecordingStore()
    app.dependency_overrides[get_session] = lambda: SessionWhoseCommitFails()

    response = TestClient(app, raise_server_exceptions=False).post("/races/2025/1/ingest")

    assert response.status_code == 500
