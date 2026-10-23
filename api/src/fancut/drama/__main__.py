"""Print a match's drama timeline: ``uv run python -m fancut.drama m019``."""

import argparse

from fancut.drama.engine import DramaEngine
from fancut.sim.league import build_league

BARS = " ▁▂▃▄▅▆▇█"


def main() -> None:
    parser = argparse.ArgumentParser(description="Show suspense, pressure and goals per minute.")
    parser.add_argument("match_id", help="e.g. m019")
    parser.add_argument("--seed", type=int, default=2026)
    args = parser.parse_args()

    match = next(m for m in build_league(args.seed) if m.meta.match_id == args.match_id)
    meta = match.meta
    print(f"{meta.home.name} vs {meta.away.name} · {meta.archetype} · {meta.stakes}")
    print("min  score  home/draw/away   suspense   pressure H/A  control")
    for s in DramaEngine(meta).run(match.events):
        if s.trigger not in ("minute", "goal", "red_card"):
            continue
        bar = BARS[round(s.suspense * (len(BARS) - 1))] * 8
        p = s.win_probability
        mark = {"goal": "  ⚽ GOAL", "red_card": "  🟥 RED"}.get(s.trigger, "")
        print(
            f"{s.minute:>3}' {s.score[0]}-{s.score[1]}  {p.home:.2f}/{p.draw:.2f}/{p.away:.2f}"
            f"   {bar} {s.pressure[0]:.2f}/{s.pressure[1]:.2f}  {s.control:+.2f}{mark}"
        )


if __name__ == "__main__":
    main()
