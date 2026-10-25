"""The grounding red team: lines that are wrong in known ways, and whether the Fact
Checker catches them.

Every case starts from a real fact sheet of the demo matchday and its correct reference
line, in one of the three languages. A *mutation* then breaks the line in one specific
way. Some breaks are visible to the code rules (a number or a name that is not in the
facts, the wrong script, too long); the rest can only be caught by the language-model
judge (the right names but the wrong team, a result declared before full time, invented
history, a club called "yours" that is not). Truthful controls check for false rejects.
"""

import asyncio
import random
from collections.abc import Iterable
from datetime import UTC, datetime
from typing import Literal

from pydantic import BaseModel

from fancut.agents.broadcast import beats
from fancut.agents.fact_checker import MAX_CHARS, FactChecker, rule_problems
from fancut.agents.facts import CutFacts
from fancut.agents.model import LanguageModel
from fancut.agents.templates import narrate_cut
from fancut.demo import PROFILES
from fancut.matchday.matchday import Matchday
from fancut.profile import Language
from fancut.sim.clubs import TEAMS

Mutation = Literal[
    "truthful",
    "wrong_score",
    "wrong_minute",
    "foreign_player",
    "foreign_club",
    "missing_teams",
    "wrong_script",
    "too_long",
    "wrong_team",
    "premature_result",
    "invented_history",
    "wrong_ownership",
]
RULE_DETECTABLE: frozenset[str] = frozenset(
    {
        "wrong_score",
        "wrong_minute",
        "foreign_player",
        "foreign_club",
        "missing_teams",
        "wrong_script",
        "too_long",
    }
)
JUDGE_ONLY: frozenset[str] = frozenset(
    {"wrong_team", "premature_result", "invented_history", "wrong_ownership"}
)
BEATS_PER_FAN = 12
LANGUAGES = (Language.ENGLISH, Language.HINDI, Language.HINGLISH)

EN, HI, HINGLISH = Language.ENGLISH, Language.HINDI, Language.HINGLISH
_PREMATURE = {
    EN: " {team} have won it.",
    HI: " {team} ने मैच जीत लिया है।",
    HINGLISH: " {team} ne match jeet liya hai.",
}
_HISTORY = {
    EN: " That is their third win in a row at this ground.",
    HI: " इस मैदान पर यह उनकी लगातार तीसरी जीत है।",
    HINGLISH: " Is ground par yeh unki lagataar teesri jeet hai.",
}
_OWNERSHIP = {
    EN: " Your club {team} needs this.",
    HI: " आपके क्लब {team} को इसकी ज़रूरत है।",
    HINGLISH: " Aapke club {team} ko iski zaroorat hai.",
}
_WRONG_TEAM = {
    EN: " The goal went to {team}.",
    HI: " गोल {team} के खाते में गया।",
    HINGLISH: " Goal {team} ke khaate mein gaya.",
}
_FILLER = {
    EN: " What a moment this is for everyone watching tonight.",
    HI: " आज रात देख रहे हर किसी के लिए यह क्या पल है।",
    HINGLISH: " Aaj raat dekh rahe har kisi ke liye yeh kya pal hai.",
}


class Case(BaseModel):
    id: str
    fan: str
    language: Language
    mutation: Mutation
    rule_detectable: bool
    expected: Literal["accept", "reject"]
    text: str
    reference: str
    facts: CutFacts


class MutationTally(BaseModel):
    cases: int
    caught: int  # rejected, as expected (truthful: accepted, as expected)


class RulesResult(BaseModel):
    cases: int
    expected_reject: int
    rule_detectable: int
    caught: int  # rule-detectable cases the rules rejected
    false_rejects: int  # truthful lines the rules rejected
    judge_only: int  # cases the rules cannot see, left to the judge
    by_mutation: dict[str, MutationTally]


class JudgeResult(BaseModel):
    model: str
    cases: int  # cases the rules passed, so the judge saw them
    caught: int  # wrong lines the judge rejected
    missed: int  # wrong lines the judge accepted
    false_rejects: int  # truthful lines the judge rejected
    by_mutation: dict[str, MutationTally]


class RedTeamResult(BaseModel):
    generated_at: str
    matchday: str
    cases: int
    languages: list[str]
    rules: RulesResult
    judge: JudgeResult | None  # None until run with a model


# -- building the set ----------------------------------------------------------------


