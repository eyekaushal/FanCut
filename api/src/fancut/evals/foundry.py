"""The Narrator's lines scored by Microsoft Foundry's evaluators.

Collects real narrations (the model writes, the Fact Checker passes) for the demo
matchday, then runs the Azure AI Evaluation SDK's AI-assisted evaluators over them:
groundedness against the fact sheet, plus relevance, coherence and fluency. With a
Foundry project endpoint it also runs the content-safety evaluators.

Needs a model (``NK_LLM_*``) and the evaluation SDK: ``uv sync --group evals``.
"""

import asyncio
from collections.abc import Iterable
from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel

from fancut.agents.broadcast import beats
from fancut.agents.commentary import Commentary
from fancut.agents.model import LanguageModel
from fancut.agents.templates import narrate_cut
from fancut.config import Settings
from fancut.demo import PROFILES
from fancut.llm import openai_v1_base_url
from fancut.matchday.matchday import Matchday
from fancut.profile import Language

API_VERSION = "2024-10-21"
QUERY = (
    "Rewrite the REFERENCE line as one vivid broadcast line for this fan, in their "
    "language, adding nothing the FACTS do not support."
)
QUALITY = ("groundedness", "relevance", "coherence", "fluency")
SAFETY = ("violence", "sexual", "self_harm", "hate_unfairness")


class Row(BaseModel):
    """One narration as the evaluators see it: the task, its grounding, the answer."""

    id: str
    fan: str
    language: Language
    source: str  # "model" or "template"; only model lines are scored
    drafts: int
    query: str
    context: str
    response: str


class FoundryResult(BaseModel):
    generated_at: str
    matchday: str
    narrator_model: str
    evaluator_model: str
    rows: int
    scored: int  # model-written lines (template fallbacks are not the Narrator's work)
    template_fallbacks: int
    metrics: dict[str, float]  # mean score per evaluator, 1 to 5 (safety: 0 to 7)
    pass_rates: dict[str, float]  # share of lines at or above the evaluator's threshold
    safety_run: bool
    per_row: list[dict[str, Any]]


async def collect_rows(
    matchday: Matchday,
    model: LanguageModel,
    languages: Iterable[Language] = (Language.ENGLISH, Language.HINDI, Language.HINGLISH),
    per_fan: int | None = None,
    concurrency: int = 6,
) -> list[Row]:
    commentary = Commentary(model)
    gate = asyncio.Semaphore(concurrency)
    jobs = []
    for key, profile in PROFILES.items():
        found = beats(matchday, profile)
        if per_fan is not None:
            found = found[:per_fan]
        for i, beat in enumerate(found):
            for language in languages:
                jobs.append((f"{key}-{i:02d}-{language.value}", profile, beat, language))

    async def one(job: tuple[Any, ...]) -> Row:
        row_id, profile, beat, language = job
        reference = narrate_cut(beat.facts, language)
        async with gate:
            line = await commentary.narrate(beat.facts, reference, language, profile.depth)
        return Row(
            id=row_id,
            fan=profile.name,
            language=language,
            source=line.source.value,
            drafts=line.drafts,
            query=QUERY,
            context=f"REFERENCE: {reference}\nFACTS: {beat.facts.to_prompt()}",
            response=line.text,
        )

    return await asyncio.gather(*(one(job) for job in jobs))


def evaluate_rows(
    rows: list[Row],
    settings: Settings,
    narrator_model: str,
    matchday_id: str,
    project_endpoint: str | None = None,
) -> FoundryResult:
    """Score the model-written rows. Imports the SDK here so the API never needs it."""
    from azure.ai.evaluation import (
        AzureOpenAIModelConfiguration,
        CoherenceEvaluator,
        FluencyEvaluator,
        GroundednessEvaluator,
        RelevanceEvaluator,
    )

    assert settings.llm_endpoint and settings.llm_api_key and settings.llm_deployment
    config = AzureOpenAIModelConfiguration(
        azure_endpoint=openai_v1_base_url(settings.llm_endpoint).removesuffix("openai/v1/"),
        api_key=settings.llm_api_key.get_secret_value(),
        azure_deployment=settings.llm_deployment,
        api_version=API_VERSION,
    )
    evaluators: dict[str, Any] = {
        "groundedness": GroundednessEvaluator(config),
        "relevance": RelevanceEvaluator(config),
        "coherence": CoherenceEvaluator(config),
        "fluency": FluencyEvaluator(config),
    }
    safety: dict[str, Any] = {}
    if project_endpoint:
        from azure.ai.evaluation import ContentSafetyEvaluator
        from azure.identity import DefaultAzureCredential

        safety["content_safety"] = ContentSafetyEvaluator(
            azure_ai_project=project_endpoint, credential=DefaultAzureCredential()
        )

    scored = [r for r in rows if r.source == "model"]
    per_row: list[dict[str, Any]] = []
    scores: dict[str, list[float]] = {}
    passes: dict[str, list[bool]] = {}
    for row in scored:
        record: dict[str, Any] = {"id": row.id, "fan": row.fan, "language": row.language.value}
        for name, evaluator in evaluators.items():
            result = evaluator(query=row.query, context=row.context, response=row.response)
            score = float(result[name])
            record[name] = score
            record[f"{name}_reason"] = result.get(f"{name}_reason")
            scores.setdefault(name, []).append(score)
            passes.setdefault(name, []).append(result.get(f"{name}_result") == "pass")
        for evaluator in safety.values():
            result = evaluator(query=row.query, response=row.response)
            for kind in SAFETY:
                score = float(result[f"{kind}_score"])
                record[kind] = score
                scores.setdefault(kind, []).append(score)
                passes.setdefault(kind, []).append(result.get(f"{kind}_result") == "pass")
        per_row.append(record)

    return FoundryResult(
        generated_at=datetime.now(UTC).isoformat(timespec="seconds"),
        matchday=matchday_id,
        narrator_model=narrator_model,
        evaluator_model=settings.llm_deployment,
        rows=len(rows),
        scored=len(scored),
        template_fallbacks=len(rows) - len(scored),
        metrics={k: round(sum(v) / len(v), 3) for k, v in scores.items() if v},
        pass_rates={k: round(sum(v) / len(v), 4) for k, v in passes.items() if v},
        safety_run=bool(safety),
        per_row=per_row,
    )
