# ADR 3: The Director is code, not a model

**Status:** accepted, 23 Oct 2026

## Context
Which match a fan sees is the product's central decision. It has to be explainable,
reproducible, fast (under a second) and cheap (thousands of decisions per matchday).

## Decision
Relevance is drama × personal stake, computed from live state. The Director re-ranks every
ten seconds of play with a 45 s dwell and a 15 % hysteresis, interrupts for must-show
moments, and keeps the alternatives it beat on every decision. No language model is
involved.

## Consequences
Every cut has an evidence object and an audit entry. The Director can be measured offline
(`python -m fancut.evals director`) and its numbers are the same on every machine. The
model's job is reduced to saying things well, where a mistake is caught by the Fact
Checker rather than shown on screen.
