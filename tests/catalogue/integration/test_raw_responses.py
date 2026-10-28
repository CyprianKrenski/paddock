import pytest
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session, sessionmaker

from catalogue.entities.models import RawResponse
from catalogue.infrastructure.jolpica_cache import RawResponseStore
from catalogue.infrastructure.raw_responses import SqlRawResponseStore

pytestmark = pytest.mark.integration


def test_missing_url_is_none(db_sessions: sessionmaker[Session]) -> None:
    store: RawResponseStore = SqlRawResponseStore(db_sessions)

    assert store.get("/1900/1/laps.json?limit=100&offset=0") is None


def test_put_twice_keeps_the_latest_body(db_sessions: sessionmaker[Session]) -> None:
    store = SqlRawResponseStore(db_sessions)

    store.put("/2025/1/laps.json?limit=100&offset=0", {"MRData": {"total": "921"}})
    store.put("/2025/1/laps.json?limit=100&offset=0", {"MRData": {"total": "922"}})

    assert store.get("/2025/1/laps.json?limit=100&offset=0") == {"MRData": {"total": "922"}}


def test_store_commits_its_own_work_but_the_test_transaction_stays_contained(
    database_url: str, db_sessions: sessionmaker[Session]
) -> None:
    SqlRawResponseStore(db_sessions).put("/y.json", {"v": 1})

    with create_engine(database_url).connect() as outsider:
        visible = outsider.scalar(
            select(func.count()).select_from(RawResponse).where(RawResponse.url == "/y.json")
        )

    assert visible == 0
