# ADR 7: Hinglish is read aloud as Hindi

**Status:** accepted, 26 Oct 2026

## Context
Hinglish is Hindi written in Latin script. An English voice reading it mispronounces the
Hindi words; a Hindi voice reading Latin script spells them out.

## Decision
On a Hinglish channel the API sends the Hindi reference line as `voice_text` on every cut
and on the recap, and the web app speaks it with the Hindi neural voice. The screen keeps
the Hinglish text.

## Consequences
Spoken Hinglish is Hindi, which is what a Hinglish speaker hears anyway. The spoken line is
the deterministic reference, not the Narrator's rewrite, which keeps it fact-safe without a
second model call.
