from fastapi.testclient import TestClient

from catalogue.api.dependencies import get_fetch, get_race_store, get_session
from catalogue.infrastructure.jolpica_pages import FetchJson
from catalogue.main import create_app

from tests.catalogue.factories import EnvelopeFactory, ResultFactory, ResultsRaceFactory
from tests.catalogue.fakes import FailingFetch, RecordingStore, ScriptedFetch, unreachable_settings


def client_with(fetch: FetchJson, store: RecordingStore) -> TestClient:
    app = create_app(unreachable_settings())
    app.dependency_overrides[get_fetch] = lambda: fetch
    app.dependency_overrides[get_race_store] = lambda: store
    return TestClient(app)


def one_driver_race() -> ScriptedFetch:
    race = ResultsRaceFactory.build(Results=[ResultFactory.build()])
    return ScriptedFetch(
        {
            "/2025/1/results.json": EnvelopeFactory.build(MRData__RaceTable__Races=[race]),
            "/2025/1/laps.json": EnvelopeFactory.build(MRData__total="0"),
            "/2025/1/pitstops.json": EnvelopeFactory.build(MRData__total="0"),
        }
    )


def test_ingest_returns_counts() -> None:
    store = RecordingStore()

    response = client_with(one_driver_race(), store).post("/races/2025/1/ingest")

    assert response.status_code == 200
    assert response.json() == {"drivers": 1, "laps": 0, "pit_stops": 0}
    assert len(store.saved) == 1


def test_out_of_range_season_or_round_never_reaches_the_source() -> None:
    client = client_with(ScriptedFetch({}), RecordingStore())

    assert client.post("/races/1800/1/ingest").status_code == 422
    assert client.post("/races/2025/0/ingest").status_code == 422
    assert client.get("/seasons/2025/standings/0").status_code == 200


def test_unknown_round_is_404() -> None:
    fetch = ScriptedFetch({"/2025/30/results.json": EnvelopeFactory.build(MRData__total="0")})

    response = client_with(fetch, RecordingStore()).post("/races/2025/30/ingest")

    assert response.status_code == 404
    assert response.json() == {"detail": "season 2025 round 30 is unknown to the source"}


def test_source_failure_is_502() -> None:
    response = client_with(FailingFetch(), RecordingStore()).post("/races/2025/1/ingest")

    assert response.status_code == 502
    assert response.json() == {
        "detail": "source failed: gave up after 4 attempts on /2025/1/results.json"
    }


class SessionWhoseCommitFails:
    def commit(self) -> None:
        raise RuntimeError("connection lost during commit")


def test_failed_commit_is_a_server_error_not_a_silent_200() -> None:
    app = create_app(unreachable_settings())
    app.dependency_overrides[get_fetch] = lambda: one_driver_race()
    app.dependency_overrides[get_race_store] = lambda: RecordingStore()
    app.dependency_overrides[get_session] = lambda: SessionWhoseCommitFails()

    response = TestClient(app, raise_server_exceptions=False).post("/races/2025/1/ingest")

    assert response.status_code == 500
