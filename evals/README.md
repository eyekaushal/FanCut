# Evaluations

Three measurements, each reproducible from a command, each recorded as JSON in
[`api/src/fancut/evals/results/`](../api/src/fancut/evals/results/) where the API serves
it on `GET /evaluation` and the Studio's Trust screen shows it.

| Command (from `api/`) | Measures | Needs |
|---|---|---|
| `uv run python -m fancut.evals director` | The Director over six matchdays, both demo fans | nothing: deterministic |
| `uv run python -m fancut.evals redteam` | The Fact Checker's code rules over 588 wrong lines | nothing |
| `uv run python -m fancut.evals redteam --judge` | …and the language-model judge over the rest | a Foundry model (`NK_LLM_*`) |
| `uv run python -m fancut.evals foundry` | The Narrator's lines scored by Foundry's evaluators | a model and `uv sync --group evals` |

## The Director (recorded 25 Oct 2026)

Measured on 6 matchdays (seeds 34 to 39) for Arjun and Maya; 122 decisive goals.
Definitions are in [`api/src/fancut/director/evaluate.py`](../api/src/fancut/director/evaluate.py).

| Metric | Result | Target |
|---|---|---|
| Personal coverage: the fan's own goals and red cards seen live or replayed | 58/58 | 100% |
| Live coverage: decisive goals on air for a neutral fan | 19%, against 11% switching at random and 12% never switching | ≥ 1.4× random |
| Early cuts: routine cuts sooner than the 45 s dwell | 0 of 212 cuts | 0 |
| Distinctness: share of the matchday two fans spend on different matches | 60% to 91%, mean 77% | ≥ 50% |

## Grounding

**Red team (recorded 25 Oct 2026, rules only).** 588 lines in three languages, built
from real fact sheets of the demo matchday: 54 truthful controls and 534 broken in one
of eleven known ways. The code rules caught **372 of 372** rule-detectable breaks (wrong
score, wrong minute, a player or club not in the facts, missing team names, the wrong
script, too long) with **0 false rejects**. The other 162 (right names but the wrong
team, a result declared before full time, invented history, a club called "yours" that
is not) can only be caught by the judge: run `--judge` with a model to record that.

**Manual review (24 Oct 2026).** 76 model-written lines from live channels, three
languages, each read against its fact sheet and reference line: 0 false claims,
1 addition that was true but not in the fact sheet.

**Foundry evaluators.** `python -m fancut.evals foundry` narrates the demo matchday with
the model and scores every line the Fact Checker passed with the Azure AI Evaluation
SDK: groundedness against the fact sheet, relevance, coherence and fluency (1 to 5),
and, with `--safety <Foundry project endpoint>`, the content-safety evaluators. The
result is written to `results/foundry.json` and appears on the Trust screen.

## What is not measured here

Latency (event to cut decision) and frame rate are observed during the demo, not
recorded by these commands. The Profile Compiler has unit tests, not an evaluation set.
