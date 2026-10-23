"""Synthetic league: fictional clubs, a seeded match simulator, drama archetypes and labels."""

from fancut.sim.league import build_league, generate_match
from fancut.sim.replay import Replayer
from fancut.sim.schema import Archetype, Event, EventType, Match, Side

__all__ = [
    "Archetype",
    "Event",
    "EventType",
    "Match",
    "Replayer",
    "Side",
    "build_league",
    "generate_match",
]
