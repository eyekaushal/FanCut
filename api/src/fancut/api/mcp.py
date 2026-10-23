"""An MCP server over the Drama Engine, so any agent (or a studio tool) can ask
"how dramatic is this match right now?" and "what would this fan be watching?"."""

from functools import cache
from typing import Any

from mcp.server.mcpserver import MCPServer

from fancut.api.services import Services
from fancut.director.director import Director
from fancut.director.relevance import relevance
from fancut.drama import DramaEngine, DramaSnapshot
from fancut.matchday.state import MatchdayState

INSTRUCTIONS = """Tools over FanCut's synthetic matchday: ten fictional Premier-League-style
matches played at once. Use matchday_overview first, then match_drama for one match at a
minute, or rank_matches to see which match a given fan's channel would show."""


def build_mcp(services: Services) -> MCPServer:
    server = MCPServer(name="fancut-drama", instructions=INSTRUCTIONS)
    matchday = services.matchday

    @cache
    def timeline(match_id: str) -> list[DramaSnapshot]:
        match = matchday.match(match_id)
        return DramaEngine(match.meta).run(match.events)

    @server.tool(description="Fixtures, stakes and the league table at kickoff.")
    def matchday_overview() -> dict[str, Any]:
        names = {t.id: t.name for m in matchday.matches for t in (m.meta.home, m.meta.away)}
        return {
            "matchday": matchday.id,
            "kickoff_utc": matchday.kickoff_utc.isoformat(),
            "fixtures": [
                {
                    "match_id": m.meta.match_id,
                    "home": m.meta.home.name,
                    "away": m.meta.away.name,
                    "stakes": m.meta.stakes.value,
                }
                for m in matchday.matches
            ],
            "table_at_kickoff": [
                {"position": i + 1, "team": names[row.team_id], "points": row.points}
                for i, row in enumerate(matchday.table().standings())
            ],
        }

    @server.tool(
        description="Score, win probability, suspense and pressure of one match at a minute."
    )
    def match_drama(match_id: str, minute: int) -> dict[str, Any]:
        snapshots = [s for s in timeline(match_id) if s.minute <= minute]
        if not snapshots:
            return {"match_id": match_id, "minute": minute, "status": "not started"}
        s = snapshots[-1]
        return {
            "match_id": match_id,
            "minute": s.minute,
            "score": list(s.score),
            "win_probability": {"home": s.win_probability.home, "draw": s.win_probability.draw,
                                "away": s.win_probability.away},
            "suspense": round(s.suspense, 3),
            "pressure": [round(p, 3) for p in s.pressure],
            "momentum": round(s.momentum, 3),
            "control": round(s.control, 3),
            "excitement_so_far": round(s.excitement, 3),
        }  # fmt: skip

    @server.tool(description="Every match ranked by relevance for a fan at a matchday minute.")
    def rank_matches(fan: str, minute: int) -> dict[str, Any]:
        profile = services.profiles.get(fan)
        if profile is None:
            return {"error": f"unknown fan '{fan}'"}
        state = MatchdayState(matchday)
        director = Director(profile)
        for event in matchday.events():
            if event.t / 60 > minute:
                break
            director.observe(state.update(event), state)
        ranked = sorted(
            (relevance(profile, feed, state) for feed in state.feeds.values()),
            key=lambda r: -r.value,
        )
        return {
            "fan": fan,
            "minute": minute,
            "on_air": director.on_air,
            "ranking": [r.model_dump() for r in ranked],
        }

    return server
