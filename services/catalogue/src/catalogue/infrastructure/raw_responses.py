from datetime import UTC, datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session, sessionmaker

from catalogue.entities.models import RawResponse

JsonObject = dict[str, Any]


class SqlRawResponseStore:
    def __init__(self, sessions: sessionmaker[Session]) -> None:
        self._sessions = sessions

    def get(self, url: str) -> JsonObject | None:
        with self._sessions() as session:
            return session.scalar(select(RawResponse.body).where(RawResponse.url == url))

    def put(self, url: str, body: JsonObject) -> None:
        row = insert(RawResponse).values(url=url, fetched_at=datetime.now(UTC), body=body)
        upsert = row.on_conflict_do_update(
            index_elements=[RawResponse.url],
            set_={"body": row.excluded.body, "fetched_at": row.excluded.fetched_at},
        )
        with self._sessions.begin() as session:
            session.execute(upsert)
