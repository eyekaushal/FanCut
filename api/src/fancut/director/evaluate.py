"""Runs a fan's channel through a whole matchday and measures it.

* **Personal coverage**: the fan's must-show moments (goals and red cards involving their
  club or players) seen live or as an instant replay. Target: 100%.
* **Live coverage**: decisive goals across all ten matches that were on air when they
  happened, compared with switching at random and with never switching.
* **Early cuts**: routine cuts made sooner than the minimum dwell time. Target: 0.
* **Distinctness**: share of the matchday two fans spend watching different matches.
"""

import random
from collections.abc import Callable
from dataclasses import dataclass, field

from pydantic import BaseModel

from fancut.director.director import MIN_DWELL, Decision, Director, Kind, Trigger
from fancut.matchday.matchday import Matchday
from fancut.matchday.state import MatchdayState, Status
from fancut.profile import FanProfile
from fancut.sim.schema import Event, EventType

SAMPLE_SECONDS = 30.0
RANDOM_SWITCH_SECONDS = 180.0

Moment = tuple[str, int]  # (match id, event seq)
Seen = Callable[[Moment], bool]


@dataclass
class Channel:
    """Everything one fan's channel did during a matchday."""

    profile: FanProfile
    decisions: list[Decision] = field(default_factory=list)
    on_air_before: dict[Moment, str | None] = field(default_factory=dict)
    must_show: list[Moment] = field(default_factory=list)

    @property
    def timeline(self) -> list[tuple[float, str]]:
        """(t, match on air from then on), in order."""
        return [(d.t, d.match_id) for d in self.decisions if d.kind is not Kind.REPLAY]

    @property
    def replays(self) -> set[Moment]:
        return {
            (d.match_id, d.event.seq)
            for d in self.decisions
            if d.kind is Kind.REPLAY and d.event is not None
        }

    def on_air_at(self, t: float) -> str | None:
        current = None
        for start, match_id in self.timeline:
            if start > t:
                break
            current = match_id
        return current


class ChannelReport(BaseModel):
    personal_moments: int
    personal_coverage: float
    decisive_goals: int
    live_coverage: float
    live_coverage_random: float
    live_coverage_never_switch: float
    cuts: int
    replays: int
    early_cuts: int


def run_channel(matchday: Matchday, profile: FanProfile) -> Channel:
    state = MatchdayState(matchday)
    director = Director(profile)
    channel = Channel(profile=profile)
    for event in matchday.events():
        if _is_moment(event):
            channel.on_air_before[(event.match_id, event.seq)] = director.on_air
        update = state.update(event)
        if _is_moment(event) and director.is_must_show(event, update.feed):
            channel.must_show.append((event.match_id, event.seq))
        director.observe(update, state)
    channel.decisions = director.decisions
    return channel


def report(matchday: Matchday, channel: Channel, seed: int = 7) -> ChannelReport:
    covered = [
        m for m in channel.must_show if channel.on_air_before[m] == m[0] or m in channel.replays
    ]
    decisive = _decisive_goals(matchday)
    first_pick = channel.timeline[0][1] if channel.timeline else None
    random_channel = _random_channel(matchday, seed)
    return ChannelReport(
        personal_moments=len(channel.must_show),
        personal_coverage=len(covered) / len(channel.must_show) if channel.must_show else 1.0,
        decisive_goals=len(decisive),
        live_coverage=_share(decisive, lambda m: channel.on_air_before.get(m) == m[0]),
        live_coverage_random=_share(decisive, lambda m: random_channel.get(m) == m[0]),
        live_coverage_never_switch=_share(decisive, lambda m: first_pick == m[0]),
        cuts=sum(d.kind is Kind.CUT for d in channel.decisions),
        replays=len(channel.replays),
        early_cuts=_early_cuts(channel.decisions),
    )


def distinctness(a: Channel, b: Channel, end_t: float) -> float:
    samples = [i * SAMPLE_SECONDS for i in range(int(end_t // SAMPLE_SECONDS))]
    if not samples:
        return 0.0
    return sum(a.on_air_at(t) != b.on_air_at(t) for t in samples) / len(samples)


def _is_moment(event: Event) -> bool:
    return event.type is EventType.GOAL or (
        event.type is EventType.CARD and event.qualifiers.get("color") == "red"
    )


def _early_cuts(decisions: list[Decision]) -> int:
    early, previous = 0, None
    for d in decisions:
        if d.kind is Kind.REPLAY:
            continue
        if d.trigger is Trigger.RELEVANCE and previous is not None and d.t - previous < MIN_DWELL:
            early += 1
        previous = d.t
    return early


def _decisive_goals(matchday: Matchday) -> list[Moment]:
    moments = []
    for match in matchday.matches:
        times = {w.end_t for w in match.truth.decisive_windows}
        moments += [
            (match.meta.match_id, e.seq)
            for e in match.events
            if e.type is EventType.GOAL and e.t in times
        ]
    return moments


def _share(moments: list[Moment], seen: Seen) -> float:
    return sum(seen(m) for m in moments) / len(moments) if moments else 0.0


def _random_channel(matchday: Matchday, seed: int) -> dict[Moment, str | None]:
    """What a channel jumping to a random live match every three minutes had on air."""
    rng = random.Random(seed)
    state = MatchdayState(matchday)
    on_air: str | None = None
    next_switch = 0.0
    seen: dict[Moment, str | None] = {}
    for event in matchday.events():
        if event.t >= next_switch:
            live = [f.match_id for f in state.feeds.values() if f.status is Status.LIVE]
            on_air = rng.choice(live) if live else on_air
            next_switch = event.t + RANDOM_SWITCH_SECONDS
        seen[(event.match_id, event.seq)] = on_air
        state.update(event)
    return seen
