# ADR 6: Neutral surfaces, club colour only, Apple-style motion

**Status:** accepted, 24 Oct 2026

## Context
The earlier design concept (ink navy, amber, a serif) read as a dashboard. The product is
a broadcast, watched on a phone as much as a laptop, often in Hindi.

## Decision
Surfaces are neutral; the only colour on screen belongs to a club. Each match card is a
WebGL silk surface in the two clubs' colours, with a contrast audit in the tests. One type
family (Inter, with Noto Sans Devanagari for Hindi), tabular numbers, hairlines. Springs
are critically damped; a flick earns a bounce; reduced motion is honoured. The cut is the
signature moment: the card leaves left, the next lands from the right, on one spring.

## Consequences
Two fans' channels look different because their matches do, not because of decoration.
The design tokens are generated from one TypeScript file and audited by CI.
