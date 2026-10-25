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
from collections import Counter
from collections.abc import Iterable
from threading import Lock, Thread
from typing import TYPE_CHECKING, Any, Literal

from pydantic import BaseModel

from fancut.agents.commentary import MAX_DRAFTS, Source
from fancut.agents.fact_checker import MAX_CHARS
from fancut.director.director import (
    ALTERNATIVES_KEPT,
    DECISION_INTERVAL,
    HYSTERESIS,
    MIN_DWELL,
)
from fancut.evals.director import DirectorEvaluation, measure_director
from fancut.evals.redteam import RulesResult, build_cases, run_rules
from fancut.matchday.matchday import Matchday

if TYPE_CHECKING:
    from fancut.api.channel import ChannelSession

log = logging.getLogger(__name__)


class Progress(BaseModel):
    done: int
    total: int


class DirectorMeasurement:
    """Runs the Director evaluation and the red team once, in a worker thread, and
    remembers the results."""

    def __init__(self, seeds: Iterable[int], known: Matchday | None = None) -> None:
        self._seeds = list(seeds)
        self._known = known  # the matchday already built for the demo, reused if listed
        self._lock = Lock()
        self._thread: Thread | None = None
        self._done = 0
        self.result: DirectorEvaluation | None = None
        self.redteam: RulesResult | None = None

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
            if self._known is not None:
                self.redteam = run_rules(build_cases(self._known))
            self.result = measure_director(self._seeds, self._known, self._advance)
        except Exception:  # keep the API up; the screen just stays on "measuring"
            log.exception("the Director measurement failed")

    def _advance(self, done: int) -> None:
        self._done = done


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
    redteam: RulesResult | None  # the code rules over the red-team set, run on this machine


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
    # What `python -m fancut.evals` recorded and committed: director, redteam (with the
    # judge, if it was run), foundry (the evaluators). Absent until someone runs them.
    recorded: dict[str, dict[str, Any] | None]
