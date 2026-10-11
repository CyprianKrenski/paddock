import pytest
from sqlalchemy.orm import Session

from catalogue.features.stores import RawResponseStore
from catalogue.infrastructure.raw_responses import SqlRawResponseStore

pytestmark = pytest.mark.integration


def test_missing_url_is_none(db_session: Session) -> None:
    store: RawResponseStore = SqlRawResponseStore(db_session)

    assert store.get("/2025/1/laps.json?limit=100&offset=0") is None


def test_put_then_get_returns_the_body(db_session: Session) -> None:
    store = SqlRawResponseStore(db_session)

    store.put("/2025/1/laps.json?limit=100&offset=0", {"MRData": {"total": "921"}})

    assert store.get("/2025/1/laps.json?limit=100&offset=0") == {"MRData": {"total": "921"}}


def test_put_twice_keeps_the_latest_body(db_session: Session) -> None:
    store = SqlRawResponseStore(db_session)

    store.put("/x.json", {"v": 1})
    store.put("/x.json", {"v": 2})

    assert store.get("/x.json") == {"v": 2}
