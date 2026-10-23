"""FastAPI application factory."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from fancut import __version__
from fancut.config import Settings, get_settings


class Health(BaseModel):
    status: str
    version: str
    environment: str


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or get_settings()
    app = FastAPI(title="FanCut API", version=__version__)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health", response_model=Health, tags=["ops"])
    def health() -> Health:
        return Health(status="ok", version=__version__, environment=settings.environment)

    return app
