from nightkeeper.sim.labels import DECISIVE_LEAD_SECONDS, Summary, label, verdict
from nightkeeper.sim.schema import Event, EventType, Side, Verdict


def _event(
    seq: int, minute: float, type_: EventType, side: Side | None = None, **kw: object
) -> Event:
    t = minute * 60
    period = 1 if minute <= 45 else 2
    return Event(match_id="t", seq=seq, t=t, clock=t, period=period, type=type_, side=side, **kw)  # type: ignore[arg-type]


def _goal(seq: int, minute: float, side: Side) -> Event:
    return _event(seq, minute, EventType.GOAL, side)


def test_only_goals_that_change_the_leader_are_decisive() -> None:
    events = [
        _goal(0, 10, Side.HOME),  # 1-0: draw -> lead, decisive
        _goal(1, 30, Side.HOME),  # 2-0: extends the lead, not decisive
        _goal(2, 60, Side.AWAY),  # 2-1: not decisive
        _goal(3, 80, Side.AWAY),  # 2-2: equaliser, decisive
        _goal(4, 89, Side.AWAY),  # 2-3: lead swap, decisive
    ]
    truth = label(events)

    assert [w.end_t for w in truth.decisive_windows] == [600.0, 4800.0, 5340.0]
    assert truth.decisive_windows[1].start_t == 4800.0 - DECISIVE_LEAD_SECONDS
    assert truth.final_score == (2, 3)


def test_dramatic_windows_include_red_cards_and_late_big_misses_in_tight_games() -> None:
    events = [
        _event(0, 20, EventType.CARD, Side.AWAY, qualifiers={"color": "red"}),
        _event(1, 50, EventType.SHOT, Side.HOME, outcome=False, xg=0.5),  # before the hour
        _event(2, 75, EventType.SHOT, Side.HOME, outcome=False, xg=0.45),  # counts
        _event(3, 80, EventType.SHOT, Side.HOME, outcome=False, xg=0.1),  # too small
    ]
    reasons = [w.reason for w in label(events).dramatic_windows]

    assert reasons == ["red card at 21'", "big chance missed at 76'"]


def _summary(**overrides: object) -> Summary:
    base: dict[str, object] = {
        "final": (1, 0),
        "at_half": (0, 0),
        "at_70": (0, 0),
        "total_xg": 1.8,
        "red_card_minutes": (),
        "lead_changes": 1,
        "late_lead_change": False,
    }
    return Summary(**{**base, **overrides})  # type: ignore[arg-type]


def test_verdict_rules() -> None:
    assert verdict(_summary()) is Verdict.SKIM
    assert verdict(_summary(late_lead_change=True)) is Verdict.WATCH
    assert verdict(_summary(final=(0, 0), total_xg=2.9, lead_changes=0)) is Verdict.WATCH
    assert verdict(_summary(final=(0, 0), total_xg=0.9, lead_changes=0)) is Verdict.SKIP
    assert verdict(_summary(final=(4, 0), at_half=(3, 0))) is Verdict.SKIP
    # A three-goal comeback after half-time is the opposite of "decided early".
    assert (
        verdict(_summary(final=(3, 3), at_half=(3, 0), lead_changes=2, late_lead_change=True))
        is Verdict.WATCH
    )
