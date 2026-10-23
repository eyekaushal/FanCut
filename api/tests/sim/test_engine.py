import itertools
from collections import Counter

from fancut.sim import Match
from fancut.sim.archetypes import SPECS
from fancut.sim.clubs import TEAMS
from fancut.sim.engine import MatchSimulator
from fancut.sim.schema import Archetype, EventType, Side


def _simulate(seed: int) -> tuple:
    spec = SPECS[Archetype.BASELINE]
    return MatchSimulator("m", TEAMS["ashvale"], TEAMS["fenwick"], spec, seed).run()


def test_same_seed_same_match() -> None:
    assert _simulate(7) == _simulate(7)
    assert _simulate(7) != _simulate(8)


def test_events_are_ordered_and_clocks_consistent(league: list[Match]) -> None:
    for match in league:
        events = match.events
        assert [e.seq for e in events] == list(range(len(events)))
        assert all(a.t <= b.t for a, b in itertools.pairwise(events))
        for e in events:
            if e.period == 1:
                assert e.clock == e.t
            else:
                assert e.clock >= 45 * 60
        assert [e.type for e in events].count(EventType.HALF_TIME) == 1
        assert events[-1].type is EventType.FULL_TIME


def test_every_goal_follows_a_scoring_shot_and_is_followed_by_a_kickoff(
    league: list[Match],
) -> None:
    for match in league:
        events = match.events
        for i, e in enumerate(events):
            if e.type is EventType.GOAL:
                shot = events[i - 1]
                assert shot.type is EventType.SHOT and shot.outcome is True
                assert shot.side is e.side and shot.player_id == e.player_id
                assert events[i + 1].type is EventType.KICKOFF
                assert events[i + 1].side is e.side.opponent


def test_final_score_matches_goal_events(league: list[Match]) -> None:
    for match in league:
        goals = Counter(e.side for e in match.events if e.type is EventType.GOAL)
        assert match.truth.final_score == (goals[Side.HOME], goals[Side.AWAY])


def test_sent_off_players_take_no_further_part(league: list[Match]) -> None:
    for match in league:
        sent_off: dict[str, float] = {}
        for e in match.events:
            if e.type is EventType.CARD and e.qualifiers.get("color") == "red":
                assert e.player_id is not None
                sent_off[e.player_id] = e.t
            elif e.player_id in sent_off:
                raise AssertionError(
                    f"{e.player_id} acted after a red card in {match.meta.match_id}"
                )


def test_at_most_three_substitutions_per_side(league: list[Match]) -> None:
    for match in league:
        subs = Counter(e.side for e in match.events if e.type is EventType.SUBSTITUTION)
        assert all(count <= 3 for count in subs.values())


def test_players_belong_to_the_side_they_play_for(league: list[Match]) -> None:
    for match in league:
        rosters = {
            Side.HOME: {p.id for p in match.meta.home.players},
            Side.AWAY: {p.id for p in match.meta.away.players},
        }
        for e in match.events:
            if e.player_id is not None:
                assert e.side is not None
                assert e.player_id in rosters[e.side]
