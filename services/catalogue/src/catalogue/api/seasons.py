from fastapi import APIRouter, HTTPException
from pydantic import ValidationError

from catalogue.api.dependencies import DbSession, Fetch, RaceReaderDep, ScheduleStoreDep
from catalogue.entities.race_snapshot import RaceSummary
from catalogue.features.ingest_season import SeasonNotFound, ingest_season
from catalogue.features.read_races import SeasonNotFound as SeasonNotLoaded
from catalogue.features.read_races import list_races, list_seasons
from catalogue.infrastructure.jolpica import UpstreamRequestFailed

router = APIRouter(prefix="/seasons")


@router.get("")
def seasons(reader: RaceReaderDep) -> dict[str, list[int]]:
    return {"seasons": list(list_seasons(reader))}


@router.post("/{season}/ingest")
def ingest(
    season: int, fetch: Fetch, store: ScheduleStoreDep, session: DbSession
) -> dict[str, int]:
    try:
        count = ingest_season(fetch, store, season=season)
    except SeasonNotFound as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except (UpstreamRequestFailed, ValidationError) as error:
        raise HTTPException(status_code=502, detail=f"source failed: {error}") from error
    session.commit()
    return {"races": count}


@router.get("/{season}/races")
def races(season: int, reader: RaceReaderDep) -> list[RaceSummary]:
    try:
        return list(list_races(reader, season))
    except SeasonNotLoaded as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
