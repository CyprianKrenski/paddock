import httpx2
from fastapi import FastAPI

from analysis.api.errors import register_error_handlers
from analysis.api.health import router as health_router
from analysis.api.races import router as races_router
from analysis.infrastructure.catalogue_client import HttpCatalogue
from analysis.infrastructure.settings import Settings


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or Settings()
    app = FastAPI(title="analysis")
    http = httpx2.Client(
        base_url=settings.catalogue_url, timeout=settings.catalogue_timeout_seconds
    )
    app.state.source = HttpCatalogue(http)
    register_error_handlers(app)
    app.include_router(health_router)
    app.include_router(races_router)
    return app


def from_env() -> FastAPI:
    return create_app(Settings())
