"""Try the agents from a terminal.

    uv run python -m fancut.agents narrate --fan arjun --language hi --limit 8
    uv run python -m fancut.agents profile "Kingsmere fan, Mehta is my captain, Hinglish please"

Without Azure settings (or with --offline) everything runs on the deterministic templates.
"""

import argparse
import asyncio

from fancut.agents.broadcast import beats
from fancut.agents.commentary import Commentary
from fancut.agents.model import FoundryModel, LanguageModel
from fancut.agents.profile_compiler import ProfileCompiler
from fancut.agents.templates import narrate_cut
from fancut.config import get_settings
from fancut.demo import PROFILES
from fancut.llm import chat_client
from fancut.matchday.matchday import build_matchday
from fancut.profile import Language
from fancut.telemetry import setup_tracing


def _model(offline: bool) -> LanguageModel | None:
    settings = get_settings()
    if offline or not settings.llm_configured:
        return None
    setup_tracing(settings)
    return FoundryModel(chat_client(settings))


async def narrate(fan: str, language: Language, limit: int, offline: bool) -> None:
    profile = PROFILES[fan]
    commentary = Commentary(_model(offline))
    for beat in beats(build_matchday(), profile)[:limit]:
        reference = narrate_cut(beat.facts, language)
        line = await commentary.narrate(beat.facts, reference, language, profile.depth)
        print(
            f"{beat.decision.t / 60:5.1f}'  [{line.source.value}, drafts {line.drafts}] {line.text}"
        )


async def profile(message: str, offline: bool) -> None:
    compiled = await ProfileCompiler(_model(offline)).compile(message)
    print(compiled.profile.model_dump_json(indent=2))
    print(f"\n{compiled.readback}")
    for question in compiled.questions:
        print(f"? {question}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run FanCut's agents.")
    parser.add_argument("--offline", action="store_true", help="templates only, no model")
    sub = parser.add_subparsers(dest="command", required=True)
    n = sub.add_parser("narrate", help="narrate a fan's matchday")
    n.add_argument("--fan", default="arjun", choices=sorted(PROFILES))
    n.add_argument("--language", default="en", choices=[lang.value for lang in Language])
    n.add_argument("--limit", type=int, default=8)
    p = sub.add_parser("profile", help="compile a profile from plain language")
    p.add_argument("message")
    args = parser.parse_args()

    if args.command == "narrate":
        asyncio.run(narrate(args.fan, Language(args.language), args.limit, args.offline))
    else:
        asyncio.run(profile(args.message, args.offline))


if __name__ == "__main__":
    main()
