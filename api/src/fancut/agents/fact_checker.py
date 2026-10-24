"""The Fact Checker: no sentence reaches a fan unless the facts support it.

Two layers. Cheap code rules run first: every number must come from the fact sheet,
every league name mentioned must be in it, and the text must be in the right script.
Then a language-model judge looks for anything the rules cannot see (a wrong scorer,
an invented claim, a twisted meaning).
"""

import re

from pydantic import BaseModel

from fancut.agents.facts import Facts
from fancut.agents.model import LanguageModel
from fancut.profile import Language
from fancut.sim.clubs import TEAMS

MAX_CHARS = 320
_DEVANAGARI = re.compile("[\u0900-\u097f]")
_DIGITS = re.compile("[0-9\u0966-\u096f]+")  # ASCII and Devanagari digits
_DEVANAGARI_DIGITS = {0x0966 + digit: str(digit) for digit in range(10)}
LEAGUE_NAMES = {t.name for t in TEAMS.values()} | {
    p.name for t in TEAMS.values() for p in t.players
}

JUDGE_INSTRUCTIONS = """You are a strict sports fact checker for a personal football channel.
You receive FACTS (JSON), a REFERENCE line known to be correct, and a TEXT written for one
fan (possibly in Hindi or Hinglish) that should say the same thing more vividly.
The REFERENCE is ground truth: never reject the TEXT for agreeing with it. Reject only
what the TEXT adds or changes that the FACTS do not support. Check carefully:
1. Attribution: who scored or was sent off, and for which team (moment.player_team).
2. Ownership: use "who_is_who" as the ground truth for every name. "Your club" may refer
   ONLY to the name marked THE FAN'S CLUB. A player marked "NOT in the fan's fantasy team"
   must never be called a fantasy player, and vice versa.
3. Positions: fan_club_position_* are the FAN'S CLUB's league positions, never another team's.
4. Score, minute and every number must match the FACTS exactly.
5. No invented events, predictions stated as certain, or claims absent from the FACTS.
   Reject added history, rivalries, match phase, "opening the scoring" for a second goal,
   and any claim that a team won or beat another before full time.
6. The words must make sense: reject garbled or nonsensical words or names, and calling
   the match itself a "replay" (only the moment is replayed).
Return supported=false with one short problem per violation; otherwise supported=true."""


class Verdict(BaseModel):
    supported: bool
    problems: list[str]


def rule_problems(
    text: str, facts: Facts, language: Language, max_chars: int = MAX_CHARS
) -> list[str]:
    problems = []
    if len(text) > max_chars:
        problems.append(f"too long ({len(text)} characters)")
    allowed = facts.numbers()
    for raw in _DIGITS.findall(text):
        if int(raw.translate(_DEVANAGARI_DIGITS)) not in allowed:
            problems.append(f"number {raw} is not in the facts")
    if not any(name in text for name in facts.required_names()):
        problems.append("must name the match's teams exactly as written in the facts")
    for name in facts.must_mention():
        if name not in text:
            problems.append(f"must mention {name} exactly as written (Latin script)")
    named = facts.names()
    for name in LEAGUE_NAMES:
        if name in text and name not in named:
            problems.append(f"{name} is not in the facts")
    has_devanagari = bool(_DEVANAGARI.search(text))
    if language is Language.HINDI and not has_devanagari:
        problems.append("Hindi text must be written in Devanagari")
    if language is not Language.HINDI and has_devanagari:
        problems.append(f"{language.value} text must not use Devanagari")
    return problems


class FactChecker:
    def __init__(self, model: LanguageModel | None) -> None:
        self._model = model

    async def check(
        self,
        text: str,
        reference: str,
        facts: Facts,
        language: Language,
        max_chars: int = MAX_CHARS,
    ) -> list[str]:
        """Problems found; an empty list means the text may go on air."""
        problems = rule_problems(text, facts, language, max_chars)
        if problems or self._model is None:
            return problems
        verdict = await self._model.structured(
            agent="FactChecker",
            instructions=JUDGE_INSTRUCTIONS,
            prompt=f"FACTS: {facts.to_prompt()}\nREFERENCE: {reference}\nTEXT: {text}",
            schema=Verdict,
        )
        return [] if verdict.supported else verdict.problems or ["judge rejected the text"]
