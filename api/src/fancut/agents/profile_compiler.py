"""The Profile Compiler: "I support Kingsmere, Mehta is my captain, Hinglish please"
-> a validated ``profile.v1``, read back to the fan in their own language.

The model only extracts what the fan said, as written. Code then resolves every name
against the league (fuzzy, so small typos still match) and asks back about anything it
cannot resolve unambiguously. Nothing is guessed.
"""

import difflib
import re
from typing import Literal

from pydantic import BaseModel

from fancut.agents.model import LanguageModel
from fancut.profile import Depth, FanProfile, Language
from fancut.sim.clubs import TEAMS

MATCH_CUTOFF = 0.8
_DEVANAGARI = re.compile("[\u0900-\u097f]")

INSTRUCTIONS = """You turn a football fan's message into profile fields for FanCut, a personal
matchday channel. Extract only what the fan actually said; never guess or fill gaps.
- club: the club they support, as written, or null.
- players: players they want to follow, as written.
- fantasy_players: players in their fantasy team, as written (include the captain).
- captain: their fantasy captain, as written, or null.
- language: "en", "hi" (Hindi in Devanagari) or "hinglish" (Hindi in Latin script).
  Use the language they ask for; otherwise the language they wrote in.
- depth: "analyst" if they want stats or tactics, "casual" if they want it simple, else null.
- name: their first name if they gave it, else null."""


class ProfileDraft(BaseModel):
    name: str | None = None
    club: str | None = None
    players: list[str] = []
    fantasy_players: list[str] = []
    captain: str | None = None
    language: Literal["en", "hi", "hinglish"] | None = None
    depth: Literal["casual", "analyst"] | None = None


class CompiledProfile(BaseModel):
    profile: FanProfile
    readback: str
    questions: list[str]


class _League:
    """Name lookup over the fictional league."""

    def __init__(self) -> None:
        self.clubs = {t.name.lower(): t.id for t in TEAMS.values()}
        self.clubs |= {t.short_name.lower(): t.id for t in TEAMS.values()}
        self.clubs |= {t.name.split()[0].lower(): t.id for t in TEAMS.values()}  # "Kingsmere"
        self.players = {p.name.lower(): p.id for t in TEAMS.values() for p in t.players}
        self.player_names = {p.id: p.name for t in TEAMS.values() for p in t.players}
        self.club_names = {t.id: t.name for t in TEAMS.values()}

    def club(self, written: str) -> str | None:
        return _closest(written, self.clubs)

    def player(self, written: str) -> str | None:
        return _closest(written, self.players)


def _closest(written: str, index: dict[str, str]) -> str | None:
    match = difflib.get_close_matches(written.lower().strip(), index, n=1, cutoff=MATCH_CUTOFF)
    return index[match[0]] if match else None


LEAGUE = _League()


class ProfileCompiler:
    def __init__(self, model: LanguageModel | None) -> None:
        self._model = model

    async def compile(self, message: str) -> CompiledProfile:
        if self._model is None:
            draft = _extract_without_model(message)
        else:
            draft = await self._model.structured(
                agent="ProfileCompiler", instructions=INSTRUCTIONS, prompt=message,
                schema=ProfileDraft,
            )  # fmt: skip
        return resolve(draft, message)


def resolve(draft: ProfileDraft, message: str) -> CompiledProfile:
    questions: list[str] = []
    club = None
    if draft.club:
        club = LEAGUE.club(draft.club)
        if club is None:
            questions.append(f"Which club did you mean by '{draft.club}'?")

    def players(written: list[str]) -> list[str]:
        found = []
        for name in written:
            player = LEAGUE.player(name)
            if player is None:
                questions.append(f"Which player did you mean by '{name}'?")
            elif player not in found:
                found.append(player)
        return found

    followed = players(draft.players)
    fantasy = players(draft.fantasy_players)
    captain = LEAGUE.player(draft.captain) if draft.captain else None
    if captain is not None and captain not in fantasy:
        fantasy.append(captain)  # a captain is always in the squad

    language = Language(draft.language) if draft.language else _language_of(message)
    profile = FanProfile(
        name=draft.name or "Fan",
        club_id=club,
        player_ids=tuple(followed),
        fantasy_squad=tuple(fantasy[:15]),
        captain_id=captain,
        language=language,
        depth=Depth(draft.depth) if draft.depth else Depth.CASUAL,
    )
    return CompiledProfile(profile=profile, readback=readback(profile), questions=questions)


def _language_of(message: str) -> Language:
    return Language.HINDI if _DEVANAGARI.search(message) else Language.ENGLISH


def _extract_without_model(message: str) -> ProfileDraft:
    """Offline fallback: pick up club and player names written in full."""
    lowered = message.lower()
    club = next((t.name for t in TEAMS.values() if t.name.lower() in lowered), None)
    named = [n for n in LEAGUE.player_names.values() if n.lower() in lowered]
    return ProfileDraft(club=club, players=named)


_READBACK = {
    Language.ENGLISH: {
        "club": "You support {club}.", "follow": "You follow {players}.",
        "fantasy": "Your fantasy team has {n} players{captain}.", "captain": ", captain {name}",
        "style": "Commentary in English, {depth} style.", "neutral": "No club yet: we'll follow the drama.",
    },
    Language.HINDI: {
        "club": "आप {club} के फ़ैन हैं।", "follow": "आप {players} को फ़ॉलो करते हैं।",
        "fantasy": "आपकी फ़ैंटेसी टीम में {n} खिलाड़ी हैं{captain}।", "captain": ", कप्तान {name}",
        "style": "कमेंट्री हिंदी में, {depth} अंदाज़ में।", "neutral": "कोई क्लब नहीं चुना: हम सबसे रोमांचक मैच दिखाएँगे।",
    },
    Language.HINGLISH: {
        "club": "Aap {club} ke fan ho.", "follow": "Aap {players} ko follow karte ho.",
        "fantasy": "Aapki fantasy team mein {n} players hain{captain}.", "captain": ", captain {name}",
        "style": "Commentary Hinglish mein, {depth} style.", "neutral": "Koi club nahi chuna: hum sabse dhamakedaar match dikhayenge.",
    },
}  # fmt: skip
_DEPTH_WORDS = {
    Language.ENGLISH: {Depth.CASUAL: "casual", Depth.ANALYST: "analyst"},
    Language.HINDI: {Depth.CASUAL: "आसान", Depth.ANALYST: "विश्लेषक"},
    Language.HINGLISH: {Depth.CASUAL: "simple", Depth.ANALYST: "analyst"},
}


def readback(profile: FanProfile) -> str:
    """Deterministic confirmation of exactly what was understood, in the fan's language."""
    words = _READBACK[profile.language]
    parts = []
    if profile.club_id:
        parts.append(words["club"].format(club=LEAGUE.club_names[profile.club_id]))
    else:
        parts.append(words["neutral"])
    if profile.player_ids:
        names = ", ".join(LEAGUE.player_names[p] for p in profile.player_ids)
        parts.append(words["follow"].format(players=names))
    if profile.fantasy_squad:
        captain = (
            words["captain"].format(name=LEAGUE.player_names[profile.captain_id])
            if profile.captain_id
            else ""
        )
        parts.append(words["fantasy"].format(n=len(profile.fantasy_squad), captain=captain))
    parts.append(words["style"].format(depth=_DEPTH_WORDS[profile.language][profile.depth]))
    return " ".join(parts)
