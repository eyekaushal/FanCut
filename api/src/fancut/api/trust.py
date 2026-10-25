"""What the Studio's Trust screen shows, and where each number comes from.

* The **Director** is measured here, on this machine, by running both demo fans through
  several whole matchdays (``fancut.director.evaluate``). It takes a few seconds, so it
  runs once in a worker thread the first time it is asked for and is kept.
* The **Fact Checker tally** is counted from the channels this process has actually run:
  how many lines the model wrote, how many drafts it took, and why drafts were rejected.
* The **grounding review** is a recorded manual measurement, dated and labelled as such.
* The **safety** section states the controls as they are built, nothing more.
"""

import logging
import time
from collections import Counter
from collections.abc import Iterable
from threading import Lock, Thread
from typing import TYPE_CHECKING, Literal

from pydantic import BaseModel

from fancut.agents.commentary import MAX_DRAFTS, Source
from fancut.agents.fact_checker import MAX_CHARS
from fancut.demo import PROFILES
from fancut.director.director import (
    ALTERNATIVES_KEPT,
    DECISION_INTERVAL,
    HYSTERESIS,
    MIN_DWELL,
)
from fancut.director.evaluate import ChannelReport, distinctness, report, run_channel
from fancut.matchday.matchday import Matchday, build_matchday
from fancut.profile import FanProfile

if TYPE_CHECKING:
    from fancut.api.channel import ChannelSession

log = logging.getLogger(__name__)


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


class Progress(BaseModel):
    done: int
    total: int


class DirectorMeasurement:
    """Runs the Director evaluation once, in a worker thread, and remembers the result."""

    def __init__(self, seeds: Iterable[int], known: Matchday | None = None) -> None:
        self._seeds = list(seeds)
        self._known = known  # the matchday already built for the demo, reused if listed
        self._lock = Lock()
        self._thread: Thread | None = None
        self._done = 0
        self.result: DirectorEvaluation | None = None

    @property
    def progress(self) -> Progress:
        return Progress(done=self._done, total=len(self._seeds))

    def start(self) -> None:
        """Kick off the measurement if it is not running or finished already."""
        with self._lock:
            if self._thread is None:
                self._thread = Thread(target=self._run, name="director-measurement", daemon=True)
                self._thread.start()

    def _run(self) -> None:
        try:
            self.result = self._measure()
        except Exception:  # keep the API up; the screen just stays on "measuring"
            log.exception("the Director measurement failed")

    def _measure(self) -> DirectorEvaluation:
        started = time.perf_counter()
        fans = list(PROFILES.values())
        rows: list[FanMatchdayReport] = []
        shares: list[MatchdayDistinctness] = []
        for seed in self._seeds:
            known = self._known
            matchday = (
                known if known is not None and known.id == f"md{seed}" else build_matchday(seed)
            )
            channels = [run_channel(matchday, fan) for fan in fans]
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
            self._done += 1
        return _pool(self._seeds, fans, rows, shares, time.perf_counter() - started)


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


# -- grounding -------------------------------------------------------------------------


class GroundingReview(BaseModel):
    """A dated manual review of model-written lines against their fact sheets."""

    method: str
    date: str
    lines: int
    languages: int
    false_claims: int
    unsupported_additions: int  # true, but not in the fact sheet
    target: float  # share of lines whose facts match the evidence


MANUAL_REVIEW = GroundingReview(
    method=(
        "Manual review of every model-written line from live channels against its fact "
        "sheet and reference line, in all three languages."
    ),
    date="2026-10-24",
    lines=76,
    languages=3,
    false_claims=0,
    unsupported_additions=1,
    target=0.98,
)


class Rejection(BaseModel):
    problem: str
    count: int


class FactCheckTally(BaseModel):
    """What the Fact Checker has done in this process, counted from the audit trails."""

    channels: int
    lines: int  # narrated decisions
    model: int  # lines the model wrote and the checker passed
    template: int  # lines where the reference line aired
    drafts: int  # model drafts written in all
    rejected_drafts: int
    rejections: list[Rejection]  # the most common reasons, as the checker phrased them


def fact_check_tally(sessions: Iterable["ChannelSession"]) -> FactCheckTally:
    lines = model = template = drafts = 0
    reasons: Counter[str] = Counter()
    channels = 0
    for session in sessions:
        channels += 1
        for entry in session.audit:
            narration = entry.narration
            if narration is None:
                continue
            lines += 1
            drafts += narration.drafts
            model += narration.source is Source.MODEL
            template += narration.source is Source.TEMPLATE
            reasons.update(narration.rejected)
    return FactCheckTally(
        channels=channels,
        lines=lines,
        model=model,
        template=template,
        drafts=drafts,
        rejected_drafts=sum(reasons.values()),
        rejections=[Rejection(problem=p, count=c) for p, c in reasons.most_common(8)],
    )


class Grounding(BaseModel):
    review: GroundingReview
    automated: str
    live: FactCheckTally


# -- safety ------------------------------------------------------------------------------


class Control(BaseModel):
    name: str
    detail: str


class DirectorRules(BaseModel):
    min_dwell_s: float = MIN_DWELL
    hysteresis: float = HYSTERESIS
    decision_interval_s: float = DECISION_INTERVAL
    alternatives_kept: int = ALTERNATIVES_KEPT


class Safety(BaseModel):
    model_deployment: str | None  # null when the deterministic templates are speaking
    speech: bool
    director: DirectorRules
    controls: list[Control]


CONTROLS = [
    Control(
        name="The Director is code",
        detail=(
            "No language model chooses the match. Relevance is drama times personal stake, "
            "computed from the live state, and every decision keeps the alternatives it beat."
        ),
    ),
    Control(
        name="Rules before any judge",
        detail=(
            "Every number in a line must appear in its fact sheet; every league name must "
            "be in it; Hindi must be written in Devanagari and the other two languages must "
            f"not; a line is at most {MAX_CHARS} characters."
        ),
    ),
    Control(
        name="A second agent judges",
        detail=(
            "A Fact Checker agent compares the draft with the fact sheet and the reference "
            "line: who scored and for whom, whose club is whose, league positions, and any "
            "claim the facts do not support."
        ),
    ),
    Control(
        name="Three drafts, then the truth",
        detail=(
            f"The Narrator gets {MAX_DRAFTS} drafts with the checker's feedback. If none "
            "passes, or the model is slow or down, the code-written reference line airs. "
            "The channel never goes silent and never waits for the model."
        ),
    ),
    Control(
        name="Every call is traced",
        detail=(
            "Narrator, Fact Checker and Profile Compiler calls are OpenTelemetry spans "
            "named after the agent: console locally, Application Insights in Azure."
        ),
    ),
    Control(
        name="Synthetic data only",
        detail=(
            "Twenty fictional clubs, fictional players and simulated matches. No real match "
            "data, footage, names or marks are used anywhere."
        ),
    ),
]


class Evaluation(BaseModel):
    status: Literal["measuring", "ready"]
    progress: Progress
    director: DirectorEvaluation | None
    grounding: Grounding
    safety: Safety
