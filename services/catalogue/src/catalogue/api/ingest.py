from fastapi import APIRouter, HTTPException
from pydantic import ValidationError

from catalogue.api.dependencies import DbSession, Fetch, RaceStoreDep
from catalogue.entities.errors import MalformedSourceRawData
from catalogue.features.ingest_race import IngestSummary, RaceNotFound, ingest_race
from catalogue.infrastructure.jolpica import UpstreamRequestFailed

router = APIRouter(prefix="/races")


@router.post("/{season}/{round_number}/ingest")
def ingest(
    season: int, round_number: int, fetch: Fetch, store: RaceStoreDep, session: DbSession
) -> IngestSummary:
    try:
        summary = ingest_race(fetch, store, season=season, round_number=round_number)
    except RaceNotFound as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except (UpstreamRequestFailed, ValidationError, MalformedSourceRawData) as error:
        raise HTTPException(status_code=502, detail=f"source failed: {error}") from error
    session.commit()
    return summary
