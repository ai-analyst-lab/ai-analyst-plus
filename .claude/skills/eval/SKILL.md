---
name: eval
description: Run the held-out gold suite live against the analyst and score it. Use when the user types "/eval", or asks to "run the eval suite", "score the system", "run the train split", "check the test split", "what's our accuracy on the gold cases", or wants the system-level eval number (accuracy + query-similarity + cost). This DRIVES the analyst on each question (it does not grade hand-supplied answers), keeps the gold blind, and writes a self-describing run record. Pairs with /reliability (stability, no key) and /compare (two configs or two models).
---

# Skill: Eval (live gold-suite runner)

## Purpose
Run the analyst on every question in the held-out gold suite, then score the answers against the
blind gold: accuracy (the analyst's number vs the recomputed gold), query-similarity (its SQL vs the
approved query), and cost/latency. This is the system-level eval — the climb the Context pillar moves
and the number the model comparison turns on.

Two honest properties:
- **Blind by construction.** The analyst runs see the **question only** — never the gold sql or value.
  The gold is read only at grading, after the answers are locked.
- **Real, not staged.** Each answer is produced by actually running the analyst now. Nothing is
  pre-filled.

## Invocation
`/eval [train|test|all] [--slice N]` — default split `train`.
- `train` — the working set you iterate on (error-analyze, add context, watch it climb). Default.
- `test` — the held-out set. Run this ONCE at the end as the honest generalization number. Never
  iterate against it (D8).
- `--slice N` — run only the first N cases (the in-room live slice). Omit for the full split.

Examples: `/eval train` · `/eval train --slice 3` · `/eval test`

## How to run it

### Step 0 — preflight (D3, fail loud)
```python
from helpers.eval_driver import preflight
conn = preflight()   # raises clearly if Snowflake isn't live — there is NO DuckDB fallback
```
If it raises, stop and surface the message. Do not grade against any other engine.

### Step 1 — get the questions (blind)
Load the question set for the split. This returns **questions only** — no answers — so you cannot
leak the key:
```python
import sys; sys.path.insert(0, "<ai-analytics-evals path>")
from aievals.data.gold import load_questions
questions = load_questions("<...>/aievals/data/novamart_gold.yaml", split="train")  # [{question, split}]
```
If `--slice N` was given, take the first N.

### Step 2 — run the analyst once per question
Launch one **fresh sub-agent per question** with the Task/Agent tool (run them concurrently in
reasonable batches). Each sub-agent gets a fresh context and sees ONLY its question. Time each run
(wall-clock) for latency. Give each sub-agent exactly this brief:

> You are answering one analytics question against the active dataset. Load the normal session
> context first (knowledge-bootstrap: `.knowledge/active.yaml`, the active dataset's `schema.md`,
> `quirks.md`, and the metric dictionary `metrics/index.yaml`). If the metric you're asked about is
> defined in the dictionary, use that definition exactly. If it is NOT defined, decide for yourself
> how best to define and measure it. Query the real warehouse with the repo connection
> (`from helpers.connection_manager import ConnectionManager`). Answer the question: "<QUESTION>".
> Return ONLY this block:
> `analyst_value: <the single number you'd report, digits only>`
> `analyst_query: <the exact SQL you ran to get it, one line>`
> `definition_source: <"metric dictionary" if you used a defined metric, else "my own choice">`

The undefined-metric cases are the ones that drift and fail at baseline; they flip to pass once the
definition is added (the C0-C2 climb). That is the point — do not hand the sub-agents definitions
they don't have in the dictionary.

### Step 3 — assemble the per-case results
Build one record per question:
`{"question", "analyst_value", "analyst_query", "latency_ms"}` (add `tokens`/`cost` per case only if
you can measure them honestly; otherwise capture run-level cost in Step 4).

### Step 4 — grade against the blind gold + write the run record
```python
from helpers.eval_driver import grade
record = grade(per_case_results, split="train", out_dir="<...>/aievals/runs",
               conn=conn, model="opus-4.8",
               extra_meta={"changelog": "<one line: what changed since last run>",
                           "total_cost": <run-level $ from ccusage if per-case cost wasn't captured>})
```
`grade` reads the gold (only now), scores accuracy + query-similarity, sums cost/latency, and writes
`<run_id>.json` + `.html` with `git_sha`, `split`, `context_state` (which metrics are defined),
`aggregate`, and per-case detail. Capturing run-level cost: run `npx ccusage@latest session` (or a
fixed window) around the run and pass the total as `total_cost`.

### Step 5 — report
Show the headline from the record: `accuracy = passed/total`, `avg_query_similarity`, and (when
present) `total_cost` / `cost_per_correct` / `avg_latency_ms`. Then:
- Name the **context_state** (how many metrics are defined). The climb is this growing run over run.
- For **train**: "this is your working number — error-analyze the failures (`/cluster-errors` or read
  the run), add the missing definitions, re-run, watch it climb."
- For **test**: "held-out number. If train climbed but this didn't, you overfit. Don't tune on this."
- P14: report the score as what this run produced, not a promised figure. Each student's number
  differs because each builds context at their own pace.

## Model comparison (D22)
To compare engines, run `/eval train` in two sessions — one on Opus 4.8, one on GLM-5.2 (engine
swapped via Ollama cloud, as in the Models pillar) — then put the two run records side by side with
`/compare`. The cell that matters is `cost_per_correct`. Run the comparison on **train** so the
held-out test stays pristine. In the room: a 2-3 case `--slice` live in each terminal + the captured
full runs.

## Notes
- The run record is the same shape the monitor reads (it carries `git_sha` + `changelog`), so a
  sequence of `/eval` runs renders as the trend line in `/monitor`.
- Blind discipline: never paste gold sql/values into a sub-agent's context. If you need to debug a
  failure, read the run record's per-case detail (it shows gold next to analyst for the human), not
  the sub-agent.
