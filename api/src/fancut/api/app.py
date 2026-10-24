"""FastAPI application: REST for profiles and channels, SSE for the live channel,
and the Drama Engine's MCP server mounted at ``/mcp``."""

from collections.abc import AsyncGenerator, AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.sse import EventSourceResponse, ServerSentEvent
from mcp.server.transport_security import TransportSecuritySettings
from pydantic import BaseModel, Field

from fancut import __version__
from fancut.agents.profile_compiler import CompiledProfile, ProfileCompiler
from fancut.api.channel import ChannelSession
from fancut.api.mcp import build_mcp
from fancut.api.services import Services, build_services
from fancut.config import Settings, get_settings
from fancut.profile import FanProfile, Language
from fancut.telemetry import setup_tracing


class Health(BaseModel):
    status: str
    version: str
    environment: str
    model: bool  # a language model is configured


class CompileRequest(BaseModel):
    message: str = Field(min_length=3, max_length=500)


class Compiled(BaseModel):
    profile_id: str
    compiled: CompiledProfile


class ChannelRequest(BaseModel):
    profile_id: str
    language: Language | None = None
    speed: float = Field(default=60.0, ge=1, le=600)
    until_minute: int | None = Field(default=None, ge=1, le=120)


class ChannelCreated(BaseModel):
    channel_id: str
    stream: str
    audit: str


class FocusRequest(BaseModel):
    match_id: str | None = None  # None releases the focus


def create_app(settings: Settings | None = None, services: Services | None = None) -> FastAPI:
    settings = settings or get_settings()
    services = services or build_services(settings)
    mcp = build_mcp(services)

    @asynccontextmanager
    async def lifespan(_app: FastAPI) -> AsyncGenerator[None]:
        setup_tracing(settings)
        async with mcp.session_manager.run():
            yield

    app = FastAPI(title="FanCut API", version=__version__, lifespan=lifespan)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    security = TransportSecuritySettings(allowed_hosts=settings.mcp_allowed_hosts)
    app.mount(
        "/mcp", mcp.streamable_http_app(streamable_http_path="/", transport_security=security)
    )

    @app.get("/health", response_model=Health, tags=["ops"])
    def health() -> Health:
        return Health(
            status="ok",
            version=__version__,
            environment=settings.environment,
            model=services.model is not None,
        )

    @app.get("/matchday", tags=["matchday"])
    def matchday() -> dict[str, Any]:
        md = services.matchday
        teams = {t.id: t for m in md.matches for t in (m.meta.home, m.meta.away)}
        return {
            "id": md.id,
            "kickoff_utc": md.kickoff_utc.isoformat(),
            "fixtures": [
                {
                    "match_id": m.meta.match_id,
                    "home": {
                        "id": m.meta.home.id,
                        "name": m.meta.home.name,
                        "short": m.meta.home.short_name,
                        "color": m.meta.home.color,
                    },
                    "away": {
                        "id": m.meta.away.id,
                        "name": m.meta.away.name,
                        "short": m.meta.away.short_name,
                        "color": m.meta.away.color,
                    },
                    "stakes": m.meta.stakes.value,
                }
                for m in md.matches
            ],
            "table": [
                {
                    "position": i + 1,
                    "team_id": r.team_id,
                    "team": teams[r.team_id].name,
                    "short": teams[r.team_id].short_name,
                    "points": r.points,
                    "goal_difference": r.goal_difference,
                }
                for i, r in enumerate(md.table().standings())
            ],
        }

    @app.get("/profiles/demo", response_model=dict[str, FanProfile], tags=["profiles"])
    def demo_profiles() -> dict[str, FanProfile]:
        return services.profiles.demo()

    @app.post("/profiles", tags=["profiles"])
    def add_profile(profile: FanProfile) -> dict[str, str]:
        return {"profile_id": services.profiles.add(profile)}

    @app.post("/profiles/compile", response_model=Compiled, tags=["profiles"])
    async def compile_profile(request: CompileRequest) -> Compiled:
        compiled = await ProfileCompiler(services.model).compile(request.message)
        return Compiled(profile_id=services.profiles.add(compiled.profile), compiled=compiled)

    @app.post("/channels", response_model=ChannelCreated, tags=["channel"])
    def create_channel(request: ChannelRequest) -> ChannelCreated:
        profile = services.profiles.get(request.profile_id)
        if profile is None:
            raise HTTPException(status_code=404, detail="unknown profile")
        session = ChannelSession(
            services.matchday,
            profile,
            services.commentary,
            language=request.language,
            speed=request.speed,
            until_minute=request.until_minute,
        )
        channel_id = services.remember(session)
        return ChannelCreated(
            channel_id=channel_id,
            stream=f"/channels/{channel_id}/stream",
            audit=f"/channels/{channel_id}/audit",
        )

    @app.get("/channels/{channel_id}/stream", response_class=EventSourceResponse, tags=["channel"])
    async def stream(channel_id: str) -> AsyncIterator[ServerSentEvent]:
        session = _session(services, channel_id)
        async for overlay in session.overlays():
            yield ServerSentEvent(
                event=overlay.type.value, id=str(overlay.seq), data=overlay.model_dump(mode="json")
            )

    @app.post("/channels/{channel_id}/focus", tags=["channel"])
    def focus(channel_id: str, request: FocusRequest) -> dict[str, str | None]:
        """Lock the pitch to one match while the Director keeps deciding; null releases."""
        session = _session(services, channel_id)
        known = {m.meta.match_id for m in services.matchday.matches}
        if request.match_id is not None and request.match_id not in known:
            raise HTTPException(status_code=404, detail="unknown match")
        session.set_focus(request.match_id)
        return {"focus": session.focus}

    @app.get("/channels/{channel_id}/audit", tags=["channel"])
    def audit(channel_id: str) -> list[dict[str, Any]]:
        return _session(services, channel_id).audit

    return app


def _session(services: Services, channel_id: str) -> ChannelSession:
    session = services.sessions.get(channel_id)
    if session is None:
        raise HTTPException(status_code=404, detail="unknown channel")
    return session
