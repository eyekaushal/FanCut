import itertools
import statistics

import pytest

from fancut.drama import DramaEngine, DramaSnapshot
from fancut.sim import Match
from fancut.sim.schema import Archetype, EventType


@pytest.fixture(scope="module")
def timelines(league: list[Match]) -> dict[str, list[DramaSnapshot]]:
    return {m.meta.match_id: DramaEngine(m.meta).run(m.events) for m in league}


def test_a_snapshot_every_minute_and_at_every_key_moment(
    league: list[Match], timelines: dict[str, list[DramaSnapshot]]
) -> None:
    for match in league:
        snaps = timelines[match.meta.match_id]
        triggers = [s.trigger for s in snaps]
        goals = sum(e.type is EventType.GOAL for e in match.events)
        assert triggers.count("goal") == goals
        assert triggers.count("half_time") == 1
        assert triggers[-1] == "full_time"
        assert triggers.count("minute") >= 90


def test_snapshots_are_well_formed(timelines: dict[str, list[DramaSnapshot]]) -> None:
    for snaps in timelines.values():
        for s in snaps:
            assert sum(s.win_probability) == pytest.approx(1.0)
            assert 0.0 <= s.suspense <= 1.0
            assert -1.0 <= s.control <= 1.0
            assert all(0.0 <= p <= 1.0 for p in s.pressure)
        excitement = [s.excitement for s in snaps]
        assert all(a <= b for a, b in itertools.pairwise(excitement))


def test_final_snapshot_knows_the_result(
    league: list[Match], timelines: dict[str, list[DramaSnapshot]]
) -> None:
    for match in league:
        final = timelines[match.meta.match_id][-1]
        home, away = match.truth.final_score
        assert final.score == (home, away)
        expected = (home > away, home == away, home < away)
        assert tuple(p == 1.0 for p in final.win_probability) == expected


def test_suspense_rises_before_late_comeback_goals(
    league: list[Match], timelines: dict[str, list[DramaSnapshot]]
) -> None:
    for match in league:
        if match.meta.archetype is not Archetype.LATE_COMEBACK:
            continue
        minutes = [s for s in timelines[match.meta.match_id] if s.trigger == "minute"]
        equaliser = next(w.end_t for w in match.truth.decisive_windows if w.end_t >= 70 * 60)
        before = statistics.mean(s.suspense for s in minutes if equaliser - 600 <= s.t < equaliser)
        assert before > statistics.median(s.suspense for s in minutes), match.meta.match_id


def test_blowouts_are_the_least_exciting_and_end_to_end_games_the_most_chaotic(
    league: list[Match], timelines: dict[str, list[DramaSnapshot]]
) -> None:
    def mean_by_archetype(metric: str) -> dict[Archetype, float]:
        values: dict[Archetype, list[float]] = {}
        for match in league:
            snaps = timelines[match.meta.match_id]
            value = (
                snaps[-1].excitement
                if metric == "excitement"
                else statistics.mean(s.control for s in snaps)
            )
            values.setdefault(match.meta.archetype, []).append(value)
        return {a: statistics.mean(v) for a, v in values.items()}

    excitement = mean_by_archetype("excitement")
    control = mean_by_archetype("control")
    assert min(excitement, key=excitement.__getitem__) is Archetype.EARLY_BLOWOUT
    assert min(control, key=control.__getitem__) is Archetype.END_TO_END
