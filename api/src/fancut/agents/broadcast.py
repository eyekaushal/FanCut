"""Plays a matchday for one fan and captures each decision's fact sheet as it happens."""

from dataclasses import dataclass

from fancut.agents.facts import CutFacts, facts_for
from fancut.director.director import Decision, Director
from fancut.matchday.matchday import Matchday
from fancut.matchday.state import MatchdayState
from fancut.profile import FanProfile


@dataclass(frozen=True)
class Beat:
    """One moment of a fan's channel: what the Director did and the facts behind it."""

    decision: Decision
    facts: CutFacts


def beats(matchday: Matchday, profile: FanProfile) -> list[Beat]:
    state = MatchdayState(matchday)
    director = Director(profile)
    found: list[Beat] = []
    for event in matchday.events():
        update = state.update(event)
        for decision in director.observe(update, state):
            found.append(Beat(decision, facts_for(decision, state, profile)))
    return found
