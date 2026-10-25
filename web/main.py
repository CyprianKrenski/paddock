from pathlib import Path

from fastapi import FastAPI
from fastapi.templating import Jinja2Templates

from web.api.errors import register_error_handlers
from web.api.health import router as health_router
from web.api.pages import router as pages_router
from web.infrastructure.clients import HttpCatalogue
from web.infrastructure.http import upstream_client
from web.infrastructure.settings import Settings

TEMPLATES = Path(__file__).parent / "templates"


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or Settings()
    app = FastAPI(title="web")
    app.state.catalogue = HttpCatalogue(
        upstream_client(settings.catalogue_url, settings.upstream_timeout_seconds)
    )
    app.state.templates = Jinja2Templates(directory=TEMPLATES)
    register_error_handlers(app)
    app.include_router(health_router)
    app.include_router(pages_router)
    return app


def from_env() -> FastAPI:
    return create_app(Settings())
