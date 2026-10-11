from fastapi import FastAPI

from catalogue.api.health import router as health_router


def create_app() -> FastAPI:
    app = FastAPI(title="catalogue")
    app.include_router(health_router)
    return app
