from fancut.matchday.fantasy import APPEARANCE, ASSIST, CLEAN_SHEET, GOAL, FantasyLedger
from fancut.sim.schema import Event, EventType, Player, Position, Side

PLAYERS = {
    "fw": Player(id="fw", name="Forward", number=9, position=Position.FW),
    "mf": Player(id="mf", name="Midfielder", number=8, position=Position.MF),
    "gk": Player(id="gk", name="Keeper", number=1, position=Position.GK),
}
TEAM_OF = {"fw": "home", "mf": "home", "gk": "away"}


def _event(seq: int, t: float, type_: EventType, player: str, **kw: object) -> Event:
    side = Side.HOME if TEAM_OF[player] == "home" else Side.AWAY
    return Event(
        match_id="m", seq=seq, t=t, clock=t, period=1, type=type_, side=side,
        player_id=player, **kw,  # type: ignore[arg-type]
    )  # fmt: skip


def _ledger() -> FantasyLedger:
    ledger = FantasyLedger(PLAYERS, TEAM_OF)
    for player in PLAYERS:
        ledger.appear(player)
    return ledger


def test_goal_and_assist_within_the_window() -> None:
    ledger = _ledger()
    ledger.update(_event(0, 100, EventType.PASS, "mf", outcome=True), "away")
    changes = ledger.update(_event(1, 108, EventType.GOAL, "fw"), "away")

    assert ("fw", GOAL[Position.FW], "goal") in changes
    assert ("mf", ASSIST, "assist") in changes


def test_no_assist_for_an_old_pass() -> None:
    ledger = _ledger()
    ledger.update(_event(0, 100, EventType.PASS, "mf", outcome=True), "away")
    changes = ledger.update(_event(1, 200, EventType.GOAL, "fw"), "away")
    assert [c[2] for c in changes] == ["goal"]


def test_clean_sheet_is_provisional_until_a_goal_is_conceded() -> None:
    ledger = _ledger()
    assert ledger.points("gk") == APPEARANCE + CLEAN_SHEET[Position.GK]
    ledger.update(_event(0, 50, EventType.GOAL, "fw"), "away")
    assert ledger.points("gk") == APPEARANCE


def test_cards_cost_points() -> None:
    ledger = _ledger()
    ledger.update(_event(0, 10, EventType.CARD, "mf", qualifiers={"color": "yellow"}), "away")
    ledger.update(_event(1, 20, EventType.CARD, "fw", qualifiers={"color": "red"}), "away")
    assert ledger.points("mf") == APPEARANCE + CLEAN_SHEET[Position.MF] - 1
    assert ledger.points("fw") == APPEARANCE - 3
