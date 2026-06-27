---
name: compare
description: Run a comparison: ask one analytics question two ways, with a piece of context and without it, and measure what changed. Use when the user says "/compare", "run it with and without <the definition/context>", "does adding <X> change the answer", "is this context worth it", or wants to see whether a metric definition (or any context) moves the answer and collapses the drift. This is the context-side companion to /reliability: reliability says stable or drifts under one setup; compare says what changed between two setups.
---

# Skill: Compare (with and without)

## Purpose
Measure what a piece of context is doing, instead of asserting it. Run the same question two ways,
once without the context (for example, no metric definition) and once with it, and report the delta:
did the spread collapse, did the runs start citing the definition, did the verdict go from drifts to
stable. The setup whose presence collapses the drift is the context that moves the answer. Convergence
is stability, not correctness.

## Invocation
`/compare "<the question>" --with <setup_dir> [N]`
Default N = 5. The setup is a directory of meaning-only definition overlays (for example the retention
definition at `.knowledge/comparisons/conditions/c1_retention_contract/`). The baseline is the analyst
with that setup absent.

Example: `/compare "What's our retention rate?" --with .knowledge/comparisons/conditions/c1_retention_contract`

## How to run it

The math and the report live in the standalone eval tool (`~/projects/ai-analytics-evals`). The run
step is the reliability skill. This skill is the glue: stage a setup, run reliability, repeat, compute
the delta, restore. The user never types a command; you do each step.

### Step 1 - baseline (without the context)
Make sure the baseline is active (the context absent). Use the eval tool's adapter to restore the base
dictionary:
```python
import sys; sys.path.insert(0, "<HOME>/projects/ai-analytics-evals")
from aievals.adapters.ai_analyst_plus import AIAnalystPlusAdapter
AIAnalystPlusAdapter().restore()
```
Then run the reliability check on the question (the /reliability skill: fire N independent sub-agents,
each fresh context, each reporting headline / measured / definition_source). Save the N results to a
run directory, for example `.knowledge/comparisons/<question-slug>/<ts>-baseline/runs.json`.

### Step 2 - with the context
Stage the setup, then run the reliability check again into a second run directory:
```python
AIAnalystPlusAdapter().stage("<the setup dir>")   # composes base + the definition overlay
```
Run reliability again into `.../<ts>-with-context/runs.json`.

### Step 3 - compute the delta and report
```python
from aievals.harness.comparison import comparison_delta, write_report
result = comparison_delta([
    {"name": "no-context", "runs_dir": "<baseline run dir>"},
    {"name": "with-context", "runs_dir": "<with-context run dir>"},
])
report = write_report("<an output dir>", "<the question>", result)
```
The numbers are computed deterministically by the eval tool, never estimated.

### Step 4 - restore and report
Always restore the baseline so the analyst is left as it was:
```python
AIAnalystPlusAdapter().restore()
```
Show the user the `comparison_report.md` it produced: the per-setup table (verdict, distinct values,
agreement, how many runs cited the definition) and the delta (verdict change, spread drop, citations
gained, and whether the context moved the answer). Frame it:
- **Moves the answer (DRIFT -> STABLE).** "Without the definition the runs drifted across N readings.
  With it they converged and every run cited it. Same model, same data; the context did that."
- **No change.** "The spread did not move. That context was not the thing the answer needed."

## Notes
- Replace `<HOME>` with the real home path. The eval tool holds no credentials and no data; it reaches
  the analyst only through the adapter.
- A metric is defined by its meaning, never a hardcoded number. No result number is ever written into a
  setup; the analyst computes it from the data each run.
- Stability is not correctness: a wrong query is perfectly stable. Compare tells you what a piece of
  context changed, not whether the answer is right.
- Works the same against local DuckDB or live Snowflake; the warehouse is the analyst's connection.
