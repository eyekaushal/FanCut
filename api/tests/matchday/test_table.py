from fancut.matchday.table import LeagueTable, TableRow


def _row(team: str, won: int, drawn: int, goals_for: int, goals_against: int) -> TableRow:
    return TableRow(
        team_id=team, played=won + drawn, won=won, drawn=drawn, lost=0,
        goals_for=goals_for, goals_against=goals_against,
    )  # fmt: skip


NAMES = {"a": "Alpha", "b": "Bravo", "c": "Charlie"}


def test_results_update_points_and_goals() -> None:
    row = _row("a", won=1, drawn=0, goals_for=2, goals_against=0).with_result(1, 1)
    assert (row.played, row.drawn, row.points, row.goal_difference) == (2, 1, 4, 2)


def test_standings_break_ties_on_goal_difference_then_goals_then_name() -> None:
    table = LeagueTable(
        {
            "a": _row("a", 2, 0, 3, 1),  # 6 pts, +2
            "b": _row("b", 2, 0, 5, 2),  # 6 pts, +3
            "c": _row("c", 2, 0, 4, 1),  # 6 pts, +3, fewer goals than b
        },
        NAMES,
    )
    assert [r.team_id for r in table.standings()] == ["b", "c", "a"]


def test_live_scores_move_teams_as_it_stands() -> None:
    table = LeagueTable(
        {"a": _row("a", 3, 0, 6, 2), "b": _row("b", 2, 1, 6, 2), "c": _row("c", 0, 0, 0, 0)},
        NAMES,
    )
    assert table.positions()["b"] == 2
    assert table.positions((("b", "c", 1, 0),))["b"] == 1  # b wins: 10 pts vs a's 9
