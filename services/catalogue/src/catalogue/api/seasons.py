from fastapi import APIRouter

from catalogue.api.dependencies import DbSession, Fetch, RaceReaderDep, ScheduleStoreDep
from catalogue.entities.race_snapshot import RaceSummary
from catalogue.entities.units import Season
from catalogue.features.ingest_season import ingest_season
from catalogue.features.read_races import list_races

router = APIRouter(prefix="/seasons")


@router.get("")
def seasons(reader: RaceReaderDep) -> dict[str, list[int]]:
    return {"seasons": list(reader.seasons())}


@router.post("/{season}/ingest")
def ingest(
    season: Season, fetch: Fetch, store: ScheduleStoreDep, session: DbSession
) -> dict[str, int]:
    count = ingest_season(fetch, store, season=season)
    session.commit()
    return {"races": count}


@router.get("/{season}/races")
def races(season: Season, reader: RaceReaderDep) -> list[RaceSummary]:
    return list(list_races(reader, season))
