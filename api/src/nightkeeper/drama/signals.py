"""Rolling signals over recent play: threat, pressure, momentum, control vs chaos."""

import math
from collections import deque

from nightkeeper.sim.schema import PITCH_LENGTH, Event, EventType, Side

WINDOW_SECONDS = 5 * 60.0
THREAT_HALF_LIFE_MINUTES = 5.0
PRESSURE_SCALE = 0.35  # threat (in xG) over the window that counts as full pressure
FINAL_THIRD = 70.0

# League baselines (from the calibrated simulator) that define "normal" play.
BASELINE_COMPLETION = 0.82
BASELINE_TURNOVERS_PER_MINUTE = 2.7


def attacking_u(side: Side, x: float) -> float:
    """Distance along the pitch towards ``side``'s target goal."""
    return x if side is Side.HOME else PITCH_LENGTH - x


def threat(event: Event) -> float:
    """How much an event moves its side towards a goal, in expected-goals units."""
    if event.side is None:
        return 0.0
    if event.type is EventType.SHOT:
        return event.xg or 0.0
    if event.type is EventType.CORNER:
        return 0.025
    if event.type is EventType.FREE_KICK and event.x is not None:
        return 0.015 if attacking_u(event.side, event.x) > FINAL_THIRD else 0.0
    if (
        event.type in (EventType.PASS, EventType.CARRY)
        and event.outcome
        and event.end_x is not None
    ):
        return 0.004 if attacking_u(event.side, event.end_x) > FINAL_THIRD else 0.0
    return 0.0


class ThreatRate:
    """Exponentially weighted threat per minute for each side, folded once a minute."""

    def __init__(self, prior: dict[Side, float]) -> None:
        self._rate = dict(prior)
        self._this_minute = {Side.HOME: 0.0, Side.AWAY: 0.0}
        self._decay = 0.5 ** (1 / THREAT_HALF_LIFE_MINUTES)

    def add(self, event: Event) -> None:
        if event.side is not None:
            self._this_minute[event.side] += threat(event)

    def close_minute(self) -> None:
        for side in Side:
            self._rate[side] = (
                self._decay * self._rate[side] + (1 - self._decay) * self._this_minute[side]
            )
            self._this_minute[side] = 0.0

    def rate(self, side: Side) -> float:
        return self._rate[side]


class PlayWindow:
    """The last five minutes of play, for pressure and control."""

    def __init__(self) -> None:
        self._events: deque[Event] = deque()

    def add(self, event: Event) -> None:
        self._events.append(event)
        while self._events and event.t - self._events[0].t > WINDOW_SECONDS:
            self._events.popleft()

    def pressure(self, side: Side) -> float:
        """0 (no threat) to 1 (sustained, dangerous pressure)."""
        total = sum(threat(e) for e in self._events if e.side is side)
        return min(1.0, total / PRESSURE_SCALE)

    def momentum(self) -> float:
        """-1 (away on top) to +1 (home on top)."""
        return self.pressure(Side.HOME) - self.pressure(Side.AWAY)

    def control(self) -> float:
        """+1 calm, patient possession play; -1 chaos: turnovers and loose passing."""
        passes = [e for e in self._events if e.type is EventType.PASS]
        minutes = self._span_minutes()
        if len(passes) < 5 or minutes <= 0:
            return 0.0
        completion = sum(bool(e.outcome) for e in passes) / len(passes)
        turnovers = sum(e.type is EventType.POSSESSION_CHANGE for e in self._events) / minutes
        score = 0.6 * (completion - BASELINE_COMPLETION) / 0.06
        score -= 0.6 * (turnovers - BASELINE_TURNOVERS_PER_MINUTE) / 1.0
        return math.tanh(score)

    def dominant_side(self) -> Side | None:
        """The side with at least 60% of recent passes, if any."""
        passes = [e.side for e in self._events if e.type is EventType.PASS]
        if not passes:
            return None
        home_share = passes.count(Side.HOME) / len(passes)
        if home_share >= 0.6:
            return Side.HOME
        if home_share <= 0.4:
            return Side.AWAY
        return None

    def _span_minutes(self) -> float:
        if len(self._events) < 2:
            return 0.0
        return (self._events[-1].t - self._events[0].t) / 60.0
