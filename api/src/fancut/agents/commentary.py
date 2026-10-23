"""Write, check, rewrite, fall back: the loop that keeps narration truthful.

Code writes a correct reference line; the Narrator rewrites it vividly; the Fact Checker
accepts or rejects with reasons; the Narrator gets two more tries with that feedback;
after that the reference line itself airs.
Any model failure (timeout, outage) also falls back, so the channel never goes silent.
"""

import logging
from enum import StrEnum

from pydantic import BaseModel

from fancut.agents.fact_checker import FactChecker
from fancut.agents.facts import Facts
from fancut.agents.model import LanguageModel
from fancut.agents.narrator import Narrator
from fancut.profile import Depth, Language

MAX_DRAFTS = 3
log = logging.getLogger(__name__)


class Source(StrEnum):
    MODEL = "model"
    TEMPLATE = "template"


class Narration(BaseModel):
    text: str
    language: Language
    source: Source
    drafts: int  # model drafts written (0 when no model is configured)
    rejected: list[str]  # why earlier drafts were rejected


class Commentary:
    def __init__(self, model: LanguageModel | None) -> None:
        self._narrator = Narrator(model) if model is not None else None
        self._checker = FactChecker(model)

    async def narrate(
        self, facts: Facts, reference: str, language: Language, depth: Depth
    ) -> Narration:
        """``reference`` is the correct deterministic line; it airs if no draft passes."""
        if self._narrator is None:
            return Narration(
                text=reference, language=language, source=Source.TEMPLATE, drafts=0, rejected=[]
            )
        rejected: list[str] = []
        feedback: list[str] | None = None
        drafts = 0
        try:
            for _ in range(MAX_DRAFTS):
                drafts += 1
                text = await self._narrator.write(facts, reference, language, depth, feedback)
                problems = await self._checker.check(text, reference, facts, language)
                if not problems:
                    return Narration(
                        text=text,
                        language=language,
                        source=Source.MODEL,
                        drafts=drafts,
                        rejected=rejected,
                    )
                feedback = problems
                rejected += problems
        except Exception:  # an outage must never silence the channel
            log.exception("narration failed; using the template")
        return Narration(
            text=reference,
            language=language,
            source=Source.TEMPLATE,
            drafts=drafts,
            rejected=rejected,
        )
