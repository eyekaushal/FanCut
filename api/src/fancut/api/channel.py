"""One fan's live channel: plays the matchday and emits ``overlay.v1`` events.

Cuts go out the instant the Director decides, carrying the correct reference line.
The model-written line follows as a ``narration`` event when it is ready, so a slow or
failing model never delays the picture.
"""

import asyncio
from collections.abc import AsyncIterator
from typing import Any

from fancut.agents.commentary import Commentary, Narration
from fancut.agents.facts import CutFacts, facts_for
from fancut.agents.templates import narrate_cut
from fancut.api.overlay import Overlay, OverlayType, ScoreLine, TableLine
from fancut.director.director import Decision, Director
from fancut.matchday.matchday import Matchday
from fancut.matchday.state import MatchdayState, Update
from fancut.profile import FanProfile, Language
from fancut.sim.replay import Replayer
from fancut.sim.schema import EventType

SCOREBOARD_EVERY = 30.0  # seconds of matchday time
NARRATION_GRACE = 15.0  # wall-clock seconds to wait for late narrations at the end
VISIBLE_ACTIONS = {
    EventType.PASS,
    EventType.CARRY,
    EventType.SHOT,
    EventType.GOAL,
    EventType.SAVE,
    EventType.TACKLE,
    EventType.INTERCEPTION,
    EventType.CORNER,
    EventType.FREE_KICK,
    EventType.FOUL,
    EventType.CARD,
    EventType.OFFSIDE,
}


