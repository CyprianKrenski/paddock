from fastapi.testclient import TestClient
from pydantic import SecretStr

from catalogue.infrastructure.settings import Settings
from catalogue.main import create_app

UNREACHABLE = Settings(
    postgres_user="x", postgres_password=SecretStr("x"), postgres_db="x", postgres_port=1
)


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
