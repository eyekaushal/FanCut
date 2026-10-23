"""The Director: decides, for one fan, which match is on air.

Pure code, no language model: every decision is deterministic and carries its evidence
(the chosen match's relevance and the best alternatives it beat).
"""

from enum import StrEnum

from pydantic import BaseModel, ConfigDict

from fancut.director.relevance import Relevance, relevance
from fancut.matchday.state import MatchdayState, MatchFeed, Update
from fancut.profile import FanProfile
from fancut.sim.schema import Event, EventType

DECISION_INTERVAL = 10.0  # seconds of play between routine re-rankings
MIN_DWELL = 45.0  # never cut away sooner than this, except for a must-show moment
HYSTERESIS = 0.15  # a rival match must be 15% more relevant to win the screen
ALTERNATIVES_KEPT = 3


class Kind(StrEnum):
    OPEN = "open"  # first pick of the matchday
    CUT = "cut"  # switch the live picture to another match
    REPLAY = "replay"  # show a moment the fan did not see live


class Trigger(StrEnum):
    START = "start"
    RELEVANCE = "relevance"  # another match became clearly more relevant
    MUST_SHOW = "must_show"  # something happened that this fan cannot miss
    OFF_AIR = "off_air"  # the match on air reached half-time or full time


class Decision(BaseModel):
    model_config = ConfigDict(frozen=True)

    kind: Kind
    trigger: Trigger
    t: float
    match_id: str
    previous_match_id: str | None
    chosen: Relevance
    alternatives: tuple[Relevance, ...]
    event: Event | None = None  # the moment behind a must-show cut or a replay


class Director:
    def __init__(self, profile: FanProfile) -> None:
        self.profile = profile
        self.on_air: str | None = None
        self._since = 0.0
        self._last_ranking = float("-inf")
        self.decisions: list[Decision] = []

    def observe(self, update: Update, state: MatchdayState) -> list[Decision]:
        event = update.event
        made: list[Decision] = []
        if self.is_must_show(event, update.feed):
            if update.feed.match_id != self.on_air:
                made.append(self._decide(Kind.REPLAY, Trigger.MUST_SHOW, update.feed, state, event))
                made.append(self._decide(Kind.CUT, Trigger.MUST_SHOW, update.feed, state, event))
        elif event.t - self._last_ranking >= DECISION_INTERVAL:
            self._last_ranking = event.t
            made.extend(self._rerank(event, state))
        self.decisions.extend(made)
        return made

    def _rerank(self, event: Event, state: MatchdayState) -> list[Decision]:
        ranked = self._ranked(state)
        best = ranked[0]
        best_feed = state.feeds[best.match_id]
        if self.on_air is None:
            return [self._decide(Kind.OPEN, Trigger.START, best_feed, state, at=event.t)]
        if best.match_id == self.on_air or best.value == 0.0:
            return []
        current = next(r for r in ranked if r.match_id == self.on_air)
        if current.value == 0.0:  # half-time or full time on the match we were showing
            return [self._decide(Kind.CUT, Trigger.OFF_AIR, best_feed, state, at=event.t)]
        dwelt = event.t - self._since >= MIN_DWELL
        if dwelt and best.value > current.value * (1 + HYSTERESIS):
            return [self._decide(Kind.CUT, Trigger.RELEVANCE, best_feed, state, at=event.t)]
        return []

    def is_must_show(self, event: Event, feed: MatchFeed) -> bool:
        """Goals and red cards involving the fan's club or players."""
        if event.type is EventType.GOAL:
            return self.profile.club_id in feed.team_ids or self._cares(event)
        if event.type is EventType.CARD and event.qualifiers.get("color") == "red":
            return self.profile.club_id in feed.team_ids or self._cares(event)
        return False

    def _cares(self, event: Event) -> bool:
        return event.player_id is not None and self.profile.cares_about_player(event.player_id)

    def _ranked(self, state: MatchdayState) -> list[Relevance]:
        scores = [relevance(self.profile, feed, state) for feed in state.feeds.values()]
        return sorted(scores, key=lambda r: (-r.value, r.match_id))

    def _decide(
        self,
        kind: Kind,
        trigger: Trigger,
        feed: MatchFeed,
        state: MatchdayState,
        event: Event | None = None,
        at: float | None = None,
    ) -> Decision:
        ranked = self._ranked(state)
        chosen = next(r for r in ranked if r.match_id == feed.match_id)
        alternatives = tuple(r for r in ranked if r.match_id != feed.match_id)[:ALTERNATIVES_KEPT]
        t = event.t if event is not None else (at or 0.0)
        decision = Decision(
            kind=kind,
            trigger=trigger,
            t=t,
            match_id=feed.match_id,
            previous_match_id=self.on_air,
            chosen=chosen,
            alternatives=alternatives,
            event=event,
        )
        if kind is not Kind.REPLAY:
            self.on_air = feed.match_id
            self._since = t
        return decision
