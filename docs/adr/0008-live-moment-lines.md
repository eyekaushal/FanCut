# ADR 8: Every goal in the match on screen gets its own line

**Status:** accepted, 26 Oct 2026

## Context
Narration was written only when the Director moved the picture. A goal in the match already
on screen passed in silence, which felt wrong in the live test.

## Decision
A goal or red card in the match on screen that the Director did not just replay or cut to
becomes a `live` decision with the moment, the current score and the fan's facts. It goes
through the same path as a cut: reference line, Narrator, Fact Checker, voice, audit. The
picture does not move.

## Consequences
The Director's own logic and the recorded evaluation are unchanged. The reason card and
the audit trail show a new kind, `live`, and the Fact Checker's instructions did not need
to change.
