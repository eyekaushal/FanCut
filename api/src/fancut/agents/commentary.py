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
from fancut.agents.recap import MAX_RECAP_CHARS, RecapFacts, RecapNarrator
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
        self._recap_narrator = RecapNarrator(model) if model is not None else None
        self._checker = FactChecker(model)

    async def narrate(
        self, facts: Facts, reference: str, language: Language, depth: Depth
    ) -> Narration:
        """``reference`` is the correct deterministic line; it airs if no draft passes."""
        return await self._loop(self._narrator, facts, reference, language, depth)

    async def recap(
        self, facts: RecapFacts, reference: str, language: Language, depth: Depth
    ) -> Narration:
        """The matchday recap, written and checked the same way, with room for 3 sentences."""
        return await self._loop(
            self._recap_narrator, facts, reference, language, depth, MAX_RECAP_CHARS
        )

    async def _loop(
        self,
        writer: Narrator | RecapNarrator | None,
        facts: Facts,
        reference: str,
        language: Language,
        depth: Depth,
        max_chars: int | None = None,
    ) -> Narration:
        if writer is None:
            return Narration(
                text=reference, language=language, source=Source.TEMPLATE, drafts=0, rejected=[]
            )
        check = {"max_chars": max_chars} if max_chars else {}
        rejected: list[str] = []
        feedback: list[str] | None = None
        drafts = 0
        try:
            for _ in range(MAX_DRAFTS):
                drafts += 1
                text = await writer.write(facts, reference, language, depth, feedback)  # type: ignore[arg-type]
                problems = await self._checker.check(text, reference, facts, language, **check)
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
