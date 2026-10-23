"""The league table, before the matchday and "as it stands" while it is played."""

from collections.abc import Mapping

from pydantic import BaseModel, ConfigDict

POINTS_FOR_WIN = 3
POINTS_FOR_DRAW = 1


class TableRow(BaseModel):
    model_config = ConfigDict(frozen=True)

    team_id: str
    played: int
    won: int
    drawn: int
    lost: int
    goals_for: int
    goals_against: int

    @property
    def points(self) -> int:
        return POINTS_FOR_WIN * self.won + POINTS_FOR_DRAW * self.drawn

    @property
    def goal_difference(self) -> int:
        return self.goals_for - self.goals_against

    def with_result(self, scored: int, conceded: int) -> "TableRow":
        return self.model_copy(
            update={
                "played": self.played + 1,
                "won": self.won + (scored > conceded),
                "drawn": self.drawn + (scored == conceded),
                "lost": self.lost + (scored < conceded),
                "goals_for": self.goals_for + scored,
                "goals_against": self.goals_against + conceded,
            }
        )


Score = tuple[str, str, int, int]  # home id, away id, home goals, away goals


class LeagueTable:
    """Immutable base table; live tables are derived by applying current scores."""

    def __init__(self, rows: Mapping[str, TableRow], names: Mapping[str, str]) -> None:
        self._rows = dict(rows)
        self._names = dict(names)

    def standings(self, scores: tuple[Score, ...] = ()) -> list[TableRow]:
        """Rows sorted by points, goal difference, goals scored, then name."""
        rows = dict(self._rows)
        for home, away, home_goals, away_goals in scores:
            rows[home] = rows[home].with_result(home_goals, away_goals)
            rows[away] = rows[away].with_result(away_goals, home_goals)
        return sorted(
            rows.values(),
            key=lambda r: (-r.points, -r.goal_difference, -r.goals_for, self._names[r.team_id]),
        )

    def positions(self, scores: tuple[Score, ...] = ()) -> dict[str, int]:
        return {row.team_id: i + 1 for i, row in enumerate(self.standings(scores))}
