import pytest
from pydantic import BaseModel

from fancut.agents.fact_checker import Verdict
from fancut.evals.redteam import (
    JUDGE_ONLY,
    LANGUAGES,
    RULE_DETECTABLE,
    Case,
    build_cases,
    run_judge,
    run_rules,
    summarize,
)
from fancut.matchday.matchday import Matchday


class ScriptedJudge:
    """A judge whose verdicts come from a script, in order; it never writes text."""

    def __init__(self, verdicts: list[Verdict]) -> None:
        self._verdicts = iter(verdicts)

    async def text(self, agent: str, instructions: str, prompt: str) -> str:
        raise AssertionError("the judge never writes")

    async def structured[S: BaseModel](
        self, agent: str, instructions: str, prompt: str, schema: type[S]
    ) -> S:
        verdict = next(self._verdicts)
        assert isinstance(verdict, schema)
        return verdict


@pytest.fixture(scope="module")
def cases(matchday: Matchday) -> list[Case]:
    return build_cases(matchday)


def test_the_set_covers_both_fans_every_language_and_every_mutation(cases: list[Case]) -> None:
    assert {c.fan for c in cases} == {"Arjun", "Maya"}
    assert {c.language for c in cases} == set(LANGUAGES)
    assert {c.mutation for c in cases} >= RULE_DETECTABLE | JUDGE_ONLY | {"truthful"}
    assert len(cases) > 500
    assert len({c.id for c in cases}) == len(cases)  # ids are unique


def test_the_set_is_reproducible(matchday: Matchday, cases: list[Case]) -> None:
    assert build_cases(matchday) == cases


def test_the_rules_catch_every_rule_detectable_case_and_pass_every_truthful_one(
    cases: list[Case],
) -> None:
    result = run_rules(cases)
    assert result.caught == result.rule_detectable
    assert result.false_rejects == 0
    assert result.judge_only == sum(c.mutation in JUDGE_ONLY for c in cases)
    assert result.by_mutation["truthful"].caught == result.by_mutation["truthful"].cases
    for mutation in RULE_DETECTABLE:
        assert result.by_mutation[mutation].caught == result.by_mutation[mutation].cases


def test_judge_only_cases_really_do_pass_the_rules(cases: list[Case]) -> None:
    """If a judge-only case tripped a rule, it would be mislabelled."""
    from fancut.agents.fact_checker import rule_problems

    for case in cases:
        if case.mutation in JUDGE_ONLY:
            assert rule_problems(case.text, case.facts, case.language) == [], case.id


async def test_the_judge_run_counts_catches_misses_and_false_rejects(cases: list[Case]) -> None:
    seen = [c for c in cases if c.mutation in ("truthful", "premature_result")][:6]
    # Alternate verdicts so both outcomes occur for both kinds of case.
    verdicts = [
        Verdict(supported=i % 2 == 0, problems=[] if i % 2 == 0 else ["x"]) for i in range(6)
    ]
    result = await run_judge(seen, ScriptedJudge(verdicts), "scripted", concurrency=1)
    assert result.model == "scripted" and result.cases == 6
    assert result.caught + result.missed == sum(c.expected == "reject" for c in seen)
    assert result.false_rejects <= sum(c.expected == "accept" for c in seen)
    assert set(result.by_mutation) <= {"truthful", "premature_result"}


def test_the_summary_records_the_matchday_and_leaves_the_judge_open(
    matchday: Matchday, cases: list[Case]
) -> None:
    result = summarize(matchday, cases[:40], None)
    assert result.matchday == matchday.id and result.cases == 40 and result.judge is None
    assert result.languages == ["en", "hi", "hinglish"]
