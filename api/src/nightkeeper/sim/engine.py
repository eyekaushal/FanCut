"""Possession-by-possession football simulator.

Internally each possession is played in the *attacking frame* of the team on the ball:
``u`` runs 0 -> 105 from its own goal to the opponent's, ``v`` runs 0 -> 68 across.
``_emit`` converts to absolute pitch coordinates. The model is deliberately simple:
a handful of probabilities, calibrated so a league of baseline matches looks like real
top-flight football (see ``tests/sim/test_calibration.py``).
"""

import math
import random
from collections.abc import Mapping

from nightkeeper.sim.archetypes import ArchetypeSpec
from nightkeeper.sim.schema import (
    PITCH_LENGTH,
    PITCH_WIDTH,
    Event,
    EventType,
    Player,
    Position,
    Qualifier,
    Side,
    Team,
)
from nightkeeper.sim.state import GameState

HALF_SECONDS = 45 * 60.0
CENTRE = (PITCH_LENGTH / 2, PITCH_WIDTH / 2)
GOAL_KICK = (5.5, PITCH_WIDTH / 2)
PENALTY_XG = 0.76
BOX_U = 88.0  # edge of the penalty area, in the attacking frame

# Per-action probabilities (tuned by the calibration test, not by hand-waving).
FOUL_RATE = 0.014
YELLOW_RATE = 0.17
RED_RATE = 0.0015
SHOT_RATE_IN_BOX = 0.07
SHOT_RATE_LONG_RANGE = 0.028
SAVE_RATE = 0.45
CORNER_AFTER_SAVE = 0.45
CORNER_AFTER_MISS = 0.3
HEADER_FROM_CORNER = 0.22
OFFSIDE_RATE = 0.02
INTERCEPT_RATE = 0.6
BOX_FOUL_FACTOR = 0.15  # defenders avoid fouling where it costs a penalty
BOX_CROWDING = 0.18  # extra chance of losing the ball in a packed box
BOOKED_CAUTION = 0.25  # booked players commit cardable fouls far less often

Weights = Mapping[Position, float]
_SHOOTERS: Weights = {Position.GK: 0, Position.DF: 1, Position.MF: 3, Position.FW: 6}
_DEFENDERS: Weights = {Position.GK: 0, Position.DF: 4, Position.MF: 3, Position.FW: 1}
_DEEP: Weights = {Position.GK: 1, Position.DF: 4, Position.MF: 3, Position.FW: 0.5}
_MIDFIELD: Weights = {Position.GK: 0, Position.DF: 2, Position.MF: 4, Position.FW: 2}
_HIGH: Weights = {Position.GK: 0, Position.DF: 1, Position.MF: 3, Position.FW: 4}


