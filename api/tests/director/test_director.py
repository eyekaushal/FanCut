import pytest

from fancut.demo import ARJUN, MAYA
from fancut.director.director import Kind, Trigger
from fancut.director.evaluate import Channel, distinctness, report, run_channel
from fancut.director.relevance import relevance
from fancut.matchday.matchday import Matchday
from fancut.matchday.state import MatchdayState
from fancut.profile import FanProfile


@pytest.fixture(scope="module")
def channels(matchday: Matchday) -> dict[str, Channel]:
    return {p.name: run_channel(matchday, p) for p in (ARJUN, MAYA)}


def test_a_fan_never_misses_their_own_moments(
    matchday: Matchday, channels: dict[str, Channel]
) -> None:
    result = report(matchday, channels["Arjun"])
    assert result.personal_moments > 0
    assert result.personal_coverage == 1.0


def test_no_routine_cut_comes_sooner_than_the_minimum_dwell(
    matchday: Matchday, channels: dict[str, Channel]
) -> None:
    for channel in channels.values():
        assert report(matchday, channel).early_cuts == 0


def test_two_fans_get_genuinely_different_channels(
    matchday: Matchday, channels: dict[str, Channel]
) -> None:
    end = max(e.t for e in matchday.events())
    assert distinctness(channels["Arjun"], channels["Maya"], end) >= 0.5


def test_the_channel_opens_on_the_fans_club(channels: dict[str, Channel]) -> None:
    first = channels["Arjun"].decisions[0]
    assert first.kind is Kind.OPEN
    assert "your_club" in first.chosen.reasons


def test_every_replay_carries_the_moment_and_is_followed_by_a_cut(
    channels: dict[str, Channel],
) -> None:
    decisions = channels["Arjun"].decisions
    for i, decision in enumerate(decisions):
        if decision.kind is Kind.REPLAY:
            assert decision.event is not None
            follow = decisions[i + 1]
            assert follow.kind is Kind.CUT and follow.trigger is Trigger.MUST_SHOW
            assert follow.match_id == decision.match_id


def test_every_decision_explains_itself(channels: dict[str, Channel]) -> None:
    for channel in channels.values():
        for decision in channel.decisions:
            assert decision.chosen.match_id == decision.match_id
            assert decision.chosen.minute >= 1
            assert len(decision.alternatives) <= 3
            assert decision.match_id not in {alt.match_id for alt in decision.alternatives}


def test_the_fans_club_outranks_an_equal_neutral_match(matchday: Matchday) -> None:
    state = MatchdayState(matchday)
    for event in list(matchday.events())[:2000]:
        state.update(event)
    club_feed = next(f for f in state.feeds.values() if ARJUN.club_id in f.team_ids)
    other = next(f for f in state.feeds.values() if ARJUN.club_id not in f.team_ids)
    neutral = FanProfile(name="Neutral")
    boost = relevance(ARJUN, club_feed, state).value / relevance(neutral, club_feed, state).value
    assert boost > 2
    assert relevance(neutral, other, state).stake <= 0.3  # only the stakes bonus
