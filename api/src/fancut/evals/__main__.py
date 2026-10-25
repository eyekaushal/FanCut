"""Run the evaluations from a terminal and record the results.

    uv run python -m fancut.evals director [--seeds 34 35 ...]
    uv run python -m fancut.evals redteam [--judge] [--limit N]
    uv run python -m fancut.evals foundry [--per-fan N] [--safety <project endpoint>]

Results land in ``fancut/evals/results/`` (committed), where ``GET /evaluation`` serves
them and the Studio's Trust screen shows them.
"""

import argparse
import asyncio
import sys

from fancut.agents.model import FoundryModel
from fancut.config import get_settings
from fancut.evals.director import DEFAULT_SEEDS, markdown, measure_director
from fancut.evals.foundry import collect_rows, evaluate_rows
from fancut.evals.redteam import build_cases, run_judge, summarize
from fancut.evals.results import save_result
from fancut.llm import chat_client
from fancut.matchday.matchday import build_matchday


def director(seeds: list[int]) -> None:
    result = measure_director(seeds, on_progress=lambda n: print(f"  matchday {n}/{len(seeds)}"))
    path = save_result("director", result.model_dump())
    print(markdown(result))
    print(f"\nwritten: {path}")


def redteam(judge: bool, limit: int | None) -> None:
    settings = get_settings()
    matchday = build_matchday()
    cases = build_cases(matchday)
    if limit:
        cases = cases[:limit]
    judged = None
    if judge:
        if not settings.llm_configured:
            sys.exit(
                "--judge needs a model: set NK_LLM_ENDPOINT, NK_LLM_API_KEY, NK_LLM_DEPLOYMENT"
            )
        model = FoundryModel(chat_client(settings))
        judged = asyncio.run(run_judge(cases, model, settings.llm_deployment or "model"))
    result = summarize(matchday, cases, judged)
    path = save_result("redteam", result.model_dump())
    r = result.rules
    print(f"{result.cases} cases in {len(result.languages)} languages")
    print(
        f"rules: caught {r.caught}/{r.rule_detectable} rule-detectable, "
        f"{r.false_rejects} false rejects, {r.judge_only} left to the judge"
    )
    if judged:
        print(
            f"judge ({judged.model}): caught {judged.caught}/{judged.caught + judged.missed}, "
            f"{judged.false_rejects} false rejects of {judged.cases} cases seen"
        )
    for name, tally in result.rules.by_mutation.items():
        line = f"  {name:18} rules {tally.caught}/{tally.cases}"
        if judged and name in judged.by_mutation:
            j = judged.by_mutation[name]
            line += f"   judge {j.caught}/{j.cases}"
        print(line)
    print(f"\nwritten: {path}")


def foundry(per_fan: int | None, safety: str | None) -> None:
    settings = get_settings()
    if not settings.llm_configured:
        sys.exit("needs a model: set NK_LLM_ENDPOINT, NK_LLM_API_KEY, NK_LLM_DEPLOYMENT")
    try:
        import azure.ai.evaluation  # noqa: F401
    except ImportError:
        sys.exit("needs the evaluation SDK: uv sync --group evals")
    matchday = build_matchday()
    model = FoundryModel(chat_client(settings))
    print("narrating…")
    rows = asyncio.run(collect_rows(matchday, model, per_fan=per_fan))
    print(f"scoring {sum(r.source == 'model' for r in rows)} model lines of {len(rows)}…")
    result = evaluate_rows(rows, settings, settings.llm_deployment or "model", matchday.id, safety)
    path = save_result("foundry", result.model_dump())
    for name, value in result.metrics.items():
        print(f"  {name:16} {value:.2f}   pass {result.pass_rates.get(name, 0):.0%}")
    print(f"\nwritten: {path}")


def main() -> None:
    parser = argparse.ArgumentParser(description="FanCut evaluations.")
    sub = parser.add_subparsers(dest="command", required=True)
    d = sub.add_parser("director", help="measure the Director over matchdays (no Azure)")
    d.add_argument("--seeds", type=int, nargs="+", default=list(DEFAULT_SEEDS))
    r = sub.add_parser("redteam", help="red-team the Fact Checker")
    r.add_argument("--judge", action="store_true", help="also run the model judge")
    r.add_argument("--limit", type=int, default=None)
    f = sub.add_parser("foundry", help="score the Narrator with Foundry's evaluators")
    f.add_argument("--per-fan", type=int, default=None, help="beats per fan (default: all)")
    f.add_argument("--safety", metavar="PROJECT_ENDPOINT", default=None)
    args = parser.parse_args()
    if args.command == "director":
        director(args.seeds)
    elif args.command == "redteam":
        redteam(args.judge, args.limit)
    else:
        foundry(args.per_fan, args.safety)


if __name__ == "__main__":
    main()
