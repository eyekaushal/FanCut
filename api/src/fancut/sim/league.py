"""Builds a reproducible league of labelled matches from a single seed."""

import random
from datetime import UTC, datetime, timedelta

from fancut.sim.archetypes import SPECS
from fancut.sim.clubs import TEAMS
from fancut.sim.engine import MatchSimulator
from fancut.sim.labels import label, summarize
from fancut.sim.schema import Archetype, Match, MatchMeta, Stakes, Team

MAX_ATTEMPTS = 2000  # a 0-0 thriller occurs in ~1% of simulations
FIRST_KICKOFF = datetime(2026, 10, 24, 19, 0, tzinfo=UTC)  # 00:30 IST: a real night match

# 30 matches: enough variety to evaluate the Director on every kind of game.
DEFAULT_MIX: dict[Archetype, int] = {
    Archetype.BASELINE: 8,
    Archetype.DEAD_RUBBER: 4,
    Archetype.GOALLESS_THRILLER: 3,
    Archetype.LATE_COMEBACK: 5,
    Archetype.RED_CARD_CHAOS: 3,
    Archetype.EARLY_BLOWOUT: 3,
    Archetype.END_TO_END: 4,
}


class ArchetypeNotReachedError(RuntimeError):
    pass


def generate_match(
    match_id: str,
    home: Team,
    away: Team,
    archetype: Archetype,
    seed: int,
    kickoff_utc: datetime = FIRST_KICKOFF,
    stakes: Stakes | None = None,
) -> Match:
    """Simulate until the match genuinely exhibits ``archetype``; deterministic for a seed.

    ``stakes`` comes from the league table when the match is part of a matchday;
    otherwise one typical of the archetype is drawn.
    """
    spec = SPECS[archetype]
    rng = random.Random(seed)
    typical = rng.choice(spec.stakes)
    stakes = stakes or typical
    for _ in range(MAX_ATTEMPTS):
        attempt_seed = rng.randrange(2**31)
        events = MatchSimulator(match_id, home, away, spec, attempt_seed).run()
        if spec.accepts(summarize(events)):
            meta = MatchMeta(
                match_id=match_id,
                seed=attempt_seed,
                kickoff_utc=kickoff_utc,
                home=home,
                away=away,
                stakes=stakes,
                archetype=archetype,
            )
            return Match(meta=meta, events=events, truth=label(events))
    raise ArchetypeNotReachedError(f"{archetype} not reached in {MAX_ATTEMPTS} attempts")


def build_league(seed: int = 2026, mix: dict[Archetype, int] | None = None) -> list[Match]:
    rng = random.Random(seed)
    archetypes = [a for a, count in (mix or DEFAULT_MIX).items() for _ in range(count)]
    rng.shuffle(archetypes)
    by_strength = sorted(TEAMS.values(), key=lambda t: t.strength, reverse=True)

    matches = []
    for index, archetype in enumerate(archetypes):
        if SPECS[archetype].wide_strength_gap:
            home, away = rng.choice(by_strength[:3]), rng.choice(by_strength[-3:])
        else:
            home, away = rng.sample(by_strength, 2)
        kickoff = FIRST_KICKOFF + timedelta(days=7 * (index // 5), hours=2 * (index % 5))
        matches.append(
            generate_match(
                f"m{index + 1:03d}", home, away, archetype, rng.randrange(2**31), kickoff
            )
        )
    return matches
