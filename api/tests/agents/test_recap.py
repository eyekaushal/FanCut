from fancut.agents.fact_checker import rule_problems
from fancut.agents.recap import MAX_RECAP_CHARS, RecapFacts, recap_facts
from fancut.agents.templates import narrate_recap
from fancut.demo import ARJUN, MAYA
from fancut.director.director import Director
from fancut.matchday.matchday import Matchday
from fancut.matchday.state import MatchdayState
from fancut.profile import FanProfile, Language


def _full_day(matchday: Matchday, profile: FanProfile) -> RecapFacts:
    state = MatchdayState(matchday)
    director = Director(profile)
    for event in matchday.events():
        director.observe(state.update(event), state)
    return recap_facts(profile, state, director)


def test_a_club_fan_gets_their_result_table_and_fantasy(matchday: Matchday) -> None:
    facts = _full_day(matchday, ARJUN)
    assert facts.fan_club == "Kingsmere City"
    assert facts.fan_club_opponent == "Glenhallow Athletic"
    assert facts.fan_club_goals is not None and facts.fan_club_opponent_goals is not None
    assert facts.fan_club_position_now and facts.fan_club_position_at_kickoff == 2
    assert facts.fantasy_total is not None and facts.fantasy_best_points
    assert facts.cuts > facts.replays > 0
    assert facts.moments_shown and all(m.minute >= 1 for m in facts.moments_shown)
    assert facts.most_dramatic_excitement_out_of_10 is None  # Arjun is casual


def test_a_neutral_analyst_gets_the_most_dramatic_match_instead(matchday: Matchday) -> None:
    facts = _full_day(matchday, MAYA)
    assert facts.fan_club is None and facts.fantasy_total is None
    assert facts.most_dramatic_excitement_out_of_10 is not None
    assert facts.required_names() == {facts.most_dramatic_home_team, facts.most_dramatic_away_team}


def test_the_reference_recap_passes_the_fact_checker_rules_in_every_language(
    matchday: Matchday,
) -> None:
    for profile in (ARJUN, MAYA):
        facts = _full_day(matchday, profile)
        for language in Language:
            text = narrate_recap(facts, language)
            assert rule_problems(text, facts, language, MAX_RECAP_CHARS) == [], (language, text)
            assert len(text) <= MAX_RECAP_CHARS
