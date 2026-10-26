# ADR 4: Code writes the truth; the model rewrites it

**Status:** accepted, 24 Oct 2026

## Context
Narration must be grounded in three languages, two of them with names in Latin script
inside Devanagari or romanised Hindi. Composing sentences from raw facts invites invented
details; verifying free text is hard.

## Decision
For every decision, code builds a fact sheet (every id resolved to a display name, every
field named for whose fact it is) and a correct reference line in the fan's language. The
Narrator may only rewrite the reference line. The Fact Checker runs code rules first (every
number and league name must be in the fact sheet; the right script; a length cap), then a
model judge. Three drafts with feedback, then the reference line airs. The cut goes out
with the reference line immediately; the Narrator's line follows as its own overlay.

## Consequences
The channel never waits for the model and never goes silent. The red team shows the rules
catch every rule-detectable break with no false rejects, and the judge the rest. The cost
is a plainer line when the model is down, which the audit trail records.
