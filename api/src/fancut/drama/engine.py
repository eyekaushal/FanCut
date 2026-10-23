"""Turns a live event stream into a minute-by-minute picture of how dramatic a match is."""

import math
from collections.abc import Iterable

from pydantic import BaseModel, ConfigDict

from fancut.drama.measures import surprise, suspense, total_variation
from fancut.drama.probability import Outcome, outcome_probabilities, pre_match_rates
from fancut.drama.signals import PlayWindow, ThreatRate
from fancut.sim.schema import Event, EventType, MatchMeta, Side

LEAGUE_THREAT_PER_MINUTE = 0.025  # average threat per side per minute in the synthetic league
FORM_RANGE = (0.5, 2.0)  # recent form can halve or double a side's normal scoring rate, no more
FORM_WEIGHT = 0.65  # how strongly recent form bends the pre-match scoring rate
RED_CARD_PENALTY = 0.75  # scoring-rate factor per man down
RED_CARD_BONUS = 1.25  # scoring-rate factor per man up
SUSPENSE_SCALE = 0.44  # raw suspense at the 99th percentile of the synthetic league maps to 1.0
FIRST_HALF_END = 47.0  # typical first half, stoppage included (minutes)
MATCH_END = 94.0  # typical full match, stoppage included (minutes)


class DramaSnapshot(BaseModel):
    """Everything the product needs to know about the match at one moment."""

    model_config = ConfigDict(frozen=True)

    match_id: str
    seq: int
    t: float
    clock: float
    period: int
    minute: int
    trigger: str  # "minute", "goal", "red_card", "half_time" or "full_time"
    score: tuple[int, int]
    win_probability: Outcome
    suspense: float  # 0-1, forward-looking: is something decisive about to happen?
    surprise: float  # how far beliefs moved since the previous snapshot
    excitement: float  # cumulative belief movement so far (total variation)
    control: float  # +1 control ... -1 chaos
    dominant_side: Side | None
    pressure: tuple[float, float]  # (home, away), 0-1
    momentum: float  # -1 away on top ... +1 home on top


class DramaEngine:
    """Feed it events in order; it emits a snapshot every minute and at key moments."""

    def __init__(self, meta: MatchMeta) -> None:
        self._match_id = meta.match_id
        home_rate, away_rate = pre_match_rates(meta.home.strength, meta.away.strength)
        self._prior = {Side.HOME: home_rate, Side.AWAY: away_rate}
        self._threat = ThreatRate({side: LEAGUE_THREAT_PER_MINUTE for side in Side})
        self._window = PlayWindow()
        self._goals = {Side.HOME: 0, Side.AWAY: 0}
        self._reds = {Side.HOME: 0, Side.AWAY: 0}
        self._belief: Outcome | None = None
        self._excitement = 0.0
        self._minute_key: tuple[int, int] | None = None
        self._last: Event | None = None

    def run(self, events: Iterable[Event]) -> list[DramaSnapshot]:
        return [snapshot for event in events for snapshot in self.update(event)]

    def update(self, event: Event) -> list[DramaSnapshot]:
        snapshots = self._close_elapsed_minutes(event)
        self._last = event
        self._window.add(event)
        self._threat.add(event)

        trigger = None
        if event.type is EventType.GOAL and event.side is not None:
            self._goals[event.side] += 1
            trigger = "goal"
        elif event.type is EventType.CARD and event.qualifiers.get("color") == "red":
            if event.side is not None:
                self._reds[event.side] += 1
            trigger = "red_card"
        elif event.type in (EventType.HALF_TIME, EventType.FULL_TIME):
            trigger = event.type.value
        if trigger is not None:
            snapshots.append(self._snapshot(trigger))
        return snapshots

    # -- internals -------------------------------------------------------------------

    def _close_elapsed_minutes(self, event: Event) -> list[DramaSnapshot]:
        key = (event.period, int(event.clock // 60))
        previous, self._minute_key = self._minute_key, key
        if previous is None or key == previous or self._last is None:
            return []
        minutes = key[1] - previous[1] if key[0] == previous[0] else 1
        for _ in range(max(1, minutes)):
            self._threat.close_minute()
        return [self._snapshot("minute")]

    def _live_rate(self, side: Side) -> float:
        low, high = FORM_RANGE
        form = min(high, max(low, self._threat.rate(side) / LEAGUE_THREAT_PER_MINUTE))
        rate = self._prior[side] * math.pow(form, FORM_WEIGHT)
        men_down = self._reds[side] - self._reds[side.opponent]
        factor = RED_CARD_PENALTY if men_down > 0 else RED_CARD_BONUS
        return rate * factor ** abs(men_down)

    def _minutes_left(self, event: Event) -> float:
        if event.type is EventType.FULL_TIME:
            return 0.0
        minute = event.clock / 60
        if event.period == 1:
            return max(0.0, FIRST_HALF_END - minute) + (MATCH_END - FIRST_HALF_END)
        return max(0.5, MATCH_END - minute)

    def _snapshot(self, trigger: str) -> DramaSnapshot:
        event = self._last
        assert event is not None, "snapshots need at least one event"
        home, away = self._goals[Side.HOME], self._goals[Side.AWAY]
        home_rate, away_rate = self._live_rate(Side.HOME), self._live_rate(Side.AWAY)
        left = self._minutes_left(event)

        belief = outcome_probabilities(home, away, home_rate, away_rate, left)
        moved = 0.0 if self._belief is None else surprise(self._belief, belief)
        if self._belief is not None:
            self._excitement += total_variation(self._belief, belief)
        self._belief = belief

        raw_suspense = suspense(home, away, home_rate, away_rate, left)
        pressure = (self._window.pressure(Side.HOME), self._window.pressure(Side.AWAY))
        return DramaSnapshot(
            match_id=self._match_id,
            seq=event.seq,
            t=event.t,
            clock=event.clock,
            period=event.period,
            minute=event.minute,
            trigger=trigger,
            score=(home, away),
            win_probability=belief,
            suspense=min(1.0, raw_suspense / SUSPENSE_SCALE),
            surprise=moved,
            excitement=self._excitement,
            control=self._window.control(),
            dominant_side=self._window.dominant_side(),
            pressure=pressure,
            momentum=pressure[0] - pressure[1],
        )
