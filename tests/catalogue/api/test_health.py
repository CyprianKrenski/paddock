from fastapi.testclient import TestClient

from catalogue.main import create_app

from tests.catalogue.fakes import unreachable_settings

UNREACHABLE = unreachable_settings()


def test_live_reports_ok() -> None:
    client = TestClient(create_app(UNREACHABLE))

    response = client.get("/health/live")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_ready_reports_503_when_database_is_unreachable() -> None:
    client = TestClient(create_app(UNREACHABLE))

    response = client.get("/health/ready")

    assert response.status_code == 503
    assert response.json() == {"detail": "database unavailable"}
