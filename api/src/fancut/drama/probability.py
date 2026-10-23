"""In-play outcome probabilities from a Poisson goal model.

Each side's remaining goals are Poisson with mean ``rate * minutes_left``. The outcome
probabilities follow by summing over all plausible remaining scorelines. This is the
model used by Flepp, Pawlowski & Richardson (2025) to measure suspense and surprise in
European football.
"""

import math
from typing import NamedTuple

MAX_GOALS = 10  # remaining goals beyond this have negligible probability
HOME_GOALS_PER_MATCH = 1.45
AWAY_GOALS_PER_MATCH = 1.25
STRENGTH_ELASTICITY = 1.2
REGULATION_MINUTES = 90.0


class Outcome(NamedTuple):
    home: float
    draw: float
    away: float


def pre_match_rates(home_strength: float, away_strength: float) -> tuple[float, float]:
    """Expected goals per minute for each side before kickoff."""
    ratio = home_strength / away_strength
    home = HOME_GOALS_PER_MATCH * ratio**STRENGTH_ELASTICITY
    away = AWAY_GOALS_PER_MATCH * ratio**-STRENGTH_ELASTICITY
    return home / REGULATION_MINUTES, away / REGULATION_MINUTES


def poisson(mean: float) -> list[float]:
    """P(0), P(1), ... P(MAX_GOALS) for a Poisson variable."""
    return [math.exp(-mean) * mean**k / math.factorial(k) for k in range(MAX_GOALS + 1)]


def outcome_probabilities(
    home_goals: int,
    away_goals: int,
    home_rate: float,
    away_rate: float,
    minutes_left: float,
) -> Outcome:
    """Probability of each final result given the score and per-minute scoring rates."""
    home_more = poisson(home_rate * max(0.0, minutes_left))
    away_more = poisson(away_rate * max(0.0, minutes_left))
    home = draw = away = 0.0
    for i, p_i in enumerate(home_more):
        for j, p_j in enumerate(away_more):
            p = p_i * p_j
            final_diff = (home_goals + i) - (away_goals + j)
            if final_diff > 0:
                home += p
            elif final_diff < 0:
                away += p
            else:
                draw += p
    total = home + draw + away
    return Outcome(home / total, draw / total, away / total)