class ChannelSession:
    def __init__(
        self,
        matchday: Matchday,
        profile: FanProfile,
        commentary: Commentary,
        language: Language | None = None,
        speed: float = 60.0,
        until_minute: int | None = None,
    ) -> None:
        self.profile = profile
        self.language = language or profile.language
        self.audit: list[dict[str, Any]] = []
        self._matchday = matchday
        self._commentary = commentary
        self._speed = speed
        self._until = until_minute
        self._seq = 0
        self._t = 0.0

    async def overlays(self) -> AsyncIterator[Overlay]:
        state = MatchdayState(self._matchday)
        director = Director(self.profile)
        narrations: asyncio.Queue[tuple[int, Narration]] = asyncio.Queue()
        pending: set[asyncio.Task[None]] = set()
        next_scoreboard = 0.0

        events = list(self._matchday.events())
        async for event in Replayer(events, speed=self._speed).stream():
            if self._until is not None and event.minute > self._until:
                break
            self._t = event.t
            update = state.update(event)
            for decision in director.observe(update, state):
                yield self._cut(
                    decision, facts_for(decision, state, self.profile), pending, narrations
                )
            for extra in self._extras(update, state, director):
                yield extra
            if event.t >= next_scoreboard:
                next_scoreboard = event.t + SCOREBOARD_EVERY
                yield self._overlay(OverlayType.SCOREBOARD, self._scoreboard(state, director))
            while not narrations.empty():
                yield self._narration(*narrations.get_nowait())

        if pending:
            await asyncio.wait(pending, timeout=NARRATION_GRACE)
        while not narrations.empty():
            yield self._narration(*narrations.get_nowait())
        yield self._overlay(OverlayType.SCOREBOARD, self._scoreboard(state, director))
        yield self._overlay(OverlayType.END, {})

    # -- events ----------------------------------------------------------------------

    def _cut(
        self,
        decision: Decision,
        facts: CutFacts,
        pending: set[asyncio.Task[None]],
        narrations: "asyncio.Queue[tuple[int, Narration]]",
    ) -> Overlay:
        decision_id = len(self.audit)
        reference = narrate_cut(facts, self.language)
        self.audit.append(
            {
                "decision": decision.model_dump(mode="json"),
                "facts": facts.model_dump(),
                "reference": reference,
            }
        )

        async def narrate() -> None:
            line = await self._commentary.narrate(
                facts, reference, self.language, self.profile.depth
            )
            self.audit[decision_id]["narration"] = line.model_dump(mode="json")
            await narrations.put((decision_id, line))

        task = asyncio.create_task(narrate())
        pending.add(task)
        task.add_done_callback(pending.discard)
        return self._overlay(
            OverlayType.CUT,
            {
                "decision_id": decision_id,
                "kind": decision.kind.value,
                "trigger": decision.trigger.value,
                "match_id": decision.match_id,
                "text": reference,
                "language": self.language.value,
                "facts": facts.model_dump(),
                "alternatives": [
                    {"match_id": a.match_id, "value": round(a.value, 3)}
                    for a in decision.alternatives
                ],
                "value": round(decision.chosen.value, 3),
            },
        )

    def _narration(self, decision_id: int, line: Narration) -> Overlay:
        return self._overlay(
            OverlayType.NARRATION,
            {
                "decision_id": decision_id,
                "text": line.text,
                "source": line.source.value,
                "drafts": line.drafts,
                "language": line.language.value,
            },
        )

    def _extras(self, update: Update, state: MatchdayState, director: Director) -> list[Overlay]:
        """Pitch actions for the match on air, plus table and fantasy changes."""
        event, extras = update.event, []
        if event.match_id == director.on_air and event.type in VISIBLE_ACTIONS:
            player = state.players[event.player_id].name if event.player_id else None
            extras.append(
                self._overlay(
                    OverlayType.ACTION,
                    {
                        "match_id": event.match_id,
                        "minute": event.minute,
                        "type": event.type.value,
                        "side": event.side.value if event.side else None,
                        "player": player,
                        "x": event.x,
                        "y": event.y,
                        "end_x": event.end_x,
                        "end_y": event.end_y,
                        "outcome": event.outcome,
                        "xg": event.xg,
                    },
                )
            )
        if event.type is EventType.GOAL:
            extras.append(self._overlay(OverlayType.TABLE, {"rows": self._table(state)}))
        if any(player in self.profile.fantasy_squad for player, _, _ in update.points):
            extras.append(self._overlay(OverlayType.FANTASY, self._fantasy(state)))
        return extras

    # -- payloads --------------------------------------------------------------------

    def _scoreboard(self, state: MatchdayState, director: Director) -> dict[str, Any]:
        lines = []
        for feed in state.feeds.values():
            meta = feed.match.meta
            lines.append(
                ScoreLine(
                    match_id=feed.match_id,
                    home=meta.home.name,
                    away=meta.away.name,
                    home_short=meta.home.short_name,
                    away_short=meta.away.short_name,
                    home_color=meta.home.color,
                    away_color=meta.away.color,
                    home_goals=feed.score[2],
                    away_goals=feed.score[3],
                    minute=feed.snapshot.minute if feed.snapshot else 1,
                    status=feed.status.value,
                    stakes=meta.stakes.value,
                    on_air=feed.match_id == director.on_air,
                ).model_dump()
            )
        return {"matches": lines}

    def _table(self, state: MatchdayState) -> list[dict[str, Any]]:
        start = state.table.positions()
        names = {t.id: t for m in state.matchday.matches for t in (m.meta.home, m.meta.away)}
        return [
            TableLine(
                position=i + 1,
                team_id=row.team_id,
                team=names[row.team_id].name,
                short=names[row.team_id].short_name,
                played=row.played,
                points=row.points,
                goal_difference=row.goal_difference,
                change=start[row.team_id] - (i + 1),
            ).model_dump()
            for i, row in enumerate(state.table.standings(state.scores()))
        ]

    def _fantasy(self, state: MatchdayState) -> dict[str, Any]:
        players = [
            {
                "name": state.players[p].name,
                "points": state.fantasy.points(p) * (2 if p == self.profile.captain_id else 1),
                "captain": p == self.profile.captain_id,
            }
            for p in self.profile.fantasy_squad
        ]
        return {"total": sum(p["points"] for p in players), "players": players}

    def _overlay(self, type_: OverlayType, data: dict[str, Any]) -> Overlay:
        self._seq += 1
        return Overlay(seq=self._seq, t=round(self._t, 2), type=type_, data=data)