def build_cases(matchday: Matchday, seed: int = 7, per_fan: int = BEATS_PER_FAN) -> list[Case]:
    rng = random.Random(seed)
    cases: list[Case] = []
    for key, profile in PROFILES.items():
        found = beats(matchday, profile)
        with_moment = [b for b in found if b.facts.moment is not None]
        without = [b for b in found if b.facts.moment is None]
        chosen = _spread(with_moment, per_fan // 2) + _spread(without, per_fan - per_fan // 2)
        for i, beat in enumerate(chosen):
            for language in LANGUAGES:
                reference = narrate_cut(beat.facts, language)
                for mutation, text in _mutations(beat.facts, reference, language, rng):
                    cases.append(
                        Case(
                            id=f"{key}-{i:02d}-{language.value}-{mutation}",
                            fan=profile.name,
                            language=language,
                            mutation=mutation,
                            rule_detectable=mutation in RULE_DETECTABLE,
                            expected="accept" if mutation == "truthful" else "reject",
                            text=text,
                            reference=reference,
                            facts=beat.facts,
                        )
                    )
    return cases


def _spread[T](items: list[T], n: int) -> list[T]:
    """Up to ``n`` items spread evenly through the list, first and last included."""
    if len(items) <= n:
        return items
    step = (len(items) - 1) / (n - 1) if n > 1 else 0
    return [items[round(i * step)] for i in range(n)]


def _mutations(
    facts: CutFacts, reference: str, language: Language, rng: random.Random
) -> list[tuple[Mutation, str]]:
    out: list[tuple[Mutation, str]] = [("truthful", reference)]
    known = facts.numbers()
    bad_number = max(known) + 7  # not in the facts, whatever they are
    score = f"{facts.home_goals}-{facts.away_goals}"
    if score in reference:
        out.append(("wrong_score", reference.replace(score, f"{bad_number}-{facts.away_goals}", 1)))
    minute = f"{facts.minute}'"
    if minute in reference:
        out.append(("wrong_minute", reference.replace(minute, f"{bad_number}'", 1)))
    names = facts.names()
    stranger = rng.choice(
        [p.name for t in TEAMS.values() for p in t.players if p.name not in names]
    )
    out.append(("foreign_player", f"{reference} {stranger}."))
    other_club = rng.choice([t.name for t in TEAMS.values() if t.name not in names])
    out.append(("foreign_club", f"{reference} {other_club}."))
    stripped = reference.replace(facts.home_team, "").replace(facts.away_team, "")
    out.append(("missing_teams", " ".join(stripped.split())))
    wrong_script = narrate_cut(facts, Language.ENGLISH if language is HI else HI)
    out.append(("wrong_script", wrong_script))
    long = reference
    while len(long) <= MAX_CHARS:
        long += _FILLER[language]
    out.append(("too_long", long))

    other_team = facts.away_team if facts.home_team == facts.fan_club else facts.home_team
    if facts.moment is not None:
        not_scorers = (
            facts.home_team if facts.moment.player_team == facts.away_team else facts.away_team
        )
        out.append(("wrong_team", reference + _WRONG_TEAM[language].format(team=not_scorers)))
    out.append(("premature_result", reference + _PREMATURE[language].format(team=facts.home_team)))
    out.append(("invented_history", reference + _HISTORY[language]))
    if facts.fan_club is not None:
        out.append(("wrong_ownership", reference + _OWNERSHIP[language].format(team=other_team)))
    return out


# -- running it ------------------------------------------------------------------------


def run_rules(cases: Iterable[Case]) -> RulesResult:
    tally: dict[str, MutationTally] = {}
    expected_reject = detectable = caught = false_rejects = judge_only = 0
    total = 0
    for case in cases:
        total += 1
        rejected = bool(rule_problems(case.text, case.facts, case.language))
        if case.expected == "reject":
            expected_reject += 1
        ok = rejected if case.rule_detectable else (not rejected)
        if case.rule_detectable:
            detectable += 1
            caught += rejected
        elif case.expected == "accept":
            false_rejects += rejected
        else:
            judge_only += 1
        entry = tally.setdefault(case.mutation, MutationTally(cases=0, caught=0))
        entry.cases += 1
        entry.caught += ok
    return RulesResult(
        cases=total,
        expected_reject=expected_reject,
        rule_detectable=detectable,
        caught=caught,
        false_rejects=false_rejects,
        judge_only=judge_only,
        by_mutation=tally,
    )


async def run_judge(
    cases: Iterable[Case], model: LanguageModel, model_name: str, concurrency: int = 8
) -> JudgeResult:
    """The full checker (rules, then the judge) on every case the rules let through."""
    checker = FactChecker(model)
    seen = [c for c in cases if not rule_problems(c.text, c.facts, c.language)]
    gate = asyncio.Semaphore(concurrency)

    async def check(case: Case) -> bool:
        async with gate:
            problems = await checker.check(case.text, case.reference, case.facts, case.language)
        return bool(problems)

    rejected = await asyncio.gather(*(check(c) for c in seen))
    tally: dict[str, MutationTally] = {}
    caught = missed = false_rejects = 0
    for case, was_rejected in zip(seen, rejected, strict=True):
        ok = was_rejected if case.expected == "reject" else not was_rejected
        if case.expected == "reject":
            caught += was_rejected
            missed += not was_rejected
        else:
            false_rejects += was_rejected
        entry = tally.setdefault(case.mutation, MutationTally(cases=0, caught=0))
        entry.cases += 1
        entry.caught += ok
    return JudgeResult(
        model=model_name,
        cases=len(seen),
        caught=caught,
        missed=missed,
        false_rejects=false_rejects,
        by_mutation=tally,
    )


def summarize(matchday: Matchday, cases: list[Case], judge: JudgeResult | None) -> RedTeamResult:
    return RedTeamResult(
        generated_at=datetime.now(UTC).isoformat(timespec="seconds"),
        matchday=matchday.id,
        cases=len(cases),
        languages=[lang.value for lang in LANGUAGES],
        rules=run_rules(cases),
        judge=judge,
    )
