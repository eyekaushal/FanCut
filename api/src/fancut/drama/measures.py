"""Suspense, surprise and excitement over beliefs about the final result.

* **Suspense** (Ely, Frankel & Kamenica, 2015) looks *forward*: how much the outcome
  probabilities are expected to move over the next few minutes. High suspense means
  something decisive may be about to happen. That is the signal to wake a fan.
* **Surprise** looks *back*: how far beliefs actually moved since the last update.
* **Excitement** (Vecer, Ichiba & Laudanovic, 2007) accumulates movement: the total
  variation of the outcome-probability path over the match so far.
"""

import math

from fancut.drama.probability import Outcome, outcome_probabilities

SUSPENSE_HORIZON_MINUTES = 5.0


def distance(a: Outcome, b: Outcome) -> float:
    """Euclidean distance between two outcome distributions."""
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b, strict=True)))


def total_variation(a: Outcome, b: Outcome) -> float:
    """Total variation distance: half the L1 distance, in [0, 1]."""
    return sum(abs(x - y) for x, y in zip(a, b, strict=True)) / 2


def surprise(previous: Outcome, current: Outcome) -> float:
    return distance(previous, current)


def suspense(
    home_goals: int,
    away_goals: int,
    home_rate: float,
    away_rate: float,
    minutes_left: float,
) -> float:
    """Expected belief movement over the next ``SUSPENSE_HORIZON_MINUTES``.

    The near future is reduced to its four plausible branches: no goal, a home goal,
    an away goal, or one each. Suspense is the root of the probability-weighted squared
    distance between today's beliefs and the beliefs in each branch.
    """
    horizon = min(SUSPENSE_HORIZON_MINUTES, max(0.0, minutes_left))
    after = max(0.0, minutes_left - horizon)
    now = outcome_probabilities(home_goals, away_goals, home_rate, away_rate, minutes_left)

    p_home = 1 - math.exp(-home_rate * horizon)
    p_away = 1 - math.exp(-away_rate * horizon)
    branches = (
        ((1 - p_home) * (1 - p_away), 0, 0),
        (p_home * (1 - p_away), 1, 0),
        ((1 - p_home) * p_away, 0, 1),
        (p_home * p_away, 1, 1),
    )
    expected = 0.0
    for weight, h, a in branches:
        later = outcome_probabilities(home_goals + h, away_goals + a, home_rate, away_rate, after)
        expected += weight * distance(now, later) ** 2
    return math.sqrt(expected)
