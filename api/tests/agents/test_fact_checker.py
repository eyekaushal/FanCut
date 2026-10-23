import pytest

from fancut.agents.fact_checker import FactChecker, Verdict, rule_problems
from fancut.agents.facts import CutFacts, Moment
from fancut.profile import Language

from .conftest import ScriptedModel

FACTS = CutFacts(
    kind="replay",
    minute=71,
    home_team="Elmhurst Wanderers",
    away_team="Copperhill City",
    home_goals=2,
    away_goals=1,
    moment=Moment(
        type="goal", player="Callum Brannagh", player_team="Elmhurst Wanderers", minute=71
    ),
    fan_fantasy_players_on_pitch=("Callum Brannagh",),
)
GOOD = "Replay: Callum Brannagh scores for Elmhurst Wanderers, 2-1 against Copperhill City at 71'."


def test_a_truthful_line_passes() -> None:
    assert rule_problems(GOOD, FACTS, Language.ENGLISH) == []


@pytest.mark.parametrize(
    ("text", "problem"),
    [
        (GOOD.replace("2-1", "3-1"), "number 3"),
        (GOOD.replace("71", "७२"), "number ७२"),  # Devanagari digits are checked too
        (GOOD + " Rohan Mehta watches on.", "Rohan Mehta is not in the facts"),
        ("Brannagh scores, 2-1 at 71'.", "must name the match's teams"),
        (GOOD.replace("Callum Brannagh", "Brannagh"), "must mention Callum Brannagh"),
    ],
)
def test_rules_catch_wrong_numbers_names_and_missing_subjects(text: str, problem: str) -> None:
    assert any(problem in p for p in rule_problems(text, FACTS, Language.ENGLISH))


def test_rules_enforce_the_script_of_each_language() -> None:
    hindi = "Elmhurst Wanderers के लिए Callum Brannagh का गोल, 2-1, 71'।"
    assert rule_problems(hindi, FACTS, Language.HINDI) == []
    assert any("Devanagari" in p for p in rule_problems(GOOD, FACTS, Language.HINDI))
    assert any("Devanagari" in p for p in rule_problems(hindi, FACTS, Language.HINGLISH))


async def test_the_judge_runs_only_after_the_rules_pass() -> None:
    model = ScriptedModel(verdicts=[Verdict(supported=False, problems=["wrong team"])])
    checker = FactChecker(model)

    assert await checker.check(GOOD.replace("2-1", "3-1"), GOOD, FACTS, Language.ENGLISH)
    assert model.calls == []  # rule failure: no model call wasted

    assert await checker.check(GOOD, GOOD, FACTS, Language.ENGLISH) == ["wrong team"]
    assert model.calls == ["FactChecker"]
