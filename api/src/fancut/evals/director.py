"""The Director measured over several matchdays, for both demo fans.

Pure code and deterministic: the same seeds give the same numbers on any machine.
Definitions live in ``fancut.director.evaluate``; this module pools them.
"""

import time
from collections.abc import Callable, Iterable

from pydantic import BaseModel

from fancut.demo import PROFILES
from fancut.director.evaluate import ChannelReport, distinctness, report, run_channel
from fancut.matchday.matchday import Matchday, build_matchday
from fancut.profile import FanProfile

DEFAULT_SEEDS = (34, 35, 36, 37, 38, 39)


class FanMatchdayReport(BaseModel):
    seed: int
    fan: str
    neutral: bool  # no club: the fan the live-coverage target is defined for
    report: ChannelReport


class MatchdayDistinctness(BaseModel):
    seed: int
    share: float


class DirectorEvaluation(BaseModel):
    seeds: list[int]
    fans: list[str]
    seconds: float  # how long the measurement took
    # Personal coverage, pooled over every fan and matchday. Target 1.0.
    personal_moments: int
    personal_covered: int
    personal_coverage: float
    # Live coverage of decisive goals for neutral fans, pooled over matchdays, against a
    # channel switching at random every three minutes and one that never switches.
    decisive_goals: int
    live_coverage: float
    live_coverage_random: float
    live_coverage_never_switch: float
    # Stability: routine cuts sooner than the minimum dwell. Target 0.
    cuts: int
    early_cuts: int
    # Distinctness between the two fans, per matchday. Target >= 0.5.
    distinctness_min: float
    distinctness_max: float
    distinctness_mean: float
    per_matchday: list[FanMatchdayReport]
    distinctness: list[MatchdayDistinctness]


def measure_director(
    seeds: Iterable[int] = DEFAULT_SEEDS,
    known: Matchday | None = None,
    on_progress: Callable[[int], None] | None = None,
    fans: Iterable[FanProfile] | None = None,
) -> DirectorEvaluation:
    """Run every fan through every matchday and pool the reports.

    ``known`` is a matchday already built (the API's), reused if its seed is listed.
    ``on_progress`` is called with the number of matchdays finished so far.
    """
    started = time.perf_counter()
    seeds = list(seeds)
    profiles = list(fans) if fans is not None else list(PROFILES.values())
    rows: list[FanMatchdayReport] = []
    shares: list[MatchdayDistinctness] = []
    for done, seed in enumerate(seeds, start=1):
        matchday = known if known is not None and known.id == f"md{seed}" else build_matchday(seed)
        channels = [run_channel(matchday, fan) for fan in profiles]
        end = max(e.t for e in matchday.events())
        rows += [
            FanMatchdayReport(
                seed=seed,
                fan=channel.profile.name,
                neutral=channel.profile.club_id is None,
                report=report(matchday, channel),
            )
            for channel in channels
        ]
        if len(channels) >= 2:
            share = distinctness(channels[0], channels[1], end)
            shares.append(MatchdayDistinctness(seed=seed, share=share))
        if on_progress:
            on_progress(done)
    return _pool(seeds, profiles, rows, shares, time.perf_counter() - started)


def _pool(
    seeds: list[int],
    fans: list[FanProfile],
    rows: list[FanMatchdayReport],
    shares: list[MatchdayDistinctness],
    seconds: float,
) -> DirectorEvaluation:
    reports = [r.report for r in rows]
    # Live coverage is defined for a neutral fan; fall back to everyone if none is a demo fan.
    neutral = [r.report for r in rows if r.neutral] or reports
    decisive = sum(r.decisive_goals for r in neutral)
    moments = sum(r.personal_moments for r in reports)
    covered = sum(r.personal_covered for r in reports)
    values = [s.share for s in shares]
    return DirectorEvaluation(
        seeds=seeds,
        fans=[fan.name for fan in fans],
        seconds=round(seconds, 1),
        personal_moments=moments,
        personal_covered=covered,
        personal_coverage=_ratio(covered, moments) if moments else 1.0,
        decisive_goals=decisive,
        live_coverage=_ratio(sum(r.live_goals for r in neutral), decisive),
        live_coverage_random=_ratio(sum(r.live_goals_random for r in neutral), decisive),
        live_coverage_never_switch=_ratio(
            sum(r.live_goals_never_switch for r in neutral), decisive
        ),
        cuts=sum(r.cuts for r in reports),
        early_cuts=sum(r.early_cuts for r in reports),
        distinctness_min=round(min(values), 3) if values else 0.0,
        distinctness_max=round(max(values), 3) if values else 0.0,
        distinctness_mean=round(sum(values) / len(values), 3) if values else 0.0,
        per_matchday=rows,
        distinctness=shares,
    )


def _ratio(part: int, whole: int) -> float:
    return round(part / whole, 4) if whole else 0.0


def markdown(result: DirectorEvaluation) -> str:
    """The headline numbers as a Markdown table, for the README."""
    pct = _pct
    rows = [
        ("Personal coverage", f"{result.personal_covered}/{result.personal_moments}", "100%"),
        (
            "Live coverage (neutral fan)",
            f"{pct(result.live_coverage)} vs {pct(result.live_coverage_random)} random, "
            f"{pct(result.live_coverage_never_switch)} never switch",
            ">= 1.4x random",
        ),
        ("Early cuts", f"{result.early_cuts} of {result.cuts} cuts", "0"),
        (
            "Distinctness (two fans)",
            f"{pct(result.distinctness_min)} to {pct(result.distinctness_max)} "
            f"(mean {pct(result.distinctness_mean)})",
            ">= 50%",
        ),
    ]
    lines = [
        f"Measured on {len(result.seeds)} matchdays (seeds {', '.join(map(str, result.seeds))}) "
        f"for {' and '.join(result.fans)}; {result.decisive_goals} decisive goals.",
        "",
        "| Metric | Result | Target |",
        "|---|---|---|",
    ]
    lines += [f"| {name} | {value} | {target} |" for name, value, target in rows]
    return "\n".join(lines)


def _pct(value: float) -> str:
    return f"{value:.0%}"
