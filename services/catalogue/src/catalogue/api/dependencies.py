from collections.abc import Iterator
from typing import Annotated

from fastapi import Depends, Request
from sqlalchemy.orm import Session

from catalogue.features.ingest_race import RaceStore
from catalogue.infrastructure.jolpica_pages import FetchJson
from catalogue.infrastructure.race_store import SqlRaceStore


def get_session(request: Request) -> Iterator[Session]:
    with request.app.state.session_factory() as session:
        yield session


def get_fetch(request: Request) -> FetchJson:
    fetch: FetchJson = request.app.state.fetch
    return fetch


def get_race_store(session: Annotated[Session, Depends(get_session)]) -> RaceStore:
    return SqlRaceStore(session)


DbSession = Annotated[Session, Depends(get_session)]
Fetch = Annotated[FetchJson, Depends(get_fetch)]
RaceStoreDep = Annotated[RaceStore, Depends(get_race_store)]
