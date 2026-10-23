"""Two fans, one matchday: ``uv run python -m fancut.director``.

Prints each fan's channel (every open, cut and replay, with its reason) and the
evaluation numbers, so the difference between personal channels is plain to see.
"""

import argparse

from fancut.demo import PROFILES
from fancut.director.director import Decision, Kind
from fancut.director.evaluate import distinctness, report, run_channel
from fancut.matchday.matchday import Matchday, build_matchday
from fancut.sim.clubs import TEAMS

PLAYERS = {p.id: p.name for team in TEAMS.values() for p in team.players}
REASON_LABELS = {
    "your_club": "your club",
    "rival": "table rival",
    "followed_player": "follows",
    "fantasy_player": "fantasy",
    "captain": "captain",
    "stakes": "stakes",
}


def describe(decision: Decision, matchday: Matchday) -> str:
    meta = matchday.match(decision.match_id).meta
    home, away = decision.chosen.goals
    line = f"{meta.home.short_name} {home}-{away} {meta.away.short_name}"
    if decision.kind is Kind.REPLAY and decision.event is not None:
        who = PLAYERS.get(decision.event.player_id or "", "")
        return f"REPLAY {decision.event.type.value} {who} · {line}"
    reasons = []
    for code in decision.chosen.reasons:
        key, _, detail = code.partition(":")
        label = REASON_LABELS.get(key, key)
        detail = PLAYERS.get(detail) or (TEAMS[detail].short_name if detail in TEAMS else detail)
        reasons.append(f"{label} {detail}".strip())
    why = ", ".join(reasons[:3]) or f"drama {decision.chosen.drama:.2f}"
    return f"{decision.kind.value.upper()} → {line} [{decision.trigger.value}] {why}"


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare two fans' channels on one matchday.")
    parser.add_argument("--seed", type=int, default=34)
    parser.add_argument("--fans", nargs=2, default=["arjun", "maya"], choices=sorted(PROFILES))
    args = parser.parse_args()

    matchday = build_matchday(args.seed)
    channels = [run_channel(matchday, PROFILES[name]) for name in args.fans]
    for channel in channels:
        print(f"\n=== {channel.profile.name}'s channel ===")
        for decision in channel.decisions:
            print(f"{decision.t / 60:5.1f}'  {describe(decision, matchday)}")

    print("\n=== Evaluation ===")
    end = max(e.t for e in matchday.events())
    for channel in channels:
        print(f"{channel.profile.name}: {report(matchday, channel).model_dump()}")
    share = distinctness(channels[0], channels[1], end)
    print(f"Distinctness: {share:.0%} of the matchday on different matches")


if __name__ == "__main__":
    main()
