"""Ground truth derived from a finished match's events.

Labels come from what actually happened (goals, cards, big chances), never from the
drama engine, so they can be used to evaluate it.

* A **decisive** moment is a goal that changes who is winning (draw -> lead, lead -> draw,
  or a lead swap). Its window is the three minutes before the goal: the span in which a
  good wake-up must fire to be early.
* A **dramatic** moment is any decisive moment, a red card, or a big chance (xG >= 0.3)
  missed while the game is within one goal after the hour mark.
* The **verdict** (watch / skim / skip) follows from the facts too, so an unplanned
  thriller is labelled "watch" whatever scenario it was generated for.

Windows are in elapsed seconds (``Event.t``); rules about "the 70th minute" use the
football clock (``Event.clock``).
"""

from collections.abc import Callable, Iterable, Sequence
from dataclasses import dataclass

from nightkeeper.sim.schema import Event, EventType, GroundTruth, Side, Verdict, Window

DECISIVE_LEAD_SECONDS = 180.0
BIG_CHANCE_XG = 0.3
LATE_MINUTE = 70


@dataclass(frozen=True)
class Summary:
    """Facts about a finished match that the archetype checks need."""

    final: tuple[int, int]
    at_half: tuple[int, int]
    at_70: tuple[int, int]
    total_xg: float
    red_card_minutes: tuple[float, ...]
    lead_changes: int
    late_lead_change: bool


def score_at(events: Iterable[Event], until: Callable[[Event], bool]) -> tuple[int, int]:
    """Score counting only goals for which ``until(goal)`` is true."""
    home = away = 0
    for e in events:
        if e.type is EventType.GOAL and until(e):
            if e.side is Side.HOME:
                home += 1
            else:
                away += 1
    return home, away


def summarize(events: Sequence[Event]) -> Summary:
    return Summary(
        final=score_at(events, _always),
        at_half=score_at(events, lambda e: e.period == 1),
        at_70=score_at(events, lambda e: e.clock <= 70 * 60),
        total_xg=sum(e.xg or 0.0 for e in events if e.type is EventType.SHOT),
        red_card_minutes=tuple(
            e.clock / 60.0
            for e in events
            if e.type is EventType.CARD and e.qualifiers.get("color") == "red"
        ),
        lead_changes=len(_decisive_goals(events)),
        late_lead_change=any(g.clock >= LATE_MINUTE * 60 for g in _decisive_goals(events)),
    )


def verdict(s: Summary) -> Verdict:
    """Is this match worth watching back? Rules a neutral pundit would sign off on."""
    decided_early = abs(s.at_half[0] - s.at_half[1]) >= 3 and abs(s.final[0] - s.final[1]) >= 2
    if decided_early and not s.late_lead_change:
        return Verdict.SKIP  # over by half-time, and it stayed over
    if (
        s.lead_changes >= 3
        or s.late_lead_change
        or (abs(s.final[0] - s.final[1]) <= 1 and s.total_xg >= 2.5)
        or (s.red_card_minutes and sum(s.final) >= 3)
    ):
        return Verdict.WATCH
    if abs(s.final[0] - s.final[1]) >= 3 or (sum(s.final) <= 1 and s.total_xg < 1.6):
        return Verdict.SKIP
    return Verdict.SKIM


def label(events: Sequence[Event]) -> GroundTruth:
    decisive = tuple(
        Window(
            start_t=max(0.0, goal.t - DECISIVE_LEAD_SECONDS),
            end_t=goal.t,
            reason=f"goal changes the result at {goal.minute}'",
        )
        for goal in _decisive_goals(events)
    )
    return GroundTruth(
        decisive_windows=decisive,
        dramatic_windows=tuple(sorted(decisive + _other_drama(events), key=lambda w: w.start_t)),
        verdict=verdict(summarize(events)),
        final_score=score_at(events, _always),
    )


def _always(event: Event) -> bool:
    return True


def _leader(home: int, away: int) -> int:
    return (home > away) - (home < away)


def _decisive_goals(events: Sequence[Event]) -> list[Event]:
    home = away = 0
    decisive = []
    for e in events:
        if e.type is not EventType.GOAL:
            continue
        before = _leader(home, away)
        if e.side is Side.HOME:
            home += 1
        else:
            away += 1
        if _leader(home, away) != before:
            decisive.append(e)
    return decisive


def _other_drama(events: Sequence[Event]) -> tuple[Window, ...]:
    windows = []
    home = away = 0
    for e in events:
        if e.type is EventType.GOAL:
            home, away = (home + 1, away) if e.side is Side.HOME else (home, away + 1)
        elif e.type is EventType.CARD and e.qualifiers.get("color") == "red":
            windows.append(Window(start_t=e.t, end_t=e.t, reason=f"red card at {e.minute}'"))
        elif (
            e.type is EventType.SHOT
            and not e.outcome
            and (e.xg or 0.0) >= BIG_CHANCE_XG
            and e.period == 2
            and e.clock >= 60 * 60
            and abs(home - away) <= 1
        ):
            windows.append(
                Window(
                    start_t=max(0.0, e.t - DECISIVE_LEAD_SECONDS),
                    end_t=e.t,
                    reason=f"big chance missed at {e.minute}'",
                )
            )
    return tuple(windows)
