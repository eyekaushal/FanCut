from fancut.drama.signals import PlayWindow, threat
from fancut.sim.schema import Event, EventType, Side


def _event(seq: int, t: float, type_: EventType, side: Side, **kw: object) -> Event:
    return Event(match_id="t", seq=seq, t=t, clock=t, period=1, type=type_, side=side, **kw)  # type: ignore[arg-type]


def _pass(seq: int, t: float, side: Side, completed: bool, end_x: float = 50.0) -> Event:
    return _event(
        seq, t, EventType.PASS, side, outcome=completed, x=50.0, y=34.0, end_x=end_x, end_y=34.0
    )


def test_threat_counts_shots_and_dangerous_possession_only() -> None:
    assert threat(_event(0, 0, EventType.SHOT, Side.HOME, xg=0.31)) == 0.31
    assert threat(_pass(1, 0, Side.HOME, True, end_x=90.0)) > 0
    assert threat(_pass(2, 0, Side.AWAY, True, end_x=90.0)) == 0  # away attacks towards x = 0
    assert threat(_pass(3, 0, Side.HOME, False, end_x=90.0)) == 0


def test_window_forgets_play_older_than_five_minutes() -> None:
    window = PlayWindow()
    window.add(_event(0, 0, EventType.SHOT, Side.HOME, xg=0.4))
    assert window.pressure(Side.HOME) > 0
    window.add(_pass(1, 301, Side.AWAY, True))
    assert window.pressure(Side.HOME) == 0


def test_patient_passing_reads_as_control_and_turnovers_as_chaos() -> None:
    calm, chaos = PlayWindow(), PlayWindow()
    for i in range(60):
        calm.add(_pass(i, i * 5.0, Side.HOME, completed=True))
    for i in range(60):
        side = Side.HOME if i % 2 else Side.AWAY
        chaos.add(_event(2 * i, i * 5.0, EventType.POSSESSION_CHANGE, side))
        chaos.add(_pass(2 * i + 1, i * 5.0 + 1, side, completed=i % 3 == 0))
    assert calm.control() > 0.5
    assert chaos.control() < -0.5
    assert calm.dominant_side() is Side.HOME
    assert chaos.dominant_side() is None
