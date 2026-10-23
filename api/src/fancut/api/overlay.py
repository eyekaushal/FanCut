"""The ``overlay.v1`` contract: timed, machine-readable events for any renderer.

Our web app renders them; a broadcaster's graphics engine could render the same stream.
Every event carries ``t``, the matchday's elapsed seconds, so it can be synchronised
with a live feed.
"""

from enum import StrEnum
from typing import Any

from pydantic import BaseModel

SCHEMA_VERSION = "overlay.v1"


class OverlayType(StrEnum):
    CUT = "cut"  # the channel opens on, cuts to or replays a match
    NARRATION = "narration"  # the model-written line for an earlier cut
    ACTION = "action"  # a play in the match on air, for the pitch graphic
    SCOREBOARD = "scoreboard"  # every match: score, minute, status
    TABLE = "table"  # the league table as it stands
    FANTASY = "fantasy"  # the fan's fantasy points
    END = "end"


class Overlay(BaseModel):
    schema_version: str = SCHEMA_VERSION
    seq: int
    t: float
    type: OverlayType
    data: dict[str, Any]


class ScoreLine(BaseModel):
    match_id: str
    home: str
    away: str
    home_short: str
    away_short: str
    home_color: str
    away_color: str
    home_goals: int
    away_goals: int
    minute: int
    status: str
    stakes: str
    on_air: bool


class TableLine(BaseModel):
    position: int
    team_id: str
    team: str
    short: str
    played: int
    points: int
    goal_difference: int
    change: int  # places gained (+) or lost (-) since kickoff
