import httpx2
from fastapi import FastAPI

from catalogue.api.errors import register_error_handlers
from catalogue.api.health import router as health_router
from catalogue.api.races import router as races_router
from catalogue.api.seasons import router as seasons_router
from catalogue.infrastructure.db import session_factory
from catalogue.infrastructure.jolpica import JolpicaClient
from catalogue.infrastructure.jolpica_cache import CachedJolpica
from catalogue.infrastructure.raw_responses import SqlRawResponseStore
from catalogue.infrastructure.settings import Settings


def create_app(settings: Settings) -> FastAPI:
    app = FastAPI(title="catalogue")
    sessions = session_factory(settings.database_url)
    http = httpx2.Client(
        base_url=settings.jolpica_base_url,
        headers={"User-Agent": settings.jolpica_user_agent},
        timeout=settings.jolpica_timeout_seconds,
    )
    app.state.session_factory = sessions
    app.state.fetch = CachedJolpica(JolpicaClient(http).get_json, SqlRawResponseStore(sessions))
    register_error_handlers(app)
    app.include_router(health_router)
    app.include_router(seasons_router)
    app.include_router(races_router)
    return app


def from_env() -> FastAPI:
    return create_app(Settings())
