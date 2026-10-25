"""The matchday recap: one fan's day in a few sentences, from facts the channel recorded.

Built the same way as a cut: code assembles a fact sheet from the final state and the
Director's decisions, writes a correct reference text, and the model only rewrites it,
checked by the Fact Checker. Field names say whose fact each one is.
"""

import json
from typing import Literal

from pydantic import BaseModel, ConfigDict

from fancut.agents.model import LanguageModel
from fancut.director.director import Director, Kind
from fancut.matchday.state import MatchdayState
from fancut.profile import Depth, FanProfile, Language
from fancut.sim.clubs import TEAMS
from fancut.sim.schema import EventType, Side

MAX_RECAP_CHARS = 700

INSTRUCTIONS = """You are FanCut's matchday narrator, closing one fan's personal channel.
You get a REFERENCE recap that is factually correct, and the FACTS behind it.
Rewrite the REFERENCE as a warm, vivid recap of at most 3 sentences and 70 words.

Hard rules:
- Keep every fact in the REFERENCE; add nothing the FACTS do not state. No history,
  predictions, nicknames, quotes or claims about matches not in the FACTS. Numbers as digits.
- Keep every player and club name exactly as written, in Latin script, in every language.
- "Your club" means only the club named fan_club. Speak to the fan as "you".

Language: en = British broadcast English; hi = Hindi in Devanagari (names in Latin);
hinglish = Hindi in Latin script. Depth: casual = warm and simple; analyst = crisp.
Output only the recap, with no quotes and no preamble."""


class RecapMoment(BaseModel):
    model_config = ConfigDict(frozen=True)

    minute: int
    type: Literal["goal", "red_card"]
    player: str
    player_team: str


class RecapFacts(BaseModel):
    """Everything the recap may say, and nothing else."""

    model_config = ConfigDict(frozen=True)

    fan_name: str
    fan_club: str | None = None
    fan_club_opponent: str | None = None
    fan_club_goals: int | None = None
    fan_club_opponent_goals: int | None = None
    fan_club_position_now: int | None = None
    fan_club_position_at_kickoff: int | None = None
    matches_shown: int
    cuts: int
    replays: int
    moments_shown: tuple[RecapMoment, ...] = ()
    fantasy_total: int | None = None
    fantasy_best_player: str | None = None
    fantasy_best_points: int | None = None
    most_dramatic_home_team: str
    most_dramatic_away_team: str
    most_dramatic_home_goals: int
    most_dramatic_away_goals: int
    most_dramatic_excitement_out_of_10: int | None = None  # analyst fans only

    def numbers(self) -> set[int]:
        values = {
            self.matches_shown,
            self.cuts,
            self.replays,
            self.most_dramatic_home_goals,
            self.most_dramatic_away_goals,
        }
        optional = (
            self.fan_club_goals,
            self.fan_club_opponent_goals,
            self.fan_club_position_now,
            self.fan_club_position_at_kickoff,
            self.fantasy_total,
            self.fantasy_best_points,
            self.most_dramatic_excitement_out_of_10,
        )
        values |= {n for n in optional if n is not None}
        values |= {m.minute for m in self.moments_shown}
        if self.most_dramatic_excitement_out_of_10 is not None:
            values.add(10)
        return values

    def names(self) -> set[str]:
        values = {self.most_dramatic_home_team, self.most_dramatic_away_team}
        optional = (self.fan_club, self.fan_club_opponent, self.fantasy_best_player)
        values |= {n for n in optional if n}
        for moment in self.moments_shown:
            values |= {moment.player, moment.player_team}
        return values

    def required_names(self) -> set[str]:
        if self.fan_club:
            return {self.fan_club}
        return {self.most_dramatic_home_team, self.most_dramatic_away_team}

    def must_mention(self) -> set[str]:
        return set()

    def to_prompt(self) -> str:
        sheet = self.model_dump(exclude_defaults=True)
        sheet["who_is_who"] = {self.fan_club: "THE FAN'S CLUB"} if self.fan_club else {}
        return json.dumps(sheet, ensure_ascii=False)


def recap_facts(profile: FanProfile, state: MatchdayState, director: Director) -> RecapFacts:
    """The fact sheet at full time, from the final state and the decisions made."""
    team_names = {team.id: team.name for team in TEAMS.values()}
    cuts = [d for d in director.decisions if d.kind is not Kind.REPLAY]
    replays = [d for d in director.decisions if d.kind is Kind.REPLAY]
    moments = tuple(
        RecapMoment(
            minute=d.event.minute,
            type="goal" if d.event.type is EventType.GOAL else "red_card",
            player=state.players[d.event.player_id].name,
            player_team=state.feeds[d.match_id].match.meta.team(d.event.side).name,
        )
        for d in replays
        if d.event is not None and d.event.player_id and d.event.side
    )

    facts: dict[str, object] = {}
    club = profile.club_id
    if club:
        feed = next(f for f in state.feeds.values() if club in f.team_ids)
        meta = feed.match.meta
        mine, theirs = (Side.HOME, Side.AWAY) if meta.home.id == club else (Side.AWAY, Side.HOME)
        facts |= {
            "fan_club": team_names[club],
            "fan_club_opponent": meta.team(theirs).name,
            "fan_club_goals": feed.goals[mine],
            "fan_club_opponent_goals": feed.goals[theirs],
            "fan_club_position_now": state.positions()[club],
            "fan_club_position_at_kickoff": state.table.positions()[club],
        }

    if profile.fantasy_squad:
        points = {
            p: state.fantasy.points(p) * (2 if p == profile.captain_id else 1)
            for p in profile.fantasy_squad
        }
        best = max(points, key=lambda p: points[p])
        facts |= {
            "fantasy_total": sum(points.values()),
            "fantasy_best_player": state.players[best].name,
            "fantasy_best_points": points[best],
        }

    dramatic = max(state.feeds.values(), key=lambda f: f.snapshot.excitement if f.snapshot else 0.0)
    excitement = dramatic.snapshot.excitement if dramatic.snapshot else 0.0
    return RecapFacts(
        fan_name=profile.name,
        matches_shown=len({d.match_id for d in cuts}),
        cuts=len(cuts),
        replays=len(replays),
        moments_shown=moments,
        most_dramatic_home_team=dramatic.match.meta.home.name,
        most_dramatic_away_team=dramatic.match.meta.away.name,
        most_dramatic_home_goals=dramatic.goals[Side.HOME],
        most_dramatic_away_goals=dramatic.goals[Side.AWAY],
        most_dramatic_excitement_out_of_10=(
            min(10, round(excitement * 10)) if profile.depth is Depth.ANALYST else None
        ),
        **facts,  # type: ignore[arg-type]
    )


class RecapNarrator:
    """Rewrites the reference recap for one fan; the Fact Checker still has the last word."""

    def __init__(self, model: LanguageModel) -> None:
        self._model = model

    async def write(
        self,
        facts: RecapFacts,
        reference: str,
        language: Language,
        depth: Depth,
        feedback: list[str] | None = None,
    ) -> str:
        prompt = (
            f"LANGUAGE: {language.value}\nDEPTH: {depth.value}\n"
            f"REFERENCE: {reference}\nFACTS: {facts.to_prompt()}"
        )
        if feedback:
            prompt += "\nYOUR LAST DRAFT WAS REJECTED BECAUSE: " + "; ".join(feedback)
        return await self._model.text(
            agent="RecapNarrator", instructions=INSTRUCTIONS, prompt=prompt
        )
