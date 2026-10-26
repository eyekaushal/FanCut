# Architecture

FanCut is two services and three contracts. The API (Python, `fancut`) simulates a matchday,
decides what each fan sees and writes what is said. The web app (Next.js) renders the
stream. The contracts between them, and between FanCut and any other renderer, are
`event.v1` (what happened on the pitch), `overlay.v1` (what to show) and `audit.v1` (why).

```
┌────────────────────────────── api (fancut) ──────────────────────────────┐
│                                                                           │
│  sim ──event.v1──► matchday.state ──► drama.engine ×10                    │
│   (league, clubs,     (table, fantasy,     (win probability, suspense,    │
│    archetypes)         on-pitch, players)   pressure, excitement)         │
│                              │                                            │
│                              ▼                                            │
│  profile ──────────► director.relevance ──► director.Director             │
│   (profile.v1,         (drama × stake,        (open, cut, replay,         │
│    Profile Compiler)    reasons kept)          live moment; dwell,        │
│                                                hysteresis, must-show)     │
│                              │                                            │
│                              ▼                                            │
│  agents.facts ──► agents.templates ──► agents.commentary                  │
│   (fact sheet)      (reference line,      (Narrator → Fact Checker,       │
│                      3 languages)          3 drafts, else reference)      │
│                              │                                            │
│                              ▼                                            │
│  api.channel ──overlay.v1 / SSE──► web          api.mcp (/mcp)            │
│  api.app     ──audit.v1, /evaluation, /speech   api.trust, evals          │
└───────────────────────────────────────────────────────────────────────────┘
```

## The matchday (`fancut.sim`, `fancut.matchday`)

A matchday is ten matches from one seed: twenty fictional clubs, a league table after 33
rounds so the title, top-four and relegation races are all alive, fixtures with stakes, and
one simulated match per fixture. Each match is a stream of `event.v1` events (pass, carry,
shot, goal, save, tackle, interception, corner, free kick, foul, card, offside, kick-off,
half-time, full time) with pitch coordinates in metres on a 105 × 68 pitch, home attacking
towards x = 105.

Matches follow *archetypes* (baseline, late comeback, end-to-end, goalless thriller, red
card chaos, early blowout, dead rubber) that shape the simulation and come with a ground
truth: the decisive and dramatic windows the evaluation uses. A calibration test holds 200
baseline matches to real top-flight rates for goals, shots, cards and possession.

`MatchdayState` folds every event into the live table, each fan's fantasy points, who is on
the pitch, and the Drama Engine's latest snapshot per match.

## The Drama Engine (`fancut.drama`)

Per match, from a win-probability model over the score, the clock and the sides'
strengths:

- **Suspense** (Ely, Frankel and Kamenica, 2015): how much the outcome probabilities are
  expected to move over the next five minutes. The forward-looking signal.
- **Surprise**: how far beliefs moved since the last update.
- **Excitement** (Vecer, Ichiba and Laudanovic, 2007): the total variation of the
  probability path so far.
- **Pressure**: each side's current attacking pressure from recent events.

The engine is also an MCP server (`fancut.api.mcp`) with three tools, so another agent or a
studio tool can ask the same questions the Director asks.

## The Director (`fancut.director`)

Pure code, deterministic, explainable. For one fan:

```
relevance = (0.2 + drama) × (1 + stake)
drama     = 0.75 × suspense + 0.25 × pressure
stake     = your club 1.5 | table rival within 3 places 0.5 | followed player 0.6
            | fantasy player 0.3 | captain +0.3 | fixture stakes 0.15–0.3, capped at 3
```

Decisions:

| Kind | When | Picture |
|---|---|---|
| `open` | first event of the matchday | the top-ranked match |
| `cut` | every 10 s of play, if a match is ≥ 15 % more relevant than the one on air and the dwell of 45 s has passed, or the match on air went off (half-time, full time) | moves |
| `replay` + `cut` | a goal or red card involving the fan's club or players, in a match not on air | replay the moment, then move |
| `live` | a goal or red card in the match already on screen | stays; a line is written |

Every decision carries the chosen match's relevance with its reasons and the three best
alternatives it beat. That is the evidence object; it goes out on the cut overlay and into
the audit trail.

## The agents (`fancut.agents`)

Every model call is a Microsoft Agent Framework agent named after its role (Narrator,
FactChecker, ProfileCompiler), through one `LanguageModel` seam, against a Foundry
deployment over the OpenAI v1 API. Tests use a scripted double with the same shape.

