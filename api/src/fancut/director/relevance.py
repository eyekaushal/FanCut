"""How much a match matters to one fan right now: live drama x personal stake.

Every component is kept, so each cut can explain itself.
"""

from pydantic import BaseModel, ConfigDict

from fancut.matchday.state import MatchdayState, MatchFeed, Status
from fancut.profile import FanProfile
from fancut.sim.schema import Stakes

DRAMA_FLOOR = 0.2  # keeps a fan's own match on air when nothing is happening anywhere
SUSPENSE_WEIGHT = 0.75  # stakes vs current pressure; tuned on six matchdays (126 decisive goals)
STAKE_CAP = 3.0
NEUTRAL_DRAMA = 0.3  # before a match has produced its first snapshot

STAKE = {
    "your_club": 1.5,
    "rival": 0.5,  # a club within three places of yours in the live table
    "followed_player": 0.6,
    "fantasy_player": 0.3,
    "captain": 0.3,  # on top of fantasy_player
}
STAKES_BONUS = {
    Stakes.TITLE_RACE: 0.3,
    Stakes.RELEGATION: 0.3,
    Stakes.TOP_FOUR: 0.15,
    Stakes.DERBY: 0.15,
    Stakes.MID_TABLE: 0.0,
}
RIVAL_DISTANCE = 3


class Relevance(BaseModel):
    model_config = ConfigDict(frozen=True)

    match_id: str
    value: float  # how much this match matters to this fan right now
    minute: int
    goals: tuple[int, int]  # (home, away)
    drama: float
    suspense: float
    pressure: float
    stake: float
    reasons: tuple[str, ...]  # machine-readable, e.g. "your_club", "fantasy_player:ash-09"


def relevance(profile: FanProfile, feed: MatchFeed, state: MatchdayState) -> Relevance:
    snapshot = feed.snapshot
    minute = snapshot.minute if snapshot else 1
    goals = feed.score[2], feed.score[3]
    if feed.status is not Status.LIVE:
        return Relevance(
            match_id=feed.match_id,
            value=0.0,
            minute=minute,
            goals=goals,
            drama=0.0,
            suspense=0.0,
            pressure=0.0,
            stake=0.0,
            reasons=(feed.status.value,),
        )
    suspense = snapshot.suspense if snapshot else NEUTRAL_DRAMA
    pressure = max(snapshot.pressure) if snapshot else NEUTRAL_DRAMA
    drama = SUSPENSE_WEIGHT * suspense + (1 - SUSPENSE_WEIGHT) * pressure

    stake, reasons = _personal_stake(profile, feed, state)
    return Relevance(
        match_id=feed.match_id,
        value=(DRAMA_FLOOR + drama) * (1 + stake),
        minute=minute,
        goals=goals,
        drama=drama,
        suspense=suspense,
        pressure=pressure,
        stake=stake,
        reasons=tuple(reasons),
    )


def _personal_stake(
    profile: FanProfile, feed: MatchFeed, state: MatchdayState
) -> tuple[float, list[str]]:
    stake, reasons = 0.0, []
    teams = feed.team_ids
    if profile.club_id in teams:
        stake += STAKE["your_club"]
        reasons.append("your_club")
    elif profile.club_id is not None:
        positions = state.positions()
        mine = positions[profile.club_id]
        for team in teams:
            if abs(positions[team] - mine) <= RIVAL_DISTANCE:
                stake += STAKE["rival"]
                reasons.append(f"rival:{team}")
                break

    for player_id in sorted(feed.on_pitch):
        if player_id in profile.player_ids:
            stake += STAKE["followed_player"]
            reasons.append(f"followed_player:{player_id}")
        elif player_id in profile.fantasy_squad:
            stake += STAKE["fantasy_player"]
            reasons.append(f"fantasy_player:{player_id}")
        if player_id == profile.captain_id:
            stake += STAKE["captain"]
            reasons.append(f"captain:{player_id}")

    bonus = STAKES_BONUS[feed.match.meta.stakes]
    if bonus:
        stake += bonus
        reasons.append(f"stakes:{feed.match.meta.stakes.value}")
    return min(stake, STAKE_CAP), reasons
