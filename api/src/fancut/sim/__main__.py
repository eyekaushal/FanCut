"""Export the synthetic league as JSON: ``uv run python -m fancut.sim --out data/league``."""

import argparse
import json
from pathlib import Path

from fancut.sim.league import build_league


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate the labelled synthetic league.")
    parser.add_argument("--seed", type=int, default=2026)
    parser.add_argument("--out", type=Path, default=Path("data/league"))
    args = parser.parse_args()

    args.out.mkdir(parents=True, exist_ok=True)
    index = []
    for match in build_league(args.seed):
        (args.out / f"{match.meta.match_id}.json").write_text(match.model_dump_json(indent=1))
        home, away = match.truth.final_score
        index.append(
            {
                "match_id": match.meta.match_id,
                "fixture": f"{match.meta.home.name} {home}-{away} {match.meta.away.name}",
                "archetype": match.meta.archetype,
                "verdict": match.truth.verdict,
                "decisive_windows": len(match.truth.decisive_windows),
                "events": len(match.events),
            }
        )
    (args.out / "index.json").write_text(json.dumps(index, indent=1))
    print(f"Wrote {len(index)} matches to {args.out}")


if __name__ == "__main__":
    main()
