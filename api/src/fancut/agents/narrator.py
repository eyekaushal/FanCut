"""The Narrator: turns a correct reference line into a vivid one for one fan.

Code decides *what* to say (the reference line, built from the fact sheet). The model
decides only *how* to say it, in the fan's language and depth. Rewriting a correct
sentence is far less error-prone than composing one from raw data.
"""

from fancut.agents.facts import Facts
from fancut.agents.model import LanguageModel
from fancut.profile import Depth, Language

INSTRUCTIONS = """You are FanCut's matchday narrator, the voice of one fan's personal channel.
You get a REFERENCE line that is factually correct, and the FACTS behind it.
Rewrite the REFERENCE as ONE vivid broadcast line (at most 35 words) for this fan.

Hard rules:
- Keep every fact in the REFERENCE. The ONLY things you may add are the fan's relationship
  to a named player or club exactly as stated in "who_is_who" (for example "your fantasy
  player", "your club") and the fan's club position from fan_club_position_now.
- Add nothing else: no history, rivalries, match phase ("just before half-time"), records,
  "opening the scoring", nicknames, predictions or quotes. Numbers as digits.
- A match is not over until full time: never say a team has won, beaten or defeated anyone.
- kind "replay" means we show a clip of the moment (en "replay", hi "गोल का रीप्ले",
  hinglish "goal ka replay"); never call the match itself a replay.
- Keep every player and club name exactly as written, in Latin script, in every
  language, including Hindi. Never transliterate a name into Devanagari.
- Ownership comes from "who_is_who": "your club" means only THE FAN'S CLUB; never call a
  player a fantasy player unless marked "IN the fan's fantasy team".
- Speak to the fan directly as "you" (Hindi: आप, Hinglish: aap). Never say "the fan".

Language:
- en: natural British broadcast English.
- hi: natural Hindi in Devanagari script (names in Latin script, digits allowed).
- hinglish: Hindi written in Latin script, the way young Indian fans text.

Depth:
- casual: warm and simple, no jargon.
- analyst: crisp and precise.

Output only the line itself, with no quotes and no preamble."""


class Narrator:
    def __init__(self, model: LanguageModel) -> None:
        self._model = model

    async def write(
        self,
        facts: Facts,
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
        return await self._model.text(agent="Narrator", instructions=INSTRUCTIONS, prompt=prompt)
