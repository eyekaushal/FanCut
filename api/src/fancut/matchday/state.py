"""Live state of a whole matchday, updated event by event."""

from dataclasses import dataclass, field
from enum import StrEnum

from fancut.drama import DramaEngine, DramaSnapshot
from fancut.matchday.fantasy import FantasyLedger, PointsChange
from fancut.matchday.matchday import Matchday
from fancut.matchday.table import Score
from fancut.sim.schema import Event, EventType, Match, Side


class Status(StrEnum):
    LIVE = "live"
    HALF_TIME = "half_time"
    FULL_TIME = "full_time"


@dataclass
class MatchFeed:
    """One match as the matchday sees it right now."""

    match: Match
    engine: DramaEngine
    status: Status = Status.LIVE
    snapshot: DramaSnapshot | None = None
    goals: dict[Side, int] = field(default_factory=lambda: {Side.HOME: 0, Side.AWAY: 0})
    on_pitch: set[str] = field(default_factory=set)

    @property
    def match_id(self) -> str:
        return self.match.meta.match_id

    @property
    def team_ids(self) -> tuple[str, str]:
        return self.match.meta.home.id, self.match.meta.away.id

    @property
    def score(self) -> Score:
        home, away = self.team_ids
        return home, away, self.goals[Side.HOME], self.goals[Side.AWAY]


@dataclass(frozen=True)
class Update:
    """What one event changed."""

    event: Event
    feed: MatchFeed
    snapshots: list[DramaSnapshot]
    points: list[PointsChange]


class MatchdayState:
    def __init__(self, matchday: Matchday) -> None:
        self.matchday = matchday
        self.table = matchday.table()
        self.feeds = {
            m.meta.match_id: MatchFeed(match=m, engine=DramaEngine(m.meta))
            for m in matchday.matches
        }
        players = {
            p.id: p for m in matchday.matches for t in (m.meta.home, m.meta.away) for p in t.players
        }
        team_of = {
            p.id: t.id
            for m in matchday.matches
            for t in (m.meta.home, m.meta.away)
            for p in t.players
        }
        self.fantasy = FantasyLedger(players, team_of)
        self.players = players
        self.team_of = team_of
        for feed in self.feeds.values():
            for team in (feed.match.meta.home, feed.match.meta.away):
                for player in team.starters:
                    feed.on_pitch.add(player.id)
                    self.fantasy.appear(player.id)

    def update(self, event: Event) -> Update:
        feed = self.feeds[event.match_id]
        snapshots = feed.engine.update(event)
        if snapshots:
            feed.snapshot = snapshots[-1]

        opponent = ""
        if event.side is not None:
            meta = feed.match.meta
            opponent = meta.team(event.side.opponent).id
        points = self.fantasy.update(event, opponent) if event.player_id else []

        if event.type is EventType.GOAL and event.side is not None:
            feed.goals[event.side] += 1
        elif event.type is EventType.SUBSTITUTION and event.player_id:
            feed.on_pitch.discard(str(event.qualifiers.get("player_off", "")))
            feed.on_pitch.add(event.player_id)
        elif event.type is EventType.CARD and event.qualifiers.get("color") == "red":
            feed.on_pitch.discard(event.player_id or "")
        elif event.type is EventType.HALF_TIME:
            feed.status = Status.HALF_TIME
        elif event.type is EventType.KICKOFF and event.period == 2:
            feed.status = Status.LIVE
        elif event.type is EventType.FULL_TIME:
            feed.status = Status.FULL_TIME
        return Update(event=event, feed=feed, snapshots=snapshots, points=points)

    def scores(self) -> tuple[Score, ...]:
        return tuple(feed.score for feed in self.feeds.values())

    def positions(self) -> dict[str, int]:
        """League positions as it stands, live scores included."""
        return self.table.positions(self.scores())
