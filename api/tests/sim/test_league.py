from collections import Counter

from fancut.sim import Match, build_league
from fancut.sim.archetypes import SPECS
from fancut.sim.labels import summarize
from fancut.sim.league import DEFAULT_MIX
from fancut.sim.schema import Archetype, Verdict

EXPECTED_VERDICT = {
    Archetype.LATE_COMEBACK: Verdict.WATCH,
    Archetype.END_TO_END: Verdict.WATCH,
    Archetype.GOALLESS_THRILLER: Verdict.WATCH,
    Archetype.RED_CARD_CHAOS: Verdict.WATCH,
    Archetype.EARLY_BLOWOUT: Verdict.SKIP,
    Archetype.DEAD_RUBBER: Verdict.SKIP,
}


def test_league_has_the_requested_mix_and_unique_ids(league: list[Match]) -> None:
    assert Counter(m.meta.archetype for m in league) == Counter(DEFAULT_MIX)
    assert len({m.meta.match_id for m in league}) == len(league)
    assert all(m.meta.home.id != m.meta.away.id for m in league)


def test_every_match_really_exhibits_its_archetype(league: list[Match]) -> None:
    for match in league:
        assert SPECS[match.meta.archetype].accepts(summarize(match.events)), match.meta.match_id


def test_scenario_verdicts_agree_with_fact_based_labels(league: list[Match]) -> None:
    for match in league:
        expected = EXPECTED_VERDICT.get(match.meta.archetype)
        if expected is not None:
            assert match.truth.verdict is expected, match.meta.match_id


def test_league_is_reproducible_from_its_seed(league: list[Match]) -> None:
    small_mix = {Archetype.BASELINE: 2, Archetype.DEAD_RUBBER: 1}
    assert build_league(7, small_mix) == build_league(7, small_mix)
