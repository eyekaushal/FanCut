"""A league of ordinary matches must look like real top-flight football."""

import statistics
from collections import Counter

import pytest

from nightkeeper.sim.archetypes import SPECS
from nightkeeper.sim.clubs import TEAMS
from nightkeeper.sim.engine import MatchSimulator
from nightkeeper.sim.schema import Archetype, EventType

MATCHES = 200


@pytest.fixture(scope="module")
def stats() -> dict[str, float]:
    teams = list(TEAMS.values())
    rows: list[dict[str, float]] = []
    for i in range(MATCHES):
        home, away = teams[i % 10], teams[(i * 3 + 1) % 10]
        if home.id == away.id:
            away = teams[(i + 5) % 10]
        events = MatchSimulator(f"c{i}", home, away, SPECS[Archetype.BASELINE], seed=i).run()
        counts = Counter(e.type for e in events)
        passes = [e for e in events if e.type is EventType.PASS]
        cards = [e.qualifiers["color"] for e in events if e.type is EventType.CARD]
        rows.append(
            {
                "goals": counts[EventType.GOAL],
                "shots": counts[EventType.SHOT],
                "xg": sum(e.xg or 0.0 for e in events if e.type is EventType.SHOT),
                "pass_accuracy": sum(bool(e.outcome) for e in passes) / len(passes),
                "fouls": counts[EventType.FOUL],
                "yellows": cards.count("yellow"),
                "reds": cards.count("red"),
                "corners": counts[EventType.CORNER],
                "goalless": counts[EventType.GOAL] == 0,
            }
        )
    return {key: statistics.mean(row[key] for row in rows) for key in rows[0]}


# Ranges bracket typical top-flight averages per match.
@pytest.mark.parametrize(
    ("metric", "low", "high"),
    [
        ("goals", 2.4, 3.1),
        ("shots", 22, 32),
        ("xg", 2.4, 3.2),
        ("pass_accuracy", 0.78, 0.88),
        ("fouls", 16, 25),
        ("yellows", 2.5, 4.5),
        ("reds", 0.0, 0.2),
        ("corners", 7, 12),
        ("goalless", 0.03, 0.12),
    ],
)
def test_baseline_matches_look_like_real_football(
    stats: dict[str, float], metric: str, low: float, high: float
) -> None:
    assert low <= stats[metric] <= high, f"{metric}={stats[metric]:.3f}"
