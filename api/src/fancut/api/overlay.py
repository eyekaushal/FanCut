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
    FOCUS = "focus"  # the fan locked the picture to a match (or released it)
    PLAYERS = "players"  # per-player numbers for everyone on the pitch in the match shown
    END = "end"


DESCRIPTIONS: dict[OverlayType, str] = {
    OverlayType.CUT: (
        "The channel opens on, cuts to or replays a match. Carries the decision id, the "
        "trigger, the fact sheet, the correct reference line, and the Director's ranking of "
        "the chosen match against the alternatives it beat."
    ),
    OverlayType.NARRATION: (
        "The Narrator's line for an earlier cut, once the Fact Checker has passed it; "
        "the reference line itself when no draft passed or no model is configured."
    ),
    OverlayType.ACTION: (
        "One play in the match on screen, in metres on a 105 x 68 pitch; home attacks "
        "towards x = 105."
    ),
    OverlayType.SCOREBOARD: "Every match: score, minute, status, stakes and which is on air.",
    OverlayType.TABLE: "The league table as it stands, with each club's change since kickoff.",
    OverlayType.FANTASY: "The fan's fantasy points so far, player by player.",
    OverlayType.FOCUS: (
        "The fan locked the picture to one match (or released it), with the Director's "
        "live ranking of that match."
    ),
    OverlayType.PLAYERS: (
        "Per-player numbers for everyone on the pitch in the match shown: passing, "
        "carrying, shooting and speed, all computed in code from the event stream."
    ),
    OverlayType.END: "Full time everywhere; the stream closes after this.",
}

TRANSPORT = (
    "Server-sent events. Each message's `event` is the overlay type, its `id` the "
    "sequence number, its `data` the JSON envelope below. `t` is the matchday's elapsed "
    "seconds; `seq` increases by one per event, so a renderer can detect gaps."
)


class Overlay(BaseModel):
    schema_version: str = SCHEMA_VERSION
    seq: int
    t: float
    type: OverlayType
    data: dict[str, Any]


def contract() -> dict[str, Any]:
    """The contract as a document a broadcaster's graphics team can read or validate against."""
    return {
        "schema_version": SCHEMA_VERSION,
        "transport": TRANSPORT,
        "envelope": Overlay.model_json_schema(),
        "events": [
            {"type": type_.value, "description": DESCRIPTIONS[type_]} for type_ in OverlayType
        ],
    }


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
