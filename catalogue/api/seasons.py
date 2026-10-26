from fastapi import APIRouter

from catalogue.api.dependencies import (
    DbSession,
    Fetch,
    RaceReaderDep,
    ScheduleStoreDep,
    SeasonPath,
    StandingsRoundPath,
)
from catalogue.entities.race_snapshot import RaceSummary, StandingRow
from catalogue.features.ingest_season import ingest_season
from catalogue.features.read_races import list_races, season_standings

router = APIRouter(prefix="/seasons")


@router.get("")
def seasons(reader: RaceReaderDep) -> dict[str, list[int]]:
    return {"seasons": list(reader.seasons())}


@router.post("/{season}/ingest")
def ingest(
    season: SeasonPath, fetch: Fetch, store: ScheduleStoreDep, session: DbSession
) -> dict[str, int]:
    count = ingest_season(fetch, store, season=season)
    session.commit()
    return {"races": count}


@router.get("/{season}/races")
def races(season: SeasonPath, reader: RaceReaderDep) -> list[RaceSummary]:
    return list(list_races(reader, season))


@router.get("/{season}/standings/{round_number}")
def standings(
    season: SeasonPath, round_number: StandingsRoundPath, reader: RaceReaderDep
) -> list[StandingRow]:
    return list(season_standings(reader, season, round_number))
