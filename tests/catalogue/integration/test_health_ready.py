import pytest
from fastapi.testclient import TestClient

from catalogue.infrastructure.settings import Settings
from catalogue.main import create_app

pytestmark = pytest.mark.integration


def test_ready_reports_ok_with_a_live_database(database_url: str) -> None:
    client = TestClient(create_app(Settings()))

    response = client.get("/health/ready")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
