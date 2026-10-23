"""Synthetic league: fictional clubs, a seeded match simulator, drama archetypes and labels."""

from nightkeeper.sim.league import build_league, generate_match
from nightkeeper.sim.replay import Replayer
from nightkeeper.sim.schema import Archetype, Event, EventType, Match, Side

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
