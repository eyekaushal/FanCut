"""Live fantasy points, scored from match events with simple, familiar rules."""

from collections import defaultdict
from collections.abc import Mapping

from fancut.sim.schema import Event, EventType, Player, Position

APPEARANCE = 2
GOAL = {Position.GK: 6, Position.DF: 6, Position.MF: 5, Position.FW: 4}
ASSIST = 3
CLEAN_SHEET = {Position.GK: 4, Position.DF: 4, Position.MF: 1, Position.FW: 0}
YELLOW = -1
RED = -3
ASSIST_WINDOW_SECONDS = 15.0

PointsChange = tuple[str, int, str]  # player id, points, reason


class FantasyLedger:
    """Points per player so far. Clean sheets count provisionally while a match is live."""

    def __init__(self, players: Mapping[str, Player], team_of: Mapping[str, str]) -> None:
        self._players = players
        self._team_of = team_of
        self._points: dict[str, int] = defaultdict(int)
        self._conceded: dict[str, int] = defaultdict(int)  # by team id
        self._appeared: set[str] = set()
        self._last_pass: dict[str, Event] = {}  # last completed pass, by team id

    def appear(self, player_id: str) -> list[PointsChange]:
        if player_id in self._appeared:
            return []
        self._appeared.add(player_id)
        return [self._add(player_id, APPEARANCE, "appearance")]

    def update(self, event: Event, opponent_team_id: str) -> list[PointsChange]:
        """Apply one event from a match against ``opponent_team_id``; return point changes."""
        if event.player_id is None:
            return []
        team = self._team_of[event.player_id]
        if event.type is EventType.PASS and event.outcome:
            self._last_pass[team] = event
        elif event.type is EventType.SUBSTITUTION:
            return self.appear(event.player_id)
        elif event.type is EventType.GOAL:
            return self._goal(event, team, opponent_team_id)
        elif event.type is EventType.CARD:
            red = event.qualifiers.get("color") == "red"
            return [self._add(event.player_id, RED if red else YELLOW, "card")]
        return []

    def points(self, player_id: str) -> int:
        """Points so far, including a provisional clean sheet for players who appeared."""
        total = self._points[player_id]
        if player_id in self._appeared and self._conceded[self._team_of[player_id]] == 0:
            total += CLEAN_SHEET[self._players[player_id].position]
        return total

    def _goal(self, event: Event, team: str, opponent: str) -> list[PointsChange]:
        assert event.player_id is not None
        scorer = self._players[event.player_id]
        changes = [self._add(scorer.id, GOAL[scorer.position], "goal")]
        assist = self._last_pass.get(team)
        if (
            assist is not None
            and assist.player_id not in (None, scorer.id)
            and event.t - assist.t <= ASSIST_WINDOW_SECONDS
        ):
            assert assist.player_id is not None
            changes.append(self._add(assist.player_id, ASSIST, "assist"))
        self._conceded[opponent] += 1
        return changes

    def _add(self, player_id: str, points: int, reason: str) -> PointsChange:
        self._points[player_id] += points
        return player_id, points, reason
