"""One fan's live channel: plays the matchday and emits ``overlay.v1`` events.

Cuts go out the instant the Director decides, carrying the correct reference line.
The model-written line follows as a ``narration`` event when it is ready, so a slow or
failing model never delays the picture.

The fan can *focus*: lock the pitch to one match while the Director keeps deciding.
Cuts still go out (the fan sees where the Director would be), but the plays on the
pitch come from the focused match until the focus is released.
"""

import asyncio
from collections.abc import AsyncIterator
from typing import Any

from pydantic import BaseModel

from fancut.agents.commentary import Commentary, Narration
from fancut.agents.facts import CutFacts, Moment, facts_for
from fancut.agents.recap import RecapFacts, recap_facts
from fancut.agents.templates import narrate_cut, narrate_recap
from fancut.api.overlay import Overlay, OverlayType, ScoreLine, TableLine
from fancut.director.director import Decision, Director
from fancut.director.relevance import Relevance, relevance
from fancut.insights import PlayerLedger
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


class Ranked(BaseModel):
    """A match's relevance with the evidence behind it, so a cut can explain itself."""

    match_id: str
    value: float
    drama: float
    stake: float
    reasons: list[str]


class AuditEntry(BaseModel):
    """One Director decision as the audit trail records it: the evidence, the reference
    line, and (once written) the Narrator's line with every rejected draft's reason."""

    decision_id: int
    t: float
    minute: int
    kind: str
    trigger: str
    match_id: str
    previous_match_id: str | None
    chosen: Ranked
    alternatives: list[Ranked]
    moment: Moment | None
    facts: CutFacts
    reference: str
    narration: Narration | None = None


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
        self.audit: list[AuditEntry] = []
        self._matchday = matchday
        self._commentary = commentary
        self._speed = speed
        self._until = until_minute
        self._seq = 0
        self._t = 0.0
        self.focus: str | None = None
        self._focus_changed = False
        self._final: tuple[MatchdayState, Director] | None = None
        self._recap: tuple[RecapFacts, str, Narration] | None = None

    @property
    def ended(self) -> bool:
        return self._final is not None

    async def recap(self) -> tuple[RecapFacts, str, Narration]:
        """The fan's matchday in a few sentences; built once, at full time."""
        assert self._final is not None, "the matchday has not ended"
        if self._recap is None:
            state, director = self._final
            facts = recap_facts(self.profile, state, director)
            reference = narrate_recap(facts, self.language)
            line = await self._commentary.recap(facts, reference, self.language, self.profile.depth)
            self._recap = (facts, reference, line)
        return self._recap

    def set_focus(self, match_id: str | None) -> None:
        """Lock the pitch to ``match_id``, or release it with ``None``."""
        self.focus = match_id
        self._focus_changed = True

    async def overlays(self) -> AsyncIterator[Overlay]:
        state = MatchdayState(self._matchday)
        director = Director(self.profile)
        ledger = PlayerLedger(state.players)
        narrations: asyncio.Queue[tuple[int, Narration]] = asyncio.Queue()
        pending: set[asyncio.Task[None]] = set()
        next_scoreboard = 0.0

        events = list(self._matchday.events())
        async for event in Replayer(events, speed=self._speed).stream():
            if self._until is not None and event.minute > self._until:
                break
            self._t = event.t
            update = state.update(event)
            ledger.update(event)
            for decision in director.observe(update, state):
                yield self._cut(
                    decision, facts_for(decision, state, self.profile), pending, narrations
                )
            if self._focus_changed:
                self._focus_changed = False
                yield self._focus_overlay(state)
                yield self._players(state, ledger, director)
            for extra in self._extras(update, state, director):
                yield extra
            if event.t >= next_scoreboard:
                next_scoreboard = event.t + SCOREBOARD_EVERY
                yield self._overlay(OverlayType.SCOREBOARD, self._scoreboard(state, director))
                if self.focus is not None:  # the focused match's standing moves with the play
                    yield self._focus_overlay(state)
                yield self._players(state, ledger, director)
            while not narrations.empty():
                yield self._narration(*narrations.get_nowait())

        if pending:
            await asyncio.wait(pending, timeout=NARRATION_GRACE)
        while not narrations.empty():
            yield self._narration(*narrations.get_nowait())
        yield self._overlay(OverlayType.SCOREBOARD, self._scoreboard(state, director))
        self._final = (state, director)
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
        # Hinglish is read aloud as Hindi: a Hindi voice reading Latin-script Hindi, or an
        # English voice reading it, both stumble. The spoken line is the Hindi reference.
        voice_text = (
            narrate_cut(facts, Language.HINDI) if self.language is Language.HINGLISH else None
        )
        chosen = _ranked(decision.chosen)
        alternatives = [_ranked(a) for a in decision.alternatives]
        self.audit.append(
            AuditEntry(
                decision_id=decision_id,
                t=round(decision.t, 2),
                minute=facts.minute,
                kind=decision.kind.value,
                trigger=decision.trigger.value,
                match_id=decision.match_id,
                previous_match_id=decision.previous_match_id,
                chosen=chosen,
                alternatives=alternatives,
                moment=facts.moment,
                facts=facts,
                reference=reference,
            )
        )

        async def narrate() -> None:
            line = await self._commentary.narrate(
                facts, reference, self.language, self.profile.depth
            )
            self.audit[decision_id].narration = line
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
                "voice_text": voice_text,
                "facts": facts.model_dump(),
                "chosen": chosen.model_dump(),
                "alternatives": [a.model_dump() for a in alternatives],
                "value": round(decision.chosen.value, 3),
            },
        )

    def _players(self, state: MatchdayState, ledger: PlayerLedger, director: Director) -> Overlay:
        """Everyone on the pitch in the match shown, with their numbers so far."""
        shown = self.focus or director.on_air
        on_pitch = sorted(state.feeds[shown].on_pitch) if shown else []
        return self._overlay(
            OverlayType.PLAYERS,
            {"match_id": shown, "players": [ledger.stats(p).model_dump() for p in on_pitch]},
        )

    def _focus_overlay(self, state: MatchdayState) -> Overlay:
        """The focus and, while one is set, the Director's current ranking of that match."""
        ranking = None
        if self.focus is not None:
            ranking = _ranked(relevance(self.profile, state.feeds[self.focus], state)).model_dump()
        return self._overlay(OverlayType.FOCUS, {"match_id": self.focus, "ranking": ranking})

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
        """Pitch actions for the match shown, plus table and fantasy changes."""
        event, extras = update.event, []
        shown = self.focus or director.on_air
        if event.match_id == shown and event.type in VISIBLE_ACTIONS:
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


def _ranked(relevance: Relevance) -> Ranked:
    return Ranked(
        match_id=relevance.match_id,
        value=round(relevance.value, 3),
        drama=round(relevance.drama, 3),
        stake=round(relevance.stake, 3),
        reasons=list(relevance.reasons),
    )