class MatchSimulator:
    """Plays one seeded match and returns its events. Same inputs, same match."""

    def __init__(
        self, match_id: str, home: Team, away: Team, spec: ArchetypeSpec, seed: int
    ) -> None:
        self._match_id = match_id
        self._teams = {Side.HOME: home, Side.AWAY: away}
        self._spec = spec
        self._rng = random.Random(seed)
        self._state = GameState()
        self._events: list[Event] = []
        self._favourite = Side.HOME if home.strength >= away.strength else Side.AWAY
        self._on_pitch = {side: list(team.starters) for side, team in self._teams.items()}
        self._bench = {side: list(team.bench) for side, team in self._teams.items()}
        self._booked: set[str] = set()
        self._sub_minutes = {
            side: sorted(self._rng.uniform(55, 85) for _ in range(3)) for side in Side
        }

    def run(self) -> tuple[Event, ...]:
        for period in (1, 2):
            self._play_half(period)
        return tuple(self._events)

    # -- halves and possessions ------------------------------------------------------

    def _play_half(self, period: int) -> None:
        state = self._state
        state.period = period
        state.clock = HALF_SECONDS * (period - 1)
        stoppage = self._rng.uniform(60, 180) if period == 1 else self._rng.uniform(180, 420)
        end_clock = state.clock + HALF_SECONDS + stoppage

        side = Side.HOME if period == 1 else Side.AWAY
        self._kickoff(side)
        u, v = CENTRE
        while state.clock < end_clock:
            self._make_due_substitutions()
            side, u, v = self._play_possession(side, u, v, end_clock)

        self._emit(EventType.HALF_TIME if period == 1 else EventType.FULL_TIME)

    def _play_possession(
        self, side: Side, u: float, v: float, end_clock: float
    ) -> tuple[Side, float, float]:
        """Play until the ball changes hands; return who has it next and where (their frame)."""
        self._emit(EventType.POSSESSION_CHANGE, side, u=u, v=v)
        defending = side.opponent
        while self._state.clock < end_clock:
            self._tick(self._rng.uniform(2.0, 5.0))
            pressured = self._rng.random() < 0.10 + 0.25 * u / PITCH_LENGTH
            if pressured:
                self._emit(
                    EventType.PRESSURE,
                    defending,
                    self._pick(defending, _DEFENDERS),
                    u,
                    v,
                    frame=side,
                )
            foul_rate = FOUL_RATE * (BOX_FOUL_FACTOR if u >= BOX_U else 1.0)
            if self._rng.random() < foul_rate:
                if self._foul(side, u, v):
                    return self._shot(side, 94.0, PITCH_WIDTH / 2, penalty=True)
                continue
            if self._wants_to_shoot(side, u):
                return self._shot(side, u, v)
            if self._rng.random() < 0.75:
                kept, u, v = self._pass(side, u, v, pressured)
            else:
                kept, u, v = self._carry(side, u, v, pressured)
            if not kept:
                return defending, PITCH_LENGTH - u, PITCH_WIDTH - v
        return defending, PITCH_LENGTH - u, PITCH_WIDTH - v

    # -- actions ---------------------------------------------------------------------

    def _wants_to_shoot(self, side: Side, u: float) -> bool:
        drive = self._intensity(side)
        if u >= BOX_U:
            return self._rng.random() < SHOT_RATE_IN_BOX * drive
        if u >= 72:
            return self._rng.random() < SHOT_RATE_LONG_RANGE * drive
        return False

    def _pass(self, side: Side, u: float, v: float, pressured: bool) -> tuple[bool, float, float]:
        """Return whether possession was kept, and where the ball ended up."""
        drive = self._intensity(side)
        du = self._rng.gauss(6.0 * drive**0.5, 9.0)
        dv = self._rng.gauss(0.0, 10.0)
        end_u, end_v = _clamp(u + du, v + dv)
        length = math.hypot(end_u - u, end_v - v)
        player = self._pick(side, _zone_weights(u))
        qualifiers: dict[str, Qualifier] = {
            "length_m": round(length, 1),
            "pressured": pressured,
            "speed_kmh": round(max(20.0, self._rng.gauss(55, 12)), 1),
        }

        if end_u > BOX_U and self._rng.random() < OFFSIDE_RATE:
            qualifiers["offside"] = True
            self._emit(
                EventType.PASS, side, player, u, v, end_u, end_v, outcome=False, q=qualifiers
            )
            self._emit(EventType.OFFSIDE, side, self._pick(side, _HIGH), end_u, end_v)
            return False, end_u, end_v

        team = self._teams[side]
        success = (
            0.89
            + 0.06 * (team.strength - 1.0)
            - 0.004 * max(0.0, length - 15.0)
            - 0.002 * max(0.0, du)
            - (0.08 if pressured else 0.0)
            - (BOX_CROWDING if u >= BOX_U else 0.0)
            - self._spec.chaos
        )
        completed = self._rng.random() < min(0.97, max(0.3, success))
        self._emit(
            EventType.PASS, side, player, u, v, end_u, end_v, outcome=completed, q=qualifiers
        )
        if not completed and self._rng.random() < INTERCEPT_RATE:
            defender = self._pick(side.opponent, _DEFENDERS)
            self._emit(EventType.INTERCEPTION, side.opponent, defender, end_u, end_v, frame=side)
        return completed, end_u, end_v

    def _carry(self, side: Side, u: float, v: float, pressured: bool) -> tuple[bool, float, float]:
        drive = self._intensity(side)
        end_u, end_v = _clamp(
            u + self._rng.uniform(2.0, 9.0) * drive**0.5, v + self._rng.gauss(0.0, 4.0)
        )
        player = self._pick(side, _zone_weights(u))
        speed = round(max(8.0, self._rng.gauss(22, 5)), 1)
        qualifiers: dict[str, Qualifier] = {"speed_kmh": speed, "sprint": speed >= 28}
        tackled = self._rng.random() < (
            0.07 + (0.06 if pressured else 0.0) + (BOX_CROWDING * 0.6 if u >= BOX_U else 0.0)
        )
        self._emit(
            EventType.CARRY, side, player, u, v, end_u, end_v, outcome=not tackled, q=qualifiers
        )
        if tackled:
            defender = self._pick(side.opponent, _DEFENDERS)
            self._emit(EventType.TACKLE, side.opponent, defender, u, v, frame=side)
            return False, u, v
        return True, end_u, end_v

    def _shot(
        self, side: Side, u: float, v: float, *, penalty: bool = False, header: bool = False
    ) -> tuple[Side, float, float]:
        shooter = self._pick(side, _SHOOTERS)
        if penalty:
            xg = PENALTY_XG
        else:
            distance = math.hypot(PITCH_LENGTH - u, PITCH_WIDTH / 2 - v)
            angle = abs(math.atan2(v - PITCH_WIDTH / 2, PITCH_LENGTH - u))
            quality = self._teams[side].strength ** 0.5 * (0.6 if header else 1.0)
            raw = 1.65 * math.exp(-0.17 * distance) * (0.35 + 0.65 * math.cos(angle)) * quality
            xg = min(0.95, max(0.01, raw))

        scored = self._rng.random() < xg
        target_v = PITCH_WIDTH / 2 + self._rng.uniform(-3.6, 3.6)
        qualifiers: dict[str, Qualifier] = {
            "speed_kmh": round(max(40.0, self._rng.gauss(92, 14)), 1),
            "penalty": penalty,
            "header": header,
        }
        self._emit(
            EventType.SHOT,
            side,
            shooter,
            u,
            v,
            PITCH_LENGTH,
            target_v,
            outcome=scored,
            xg=round(xg, 3),
            q=qualifiers,
        )
        if scored:
            self._emit(EventType.GOAL, side, shooter, PITCH_LENGTH, target_v)
            self._state.goals[side] += 1
            self._kickoff(side.opponent)
            return side.opponent, *CENTRE

        defending = side.opponent
        if self._rng.random() < SAVE_RATE:
            keeper = self._on_pitch[defending][0]
            self._emit(EventType.SAVE, defending, keeper, PITCH_LENGTH - 1, target_v, frame=side)
            if self._rng.random() < CORNER_AFTER_SAVE:
                return self._corner(side)
        elif self._rng.random() < CORNER_AFTER_MISS:
            return self._corner(side)
        return defending, *GOAL_KICK

    def _corner(self, side: Side) -> tuple[Side, float, float]:
        corner_v = self._rng.choice((0.5, PITCH_WIDTH - 0.5))
        self._emit(
            EventType.CORNER, side, self._pick(side, _MIDFIELD), PITCH_LENGTH - 0.5, corner_v
        )
        if self._rng.random() < HEADER_FROM_CORNER:
            u = self._rng.uniform(95.0, 101.0)
            v = PITCH_WIDTH / 2 + self._rng.uniform(-6.0, 6.0)
            return self._shot(side, u, v, header=True)
        return side.opponent, *GOAL_KICK

    def _foul(self, side: Side, u: float, v: float) -> bool:
        """Defender fouls the side in possession. Returns True if it is a penalty."""
        defending = side.opponent
        offender = self._pick(defending, _DEFENDERS)
        self._emit(EventType.FOUL, defending, offender, u, v, frame=side)
        self._maybe_card(defending, offender)

        penalty = u > PITCH_LENGTH - 16.5 and 13.84 < v < PITCH_WIDTH - 13.84
        self._emit(
            EventType.FREE_KICK, side, self._pick(side, _MIDFIELD), u, v, q={"penalty": penalty}
        )
        return penalty

    def _maybe_card(self, side: Side, player: Player) -> None:
        red_rate = RED_RATE * (self._spec.red_card_boost if self._state.minute < 65 else 1.0)
        yellow_rate = YELLOW_RATE * (BOOKED_CAUTION if player.id in self._booked else 1.0)
        roll = self._rng.random()
        if roll < red_rate:
            self._send_off(side, player, "violent conduct")
        elif roll < red_rate + yellow_rate:
            if player.id in self._booked:
                self._send_off(side, player, "second yellow")
            else:
                self._booked.add(player.id)
                self._emit(EventType.CARD, side, player, q={"color": "yellow"})

    def _send_off(self, side: Side, player: Player, reason: str) -> None:
        self._emit(EventType.CARD, side, player, q={"color": "red", "reason": reason})
        self._on_pitch[side].remove(player)
        self._state.red_cards[side] += 1

    def _kickoff(self, side: Side) -> None:
        self._emit(EventType.KICKOFF, side, self._pick(side, _HIGH), *CENTRE)

    def _make_due_substitutions(self) -> None:
        for side in Side:
            due = self._sub_minutes[side]
            while due and self._state.minute >= due[0] and self._state.period == 2:
                due.pop(0)
                outfield = [p for p in self._on_pitch[side] if p.position is not Position.GK]
                bench = [p for p in self._bench[side] if p.position is not Position.GK]
                if not outfield or not bench:
                    continue
                off, on = self._rng.choice(outfield), bench[0]
                self._bench[side].remove(on)
                self._on_pitch[side][self._on_pitch[side].index(off)] = on
                self._emit(EventType.SUBSTITUTION, side, on, q={"player_off": off.id})

    # -- helpers ---------------------------------------------------------------------

    def _intensity(self, side: Side) -> float:
        return self._spec.intensity(side, self._state, self._favourite)

    def _tick(self, seconds: float) -> None:
        self._state.t += seconds
        self._state.clock += seconds

    def _pick(self, side: Side, weights: Weights) -> Player:
        players = self._on_pitch[side]
        star = self._teams[side].star_player_id
        scores = [weights[p.position] * (2.5 if p.id == star else 1.0) for p in players]
        if not any(scores):
            return self._rng.choice(players)
        return self._rng.choices(players, weights=scores)[0]

    def _emit(
        self,
        type_: EventType,
        side: Side | None = None,
        player: Player | None = None,
        u: float | None = None,
        v: float | None = None,
        end_u: float | None = None,
        end_v: float | None = None,
        *,
        outcome: bool | None = None,
        xg: float | None = None,
        q: dict[str, Qualifier] | None = None,
        frame: Side | None = None,
    ) -> None:
        """Record an event. Positions are given in the attacking frame of ``frame``
        (default: ``side``) and stored as absolute pitch coordinates."""
        frame = frame or side
        x, y = _to_absolute(frame, u, v)
        end_x, end_y = _to_absolute(frame, end_u, end_v)
        state = self._state
        self._events.append(
            Event(
                match_id=self._match_id,
                seq=len(self._events),
                t=round(state.t, 2),
                clock=round(state.clock, 2),
                period=state.period,
                type=type_,
                side=side,
                player_id=player.id if player else None,
                x=x,
                y=y,
                end_x=end_x,
                end_y=end_y,
                outcome=outcome,
                xg=xg,
                qualifiers=q or {},
            )
        )


def _zone_weights(u: float) -> Weights:
    if u < 35:
        return _DEEP
    return _HIGH if u > 70 else _MIDFIELD


def _clamp(u: float, v: float) -> tuple[float, float]:
    return min(PITCH_LENGTH - 0.5, max(0.5, u)), min(PITCH_WIDTH - 0.5, max(0.5, v))


def _to_absolute(
    frame: Side | None, u: float | None, v: float | None
) -> tuple[float | None, float | None]:
    if u is None or v is None:
        return None, None
    if frame is Side.AWAY:
        return round(PITCH_LENGTH - u, 2), round(PITCH_WIDTH - v, 2)
    return round(u, 2), round(v, 2)
