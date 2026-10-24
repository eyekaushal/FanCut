from fancut.insights import PlayerLedger, pass_difficulty
from fancut.sim import Match
from fancut.sim.schema import Event, EventType, Side


def _event(type_: EventType, t: float, **kw: object) -> Event:
    base: dict[str, object] = {
        "match_id": "m1", "seq": int(t * 10), "t": t, "clock": t, "period": 1,
        "type": type_, "side": Side.HOME, "player_id": "p1",
    }  # fmt: skip
    return Event(**{**base, **kw})  # type: ignore[arg-type]


def test_pass_difficulty_rewards_length_forward_play_and_the_final_third() -> None:
    square = _event(EventType.PASS, 1, x=50, y=30, end_x=50, end_y=36)
    long_forward = _event(EventType.PASS, 1, x=30, y=34, end_x=75, end_y=34)
    backwards = _event(EventType.PASS, 1, x=50, y=34, end_x=30, end_y=34)
    assert pass_difficulty(square) < 0.1
    assert pass_difficulty(long_forward) == 1.0
    assert pass_difficulty(backwards) < pass_difficulty(long_forward)
    # The away side attacks the other way, so the same coordinates mean a backward ball.
    away = _event(EventType.PASS, 1, side=Side.AWAY, x=30, y=34, end_x=75, end_y=34)
    assert pass_difficulty(away) < pass_difficulty(long_forward)


def test_the_ledger_times_a_carry_by_the_next_event(league: list[Match]) -> None:
    players = {p.id: p for t in (league[0].meta.home, league[0].meta.away) for p in t.players}
    p1 = league[0].meta.home.players[5].id
    ledger = PlayerLedger({**players, "p1": players[p1]})
    ledger.update(_event(EventType.CARRY, 10.0, x=20, y=34, end_x=44, end_y=34))  # 24 m
    ledger.update(_event(EventType.PASS, 13.0, x=44, y=34, end_x=60, end_y=40, outcome=True))
    ledger.update(_event(EventType.TACKLE, 13.5, player_id="p1"))
    stats = ledger.stats("p1")
    assert stats.carries == 1 and stats.distance_carried_m == 24.0
    assert stats.top_speed_mps == 8.0 and stats.bursts == 1  # 24 m in 3 s
    assert stats.passes == 1 and stats.passes_completed == 1 and stats.pass_accuracy == 1.0
    assert stats.fastest_pass_mps > 30  # 17 m in half a second: an artefact, so capped out
    assert stats.tackles == 1


def test_a_whole_match_produces_plausible_numbers(league: list[Match]) -> None:
    match = league[0]
    players = {p.id: p for t in (match.meta.home, match.meta.away) for p in t.players}
    ledger = PlayerLedger(players)
    for event in match.events:
        ledger.update(event)
    seen = [ledger.stats(p) for p in players if ledger.stats(p).passes]
    assert len(seen) >= 20
    for s in seen:
        assert s.pass_accuracy is not None and 0 <= s.pass_accuracy <= 1
        assert 0 <= s.pass_difficulty <= 1
        assert s.top_speed_mps <= 10.5
        assert s.fastest_pass_mps <= 35
    assert sum(s.goals for s in seen) == sum(match.truth.final_score)
    assert any(s.bursts for s in seen)
