from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from catalogue.entities.errors import MalformedSourceRawData
from catalogue.features.ingest_race import RaceNotFound
from catalogue.features.ingest_season import SeasonNotFound
from catalogue.features.read_races import RaceNotIngested, SeasonNotLoaded, StandingsNotLoaded
from catalogue.infrastructure.jolpica import UpstreamRequestFailed


def not_found(request: Request, error: Exception) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": str(error)})


def source_failed(request: Request, error: Exception) -> JSONResponse:
    return JSONResponse(status_code=502, content={"detail": f"source failed: {error}"})


def register_error_handlers(app: FastAPI) -> None:
    for missing in (
        RaceNotFound,
        SeasonNotFound,
        RaceNotIngested,
        SeasonNotLoaded,
        StandingsNotLoaded,
    ):
        app.add_exception_handler(missing, not_found)
    for failed in (UpstreamRequestFailed, ValidationError, MalformedSourceRawData):
        app.add_exception_handler(failed, source_failed)
