# ADR 1: A synthetic league with labelled matches

**Status:** accepted, 21 Oct 2026

## Context
The hackathon forbids real match data, footage, names and marks, and ships no dataset. We
need a whole matchday of football-realistic events, repeatable from a seed, with ground
truth to evaluate against.

## Decision
Twenty fictional clubs with fictional players. A match simulator driven by *archetypes*
(baseline, late comeback, end-to-end, goalless thriller, red card chaos, early blowout,
dead rubber) that emit `event.v1` events with pitch coordinates and carry a ground truth:
the decisive and dramatic windows. A matchday is ten matches from one seed. A calibration
test holds 200 baseline matches to real top-flight rates.

## Consequences
Every number in the product is reproducible and every evaluation has a ground truth.
Real-data adapters for `event.v1` are roadmap work, not a rewrite.
