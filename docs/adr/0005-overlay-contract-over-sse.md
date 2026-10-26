# ADR 5: A timed, machine-readable overlay contract over server-sent events

**Status:** accepted, 24 Oct 2026

## Context
The challenge is written for a studio: the output should be something a graphics engine
can render, not only our web page. The stream is one-directional and must survive browser
reconnects.

## Decision
`overlay.v1`: typed events (`cut`, `narration`, `action`, `scoreboard`, `table`, `fantasy`,
`focus`, `players`, `end`) with a sequence number and the matchday's elapsed seconds, over
server-sent events. The API documents the contract at `/contract/overlay.v1`. The web app
is one renderer of it and invents nothing.

## Consequences
The Studio's inspector shows exactly what a broadcaster would receive. Reconnects are
handled by sequence numbers. WebSockets were not needed since nothing flows upstream
except the focus request, which is a plain POST.
