"""Per-player numbers from the event stream: passing, carrying, shooting, speed.

Pure code over ``event.v1``. Distances come from the pitch coordinates (metres);
speeds from the time until the next event in the same match, which is when the ball
or the player arrived. Pass difficulty is a rating of the attempt, not the outcome.
"""

import math
from collections import defaultdict
from collections.abc import Mapping
from dataclasses import dataclass, field

from pydantic import BaseModel

from fancut.sim.schema import PITCH_LENGTH, Event, EventType, Player, Side

# A carry in the league's fastest 1% (measured: p99 4.7 m/s, max 6.2 m/s). An event's
# duration spans a whole phase of play, so these are bursts, not sprints at 25 km/h.
BURST_MPS = 4.5
MAX_TIMED_GAP = 8.0  # seconds; a longer gap means the next event is not the arrival
MAX_PLAYER_MPS = 10.5  # anything faster is a timing artefact, not a player
MAX_BALL_MPS = 35.0


def pass_difficulty(event: Event) -> float:
    """0 (a square five-yard ball) to 1 (a long ball into the final third)."""
    if event.x is None or event.y is None or event.end_x is None or event.end_y is None:
        return 0.0
    length = math.hypot(event.end_x - event.x, event.end_y - event.y)
    towards = 1.0 if event.side is Side.HOME else -1.0
    forward = (event.end_x - event.x) * towards
    final_third = (
        event.end_x if towards > 0 else PITCH_LENGTH - event.end_x
    ) >= PITCH_LENGTH * 2 / 3
    score = 0.45 * min(1.0, length / 40) + 0.35 * max(0.0, min(1.0, forward / 30))
    score += 0.2 if final_third else 0.0
    return round(min(1.0, score), 3)


class PlayerStats(BaseModel):
    player_id: str
    name: str
    passes: int = 0
    passes_completed: int = 0
    pass_difficulty: float = 0.0  # mean rating of the passes attempted
    longest_pass_m: float = 0.0
    fastest_pass_mps: float = 0.0
    carries: int = 0
    distance_carried_m: float = 0.0
    top_speed_mps: float = 0.0
    bursts: int = 0
    shots: int = 0
    goals: int = 0
    xg: float = 0.0
    fastest_shot_mps: float = 0.0
    tackles: int = 0
    interceptions: int = 0

    @property
    def pass_accuracy(self) -> float | None:
        return self.passes_completed / self.passes if self.passes else None


@dataclass
class _Running:
    stats: PlayerStats
    difficulty_total: float = 0.0


@dataclass
class _Pending:
    """A pass, carry or shot whose arrival time is the next event in its match."""

    event: Event
    length: float


@dataclass
class PlayerLedger:
    players: Mapping[str, Player]
    _running: dict[str, _Running] = field(default_factory=dict)
    _pending: dict[str, _Pending] = field(default_factory=dict)  # by match id
    _appeared: dict[str, set[str]] = field(default_factory=lambda: defaultdict(set))

    def update(self, event: Event) -> None:
        self._time_pending(event)
        if event.player_id is None:
            return
        running = self._for(event.player_id)
        stats = running.stats
        length = _length(event)

        if event.type is EventType.PASS:
            stats.passes += 1
            stats.passes_completed += 1 if event.outcome else 0
            running.difficulty_total += pass_difficulty(event)
            stats.pass_difficulty = round(running.difficulty_total / stats.passes, 3)
            stats.longest_pass_m = round(max(stats.longest_pass_m, length), 1)
            self._pending[event.match_id] = _Pending(event, length)
        elif event.type is EventType.CARRY:
            stats.carries += 1
            stats.distance_carried_m = round(stats.distance_carried_m + length, 1)
            self._pending[event.match_id] = _Pending(event, length)
        elif event.type in (EventType.SHOT, EventType.GOAL):
            stats.shots += 1
            stats.goals += 1 if event.type is EventType.GOAL else 0
            stats.xg = round(stats.xg + (event.xg or 0.0), 3)
            self._pending[event.match_id] = _Pending(event, length)
        elif event.type is EventType.TACKLE:
            stats.tackles += 1
        elif event.type is EventType.INTERCEPTION:
            stats.interceptions += 1

    def stats(self, player_id: str) -> PlayerStats:
        return self._for(player_id).stats

    def _for(self, player_id: str) -> _Running:
        if player_id not in self._running:
            self._running[player_id] = _Running(
                PlayerStats(player_id=player_id, name=self.players[player_id].name)
            )
        return self._running[player_id]

    def _time_pending(self, event: Event) -> None:
        """The event after a pass, carry or shot gives its duration, hence its speed."""
        pending = self._pending.pop(event.match_id, None)
        if pending is None or pending.event.player_id is None:
            return
        gap = event.t - pending.event.t
        if gap <= 0 or gap > MAX_TIMED_GAP or pending.length <= 0:
            return
        speed = pending.length / gap
        stats = self._for(pending.event.player_id).stats
        kind = pending.event.type
        if kind is EventType.CARRY and speed <= MAX_PLAYER_MPS:
            stats.top_speed_mps = round(max(stats.top_speed_mps, speed), 2)
            if speed >= BURST_MPS:
                stats.bursts += 1
        elif kind is EventType.PASS and speed <= MAX_BALL_MPS:
            stats.fastest_pass_mps = round(max(stats.fastest_pass_mps, speed), 2)
        elif kind in (EventType.SHOT, EventType.GOAL) and speed <= MAX_BALL_MPS:
            stats.fastest_shot_mps = round(max(stats.fastest_shot_mps, speed), 2)


def _length(event: Event) -> float:
    if event.x is None or event.y is None or event.end_x is None or event.end_y is None:
        return 0.0
    return math.hypot(event.end_x - event.x, event.end_y - event.y)
