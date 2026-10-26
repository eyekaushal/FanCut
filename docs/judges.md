# Testing FanCut in five minutes

No login, nothing to install. The live site runs until 10 November 2026.

**Live site:** https://ca-web-uqyqafwuy3rta.wittypond-5f858327.westus3.azurecontainerapps.io
**Demo video:** https://youtu.be/QhVRt6taUzo

Each channel plays a whole matchday in about three minutes (30 match seconds per real
second). Add `&speed=120` to any channel URL to watch it in under a minute, or `&speed=10`
to watch it slowly.

## 1. Two fans, one matchday (the centrepiece)

Open **Two fans, side by side** from the landing page (`/split`).

Arjun supports Kingsmere City, runs a fantasy team and reads Hindi; Maya is a neutral
analyst in English. Watch the header count how often they are on different matches. Watch
a replay interrupt Arjun's channel when one of his players scores elsewhere, with the
reason under the score.

## 2. One channel, properly

Open **Watch as Arjun** (`/channel?profile=arjun`).

- The card is the match on air; the line under the score says why, in the fan's language,
  with chips for the reasons. The Narrator's line replaces the reference line a few seconds
  after each cut.
- Switch the language in the header: the channel restarts in English, हिंदी or Hinglish.
- Turn on **Voice** to hear the lines (Azure AI Speech).
- Tap a match in the strip to **focus** on it: the card explains how the Director ranks it
  against the match it chose. Tap "Back to the Director".
- Under the pitch, pick a player in **Player cam**: their plays stay bright, their numbers
  (distance, top speed, passes, xG) update live.
- At full time, the recap appears at the top.

## 3. Describe yourself

Open **Start my channel** (`/start`). Type something like
*"I support Oakbridge Town, my captain is Rohan Mehta, Hinglish please"* in English, Hindi
or Hinglish. The Profile Compiler reads back what it understood and asks about anything
it could not resolve. Start the channel.

## 4. The Studio: why, and how trustworthy

Open **Studio** (`/studio`).

- **Measured**: the Director's numbers over six matchdays, computed by the API when the
  page is first opened (about 30 seconds), next to the red team, the manual grounding
  review and the Foundry evaluator scores, each with its method.
- **Decision log**: every decision with the ranking that made it, the reference line, the
  Narrator's line, and any draft the Fact Checker rejected with its reason. Expand a row
  for the alternatives and the fact sheet. "audit.v1 JSON" opens the raw trail.
- **Overlay inspector**: the raw `overlay.v1` stream a broadcaster's graphics engine would
  consume. Pause it, filter by type, open an event, copy its JSON.
- **Responsible AI**: the controls as built, the Director's rules, which model is speaking.

## 5. The API itself

- `GET /health`: version, whether a model and Speech are configured.
- `GET /contract/overlay.v1`: the overlay contract with every event type described.
- `GET /evaluation`: the measurements as JSON.
- `POST /mcp/`: the Drama Engine's MCP server (`matchday_overview`, `match_drama`,
  `rank_matches`).

## Running it yourself

See the README. Without Azure keys the channel runs end to end on its reference lines;
with a Foundry deployment and a Speech key in `api/.env`, the Narrator, the judge and the
voice switch on. `uv run pytest` runs 134 tests; `npm test` runs 80.
