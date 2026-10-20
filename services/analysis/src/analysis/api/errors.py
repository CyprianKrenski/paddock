from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from analysis.entities.errors import CatalogueUnavailable, RaceNotAvailable


def not_found(request: Request, error: Exception) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": str(error)})


def unavailable(request: Request, error: Exception) -> JSONResponse:
    return JSONResponse(status_code=503, content={"detail": str(error)})


def register_error_handlers(app: FastAPI) -> None:
    app.add_exception_handler(RaceNotAvailable, not_found)
    app.add_exception_handler(CatalogueUnavailable, unavailable)
