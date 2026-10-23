"""One matchday: every club plays at the same kickoff, late in the season."""

import heapq
import random
from collections.abc import Iterator
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from fancut.matchday.table import LeagueTable, TableRow
from fancut.sim.clubs import TEAMS
from fancut.sim.league import FIRST_KICKOFF, generate_match
from fancut.sim.schema import Archetype, Event, Match, Stakes, Team

ROUNDS_PLAYED = 33  # five rounds left: title, top-four and relegation races are all alive
DRAWS_PER_GAME = 0.25

# Ten fixtures need ten scenarios; most matchdays are mostly ordinary.
MATCHDAY_MIX = (
    Archetype.LATE_COMEBACK,
    Archetype.END_TO_END,
    Archetype.GOALLESS_THRILLER,
    Archetype.RED_CARD_CHAOS,
    Archetype.EARLY_BLOWOUT,
    Archetype.DEAD_RUBBER,
    Archetype.BASELINE,
    Archetype.BASELINE,
    Archetype.BASELINE,
    Archetype.BASELINE,
)


class Matchday(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: str
    kickoff_utc: datetime
    table_before: tuple[TableRow, ...]
    matches: tuple[Match, ...]

    def table(self) -> LeagueTable:
        return LeagueTable({r.team_id: r for r in self.table_before}, team_names())

    def events(self) -> Iterator[Event]:
        """Every match's events in one stream, ordered by elapsed time."""
        order = {m.meta.match_id: i for i, m in enumerate(self.matches)}
        yield from heapq.merge(
            *(m.events for m in self.matches),
            key=lambda e: (e.t, order[e.match_id], e.seq),
        )

    def match(self, match_id: str) -> Match:
        return next(m for m in self.matches if m.meta.match_id == match_id)


def team_names() -> dict[str, str]:
    return {team.id: team.name for team in TEAMS.values()}


def build_matchday(seed: int = 34, kickoff_utc: datetime = FIRST_KICKOFF) -> Matchday:
    """A reproducible matchday: table, fixtures, stakes and ten simulated matches."""
    rng = random.Random(seed)
    table_before = _table_after_rounds(rng)
    positions = {row.team_id: i + 1 for i, row in enumerate(_sorted(table_before))}
    fixtures = _fixtures(rng)
    stakes = [_stakes(positions[home.id], positions[away.id]) for home, away in fixtures]
    scenarios = _assign_scenarios(rng, fixtures, stakes)

    matches = tuple(
        generate_match(
            match_id=f"md{seed}-{i + 1:02d}",
            home=home,
            away=away,
            archetype=scenarios[i],
            seed=rng.randrange(2**31),
            kickoff_utc=kickoff_utc,
            stakes=stakes[i],
        )
        for i, (home, away) in enumerate(fixtures)
    )
    return Matchday(
        id=f"md{seed}",
        kickoff_utc=kickoff_utc,
        table_before=tuple(table_before),
        matches=matches,
    )


def _table_after_rounds(rng: random.Random) -> list[TableRow]:
    rows = []
    for team in TEAMS.values():
        points_per_game = min(2.4, max(0.5, 1.37 + 2.2 * (team.strength - 1.0)))
        points = max(5, round(points_per_game * ROUNDS_PLAYED + rng.gauss(0, 4)))
        drawn = min(points, round(ROUNDS_PLAYED * DRAWS_PER_GAME + rng.gauss(0, 2)))
        won = min((points - drawn) // 3, ROUNDS_PLAYED - drawn)
        lost = ROUNDS_PLAYED - won - drawn
        goals_for = max(10, round(ROUNDS_PLAYED * 1.35 * team.strength**1.5 + rng.gauss(0, 5)))
        goals_against = max(10, round(ROUNDS_PLAYED * 1.35 / team.strength**1.5 + rng.gauss(0, 5)))
        rows.append(
            TableRow(
                team_id=team.id,
                played=ROUNDS_PLAYED,
                won=won,
                drawn=drawn,
                lost=lost,
                goals_for=goals_for,
                goals_against=goals_against,
            )
        )
    return rows


def _sorted(rows: list[TableRow]) -> list[TableRow]:
    names = team_names()
    return sorted(
        rows, key=lambda r: (-r.points, -r.goal_difference, -r.goals_for, names[r.team_id])
    )


def _fixtures(rng: random.Random) -> list[tuple[Team, Team]]:
    teams = list(TEAMS.values())
    rng.shuffle(teams)
    return [(teams[i], teams[i + 1]) for i in range(0, len(teams), 2)]


def _assign_scenarios(
    rng: random.Random, fixtures: list[tuple[Team, Team]], stakes: list[Stakes]
) -> list[Archetype]:
    """Each scenario goes where it naturally happens: the blowout to the most lopsided
    fixture, the 0-0 thriller to the most even one, the dead rubber to a fixture with
    nothing at stake. The other scenarios are shuffled across the rest."""
    slots: list[Archetype | None] = [None] * len(fixtures)
    gaps = [abs(home.strength - away.strength) for home, away in fixtures]
    slots[gaps.index(max(gaps))] = Archetype.EARLY_BLOWOUT
    # The pickiest scenario first: a dead rubber only makes sense where nothing is at stake.
    quiet = [i for i, s in enumerate(stakes) if s is Stakes.MID_TABLE and slots[i] is None]
    free = [i for i, slot in enumerate(slots) if slot is None]
    slots[rng.choice(quiet or free)] = Archetype.DEAD_RUBBER
    free = [i for i, slot in enumerate(slots) if slot is None]
    slots[min(free, key=gaps.__getitem__)] = Archetype.GOALLESS_THRILLER

    placed = (Archetype.EARLY_BLOWOUT, Archetype.GOALLESS_THRILLER, Archetype.DEAD_RUBBER)
    rest = [a for a in MATCHDAY_MIX if a not in placed]
    rng.shuffle(rest)
    return [slot if slot is not None else rest.pop() for slot in slots]


def _concern(position: int) -> Stakes:
    if position <= 3:
        return Stakes.TITLE_RACE
    if position <= 6:
        return Stakes.TOP_FOUR
    if position >= 16:
        return Stakes.RELEGATION
    return Stakes.MID_TABLE


_URGENCY = (Stakes.TITLE_RACE, Stakes.RELEGATION, Stakes.TOP_FOUR, Stakes.MID_TABLE)


def _stakes(home_position: int, away_position: int) -> Stakes:
    """A match matters as much as its more urgent team's race."""
    concerns = {_concern(home_position), _concern(away_position)}
    return next(s for s in _URGENCY if s in concerns)
