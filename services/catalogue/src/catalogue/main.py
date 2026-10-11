from fastapi import FastAPI

from catalogue.api.health import router as health_router
from catalogue.infrastructure.db import session_factory
from catalogue.infrastructure.settings import Settings


def create_app(settings: Settings) -> FastAPI:
    app = FastAPI(title="catalogue")
    app.state.session_factory = session_factory(settings.database_url)
    app.include_router(health_router)
    return app
