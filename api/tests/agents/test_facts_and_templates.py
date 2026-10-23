from fancut.agents.broadcast import Beat
from fancut.agents.fact_checker import rule_problems
from fancut.agents.templates import narrate_cut
from fancut.profile import Language


def test_every_template_line_passes_the_fact_checker_rules(
    arjun_beats: list[Beat], maya_beats: list[Beat]
) -> None:
    """The fallback must itself be truthful: every beat, every language."""
    for beat in [*arjun_beats, *maya_beats]:
        for language in Language:
            line = narrate_cut(beat.facts, language)
            assert rule_problems(line, beat.facts, language) == [], (language, line)


def test_who_is_who_states_what_each_name_is_not(arjun_beats: list[Beat]) -> None:
    opening = arjun_beats[0].facts
    roles = opening.who_is_who()
    assert (
        "THE FAN'S CLUB" in roles[opening.home_team] or "THE FAN'S CLUB" in roles[opening.away_team]
    )
    followed = opening.players_the_fan_follows_on_pitch[0]
    assert "a player the fan follows" in roles[followed]
    assert "NOT in the fan's fantasy team" in roles[followed]


def test_casual_fans_get_no_analyst_numbers(
    arjun_beats: list[Beat], maya_beats: list[Beat]
) -> None:
    assert all(b.facts.suspense_out_of_10 is None for b in arjun_beats)  # Arjun is casual
    assert all(b.facts.suspense_out_of_10 is not None for b in maya_beats)  # Maya is an analyst


def test_replays_name_the_moment(arjun_beats: list[Beat]) -> None:
    replays = [b for b in arjun_beats if b.facts.kind == "replay"]
    assert replays
    for beat in replays:
        assert beat.facts.moment is not None
        assert beat.facts.moment.player in narrate_cut(beat.facts, Language.HINDI)
