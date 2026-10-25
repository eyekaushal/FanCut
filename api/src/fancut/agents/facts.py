"""Fact sheets: the only things a narrator is allowed to say.

A fact sheet is built from deterministic state at the moment a decision is made, with
every id resolved to a display name. Field names spell out *whose* fact each one is
("fan_club_position_now", not "position"), because a model fills any ambiguity with a guess.
"""

import json
from typing import Literal, Protocol

from pydantic import BaseModel, ConfigDict

from fancut.director.director import Decision
from fancut.matchday.state import MatchdayState
from fancut.profile import Depth, FanProfile
from fancut.sim.clubs import TEAMS
from fancut.sim.schema import EventType


class Facts(Protocol):
    """What the commentary pipeline needs from any fact sheet."""

    def numbers(self) -> set[int]: ...

    def names(self) -> set[str]: ...

    def required_names(self) -> set[str]:
        """At least one of these must appear verbatim in any narration."""
        ...

    def must_mention(self) -> set[str]:
        """Every one of these must appear verbatim in any narration."""
        ...

    def to_prompt(self) -> str: ...


class Moment(BaseModel):
    model_config = ConfigDict(frozen=True)

    type: Literal["goal", "red_card"]
    player: str
    player_team: str
    minute: int


class CutFacts(BaseModel):
    model_config = ConfigDict(frozen=True)

    kind: Literal["open", "cut", "replay", "live"]
    minute: int
    home_team: str
    away_team: str
    home_goals: int
    away_goals: int
    moment: Moment | None = None
    match_stakes: str = "mid_table"
    fan_club: str | None = None
    fan_club_is_playing_in_this_match: bool = False
    fan_club_table_rival_in_this_match: str | None = None
    players_the_fan_follows_on_pitch: tuple[str, ...] = ()
    fan_fantasy_captain_on_pitch: str | None = None
    fan_fantasy_players_on_pitch: tuple[str, ...] = ()
    fan_club_position_now: int | None = None
    fan_club_position_at_kickoff: int | None = None
    suspense_out_of_10: int | None = None  # analyst fans only
    pressure_out_of_10: int | None = None  # analyst fans only

    def numbers(self) -> set[int]:
        values = {self.minute, self.home_goals, self.away_goals}
        optional = (
            len(self.fan_fantasy_players_on_pitch) or None,
            self.fan_club_position_now,
            self.fan_club_position_at_kickoff,
            self.suspense_out_of_10,
            self.pressure_out_of_10,
            self.moment.minute if self.moment else None,
        )
        values |= {n for n in optional if n is not None}
        if self.suspense_out_of_10 is not None:
            values.add(10)  # "x out of 10"
        return values

    def names(self) -> set[str]:
        values = {self.home_team, self.away_team, *self.players_the_fan_follows_on_pitch}
        values |= set(self.fan_fantasy_players_on_pitch)
        optional = (self.fan_club, self.fan_club_table_rival_in_this_match)
        values |= {n for n in (*optional, self.fan_fantasy_captain_on_pitch) if n}
        if self.moment is not None:
            values |= {self.moment.player, self.moment.player_team}
        return values

    def required_names(self) -> set[str]:
        return {self.home_team, self.away_team}

    def must_mention(self) -> set[str]:
        return {self.moment.player} if self.moment else set()

    def who_is_who(self) -> dict[str, str]:
        """Every name with its exact role for this fan, including what it is NOT."""
        followed = set(self.players_the_fan_follows_on_pitch)
        fantasy = set(self.fan_fantasy_players_on_pitch)
        roles: dict[str, list[str]] = {}
        for team, side in ((self.home_team, "home team"), (self.away_team, "away team")):
            roles[team] = [side]
            if team == self.fan_club:
                roles[team].append("THE FAN'S CLUB")
            elif team == self.fan_club_table_rival_in_this_match:
                roles[team].append("a table rival of the fan's club, NOT the fan's club")
            else:
                roles[team].append("NOT the fan's club")
        for player in sorted(followed | fantasy | self._moment_player()):
            role = ["a player the fan follows" if player in followed else "NOT followed by the fan"]
            role.append(
                "IN the fan's fantasy team"
                if player in fantasy
                else "NOT in the fan's fantasy team"
            )
            if player == self.fan_fantasy_captain_on_pitch:
                role.append("the fan's fantasy captain")
            roles[player] = role
        return {name: "; ".join(parts) for name, parts in roles.items()}

    def _moment_player(self) -> set[str]:
        return {self.moment.player} if self.moment else set()

    def to_prompt(self) -> str:
        sheet = self.model_dump(exclude_defaults=True)
        sheet["who_is_who"] = self.who_is_who()
        return json.dumps(sheet, ensure_ascii=False)


def facts_for(decision: Decision, state: MatchdayState, profile: FanProfile) -> CutFacts:
    """The fact sheet for one Director decision, read from the live state right now."""
    feed = state.feeds[decision.match_id]
    meta = feed.match.meta
    chosen = decision.chosen
    team_names = {team.id: team.name for team in TEAMS.values()}

    followed: list[str] = []
    captain, rival = None, None
    for code in chosen.reasons:
        key, _, detail = code.partition(":")
        if key == "followed_player":
            followed.append(state.players[detail].name)
        elif key == "captain":
            captain = state.players[detail].name
        elif key == "rival":
            rival = team_names[detail]
    fantasy = tuple(state.players[p].name for p in profile.fantasy_squad if p in feed.on_pitch)

    club = profile.club_id
    playing = club is not None and club in feed.team_ids
    table_relevant = playing or rival is not None
    analyst = profile.depth is Depth.ANALYST
    return CutFacts(
        kind=decision.kind.value,
        minute=chosen.minute,
        home_team=meta.home.name,
        away_team=meta.away.name,
        home_goals=chosen.goals[0],
        away_goals=chosen.goals[1],
        moment=_moment(decision, state),
        match_stakes=meta.stakes.value,
        fan_club=team_names[club] if club else None,
        fan_club_is_playing_in_this_match=playing,
        fan_club_table_rival_in_this_match=rival,
        players_the_fan_follows_on_pitch=tuple(followed),
        fan_fantasy_captain_on_pitch=captain,
        fan_fantasy_players_on_pitch=fantasy,
        fan_club_position_now=state.positions()[club] if club and table_relevant else None,
        fan_club_position_at_kickoff=state.table.positions()[club]
        if club and table_relevant
        else None,
        suspense_out_of_10=round(chosen.suspense * 10) if analyst else None,
        pressure_out_of_10=round(chosen.pressure * 10) if analyst else None,
    )


def _moment(decision: Decision, state: MatchdayState) -> Moment | None:
    event = decision.event
    if event is None or event.player_id is None or event.side is None:
        return None
    if event.type is EventType.GOAL:
        kind: Literal["goal", "red_card"] = "goal"
    elif event.type is EventType.CARD:
        kind = "red_card"
    else:
        return None
    team = state.feeds[event.match_id].match.meta.team(event.side)
    return Moment(
        type=kind, player=state.players[event.player_id].name, player_team=team.name,
        minute=event.minute,
    )  # fmt: skip
