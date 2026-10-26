from collections.abc import Iterator
from typing import Annotated

from fastapi import Depends, Path, Request
from sqlalchemy.orm import Session

from catalogue.entities.units import RoundNumber, Season
from catalogue.features.ingest_race import RaceStore
from catalogue.features.ingest_season import ScheduleStore
from catalogue.features.read_races import RaceReader
from catalogue.infrastructure.jolpica_pages import FetchJson
from catalogue.infrastructure.race_reader import SqlRaceReader
from catalogue.infrastructure.race_store import SqlRaceStore


def get_session(request: Request) -> Iterator[Session]:
    with request.app.state.session_factory() as session:
        yield session


def get_fetch(request: Request) -> FetchJson:
    fetch: FetchJson = request.app.state.fetch
    return fetch


def get_race_store(session: Annotated[Session, Depends(get_session)]) -> SqlRaceStore:
    return SqlRaceStore(session)


def get_race_reader(session: Annotated[Session, Depends(get_session)]) -> RaceReader:
    return SqlRaceReader(session)


DbSession = Annotated[Session, Depends(get_session)]
Fetch = Annotated[FetchJson, Depends(get_fetch)]
RaceStoreDep = Annotated[RaceStore, Depends(get_race_store)]
ScheduleStoreDep = Annotated[ScheduleStore, Depends(get_race_store)]
RaceReaderDep = Annotated[RaceReader, Depends(get_race_reader)]
SeasonPath = Annotated[Season, Path(ge=1950, le=2100)]
RoundPath = Annotated[RoundNumber, Path(ge=1, le=30)]
StandingsRoundPath = Annotated[RoundNumber, Path(ge=0, le=30)]
