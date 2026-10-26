# ADR 2: From "wake me before the moment" to "cut to the match that matters"

**Status:** accepted, 23 Oct 2026

## Context
The project began as Nightkeeper: watch a late-night match and wake the fan *before* the
decisive moment. Measured on the synthetic league, any anticipatory signal was right about
36 % of the time (twice chance, but six wake-ups in ten wasted). A wake-up that is usually
wrong destroys trust, and fact-based wake-ups are a commodity.

## Decision
Keep the engine, change the use. In a personal matchday channel the same signal decides
*which match to show now*. A wrong cut costs thirty seconds, not sleep, and professional
whip-around shows cut on present-state facts the same way.

## Consequences
The Drama Engine, the probability model and the simulator survived unchanged. Everything
fan-facing was rebuilt around the Director and the channel.