- **Fact sheet** (`facts.py`): the only things a narrator may say, built from the live state
  at the moment of the decision with every id resolved to a display name. Field names
  spell out whose fact each one is (`fan_club_position_now`) and a `who_is_who` map states
  each name's exact role for this fan, including what it is *not*.
- **Reference line** (`templates.py`): the correct sentence, written by code in English,
  Hindi (Devanagari) or Hinglish, with names kept in Latin script in every language so
  code can verify them.
- **Narrator**: rewrites the reference line vividly for this fan's language and depth. It
  may add only the fan's relationship to a named player or club and the club's table
  position; nothing else.
- **Fact Checker**: code rules first (every number and league name must be in the fact
  sheet; the right script; a length cap), then a model judge for attribution, ownership,
  positions, invented claims and premature results. Three drafts with feedback, then the
  reference line airs. Any model failure also falls back. The channel never waits for the
  model: the cut goes out with the reference line at once and the Narrator's line follows
  as a `narration` overlay.
- **Profile Compiler**: plain language in any of the three languages to a validated
  `profile.v1`, with a read-back and questions for anything it could not resolve. Without a
  model, deterministic extraction over the club and player names.
- **Recap**: the fan's matchday in a few sentences at full time, through the same loop.

## The stream (`fancut.api.channel`, `overlay.v1`)

A channel is one fan, one matchday, one speed. It replays the merged event stream and emits
overlays over server-sent events: `cut`, `narration`, `action` (plays in the match on
screen), `scoreboard` (every 30 s), `table` (on goals), `fantasy` (on points), `focus`,
`players` (per-player numbers for the match on screen), `end`. Each carries `seq` and the
matchday's elapsed seconds `t`, so a renderer can sync and detect gaps. The contract is
documented by the API itself at `GET /contract/overlay.v1`.

The fan can **focus**: lock the pitch to one match while the Director keeps deciding. The
focus overlay carries the Director's live ranking of that match, so the screen can say why
the Director is elsewhere.

The web app folds overlays into a pure reducer (`channel-state.ts`), holds the picture on a
replay for 2.5 s (`replay-hold.ts`), and resets the store whenever the channel id changes.

## The audit trail (`audit.v1`)

`GET /channels/{id}/audit` returns every decision the channel made: minute, kind, trigger,
from and to, the chosen match's ranking and the alternatives, the fact sheet, the
reference line, and the Narrator's result with every rejected draft's reason, plus the
model deployment and the Director's rules. The Studio renders it as the decision log.

## Trust (`fancut.api.trust`, `fancut.evals`)

`GET /evaluation` measures the Director on six matchdays in a worker thread the first time
it is asked, runs the code rules over the red-team set, tallies what the Fact Checker has
done in this process, and serves the recorded results of `python -m fancut.evals`
(director, red team with the judge, Foundry evaluators). See `evals/README.md`.

## The web app

Next.js 16 App Router, React 19, TypeScript strict, Tailwind v4, Motion. The design is
neutral surfaces with the only colour belonging to a club: each match card is a WebGL
"silk" surface in the two clubs' colours (one shared GL context renders static images per
card), with a WCAG AA contrast audit in the tests. Springs are critically damped; a flick
earns a bounce; reduced motion is honoured. Type is Inter with Noto Sans Devanagari for
Hindi; names stay Latin. The pitch is a 2D canvas that only runs while something is
fading. Interface strings exist in all three languages; the channel's language sets the
screen's.

## Deployment (`infra/`)

Two Container Apps in one environment, a Basic registry pulled through a user-assigned
managed identity, Log Analytics and Application Insights, all from Bicep through `azd up`.
Hostnames are derived in Bicep and injected: the API's own hostname into its MCP
allow-list, the web URL into CORS, the API URL into the web image at build time. Keys are
Container Apps secrets. The API runs as one always-on replica because channels live in
memory for the length of their stream.

## Failure modes

| Failure | What happens |
|---|---|
| No model configured, model slow, model down, rate-limited | The reference line airs; the audit records `template` and the drafts tried |
| A draft fails the rules or the judge | Up to two rewrites with the problems as feedback, then the reference line |
| The browser's stream drops | `EventSource` reconnects; duplicates are dropped by sequence number; an ended stream is not reopened |
| No Speech key | `/speech` answers 503 and the voice switch is not rendered |
| A profile the Compiler could not fully resolve | It asks back; nothing is guessed on the fan's behalf |
