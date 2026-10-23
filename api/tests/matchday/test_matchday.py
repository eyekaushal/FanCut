import itertools
from collections import Counter

import pytest

from fancut.matchday.matchday import Matchday, _stakes
from fancut.matchday.state import MatchdayState, Status
from fancut.sim.schema import Archetype, EventType, Stakes


def test_every_club_plays_once_at_the_same_kickoff(matchday: Matchday) -> None:
    teams = [t for m in matchday.matches for t in (m.meta.home.id, m.meta.away.id)]
    assert len(matchday.matches) == 10
    assert len(set(teams)) == 20
    assert {m.meta.kickoff_utc for m in matchday.matches} == {matchday.kickoff_utc}


def test_merged_stream_is_complete_and_time_ordered(matchday: Matchday) -> None:
    events = list(matchday.events())
    assert len(events) == sum(len(m.events) for m in matchday.matches)
    assert all(a.t <= b.t for a, b in itertools.pairwise(events))


def test_scenarios_go_where_they_naturally_happen(matchday: Matchday) -> None:
    by_archetype = {m.meta.archetype: m for m in matchday.matches}
    gaps = {
        m.meta.match_id: abs(m.meta.home.strength - m.meta.away.strength) for m in matchday.matches
    }
    blowout = by_archetype[Archetype.EARLY_BLOWOUT].meta.match_id
    assert gaps[blowout] == max(gaps.values())
    if any(m.meta.stakes is Stakes.MID_TABLE for m in matchday.matches):
        assert by_archetype[Archetype.DEAD_RUBBER].meta.stakes is Stakes.MID_TABLE


@pytest.mark.parametrize(
    ("home", "away", "expected"),
    [
        (1, 12, Stakes.TITLE_RACE),
        (2, 19, Stakes.TITLE_RACE),  # title race outranks relegation
        (5, 11, Stakes.TOP_FOUR),
        (9, 18, Stakes.RELEGATION),
        (8, 12, Stakes.MID_TABLE),
    ],
)
def test_a_match_matters_as_much_as_its_most_urgent_team(
    home: int, away: int, expected: Stakes
) -> None:
    assert _stakes(home, away) is expected


def test_live_state_ends_with_the_real_results(matchday: Matchday) -> None:
    state = MatchdayState(matchday)
    for event in matchday.events():
        state.update(event)
    for match in matchday.matches:
        feed = state.feeds[match.meta.match_id]
        assert feed.status is Status.FULL_TIME
        assert (feed.score[2], feed.score[3]) == match.truth.final_score
        reds = Counter(
            e.side for e in match.events
            if e.type is EventType.CARD and e.qualifiers.get("color") == "red"
        )  # fmt: skip
        assert len(feed.on_pitch) == 22 - sum(reds.values())
