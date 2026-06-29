---
name: compare
description: Compare one analytics question with and without a context or metric-definition overlay, measuring whether the context changes the answer or collapses reliability drift. Use when the user asks to run with/without context, test whether a definition matters, see if context is worth it, or compare answer stability across setups.
---

# Compare

## Purpose

Measure what a piece of context changes. Run the same analytics question in two conditions:
without the context and with the context. Compare reliability results to determine whether
the context moved the answer, collapsed drift, increased metric-definition citation, or had
no effect.

This is the Codex-native counterpart to the legacy Claude compare workflow and is the
context-side companion to `$reliability`.

## Invocation pattern

```text
$compare "<question>" --with <setup_dir> [N]
```

Default `N = 5`. The setup directory should contain meaning-only context such as a metric
definition overlay. It must not contain hardcoded result numbers or conclusions.

Example:

```text
$compare "What's our retention rate?" --with .knowledge/comparisons/conditions/c1_retention_contract 5
```

## Core principle

Compare measures stability and context effect, not correctness. A wrong query can be stable.
The question is: did adding the context change the answer or reduce ambiguity?

## Requirements and blockers

This workflow depends on two capabilities:

1. `$reliability` or equivalent independent repeated runs for each condition.
2. A way to stage and restore context overlays.

The legacy workflow used `~/projects/ai-analytics-evals` and its
`AIAnalystPlusAdapter`. In Codex, use that adapter only if it exists locally. If it is
missing, do not pretend the comparison was automated; either use a repository-native overlay
mechanism if available or stop with instructions to install/provide the eval adapter.

Always restore the baseline context after the comparison, even if a run fails.

## Step 1 — validate setup

1. Parse the question, setup directory, and N.
2. Verify the setup directory exists.
3. Inspect the setup enough to confirm it contains definitions/context, not result numbers.
4. Record the active dataset and current metric dictionary state.
5. Confirm that the staging mechanism is available:

```python
import sys
sys.path.insert(0, "<HOME>/projects/ai-analytics-evals")
from aievals.adapters.ai_analyst_plus import AIAnalystPlusAdapter
```

If unavailable, stop with a clear blocker and do not mutate the metric dictionary manually.

## Step 2 — baseline run without context

Restore the base dictionary/context:

```python
AIAnalystPlusAdapter().restore()
```

Run `$reliability` on the question with N independent runs. Save results under a comparison
run directory, for example:

```text
.knowledge/comparisons/<question-slug>/<UTC-timestamp>-baseline/runs.json
```

The run format should match `$reliability`:

```json
{
  "question": "<question>",
  "runs": [
    {"run": 1, "headline": "...", "measured": "...", "definition_source": "..."}
  ]
}
```

## Step 3 — with-context run

Stage the setup:

```python
AIAnalystPlusAdapter().stage("<setup_dir>")
```

Run `$reliability` again with N independent runs and save to:

```text
.knowledge/comparisons/<question-slug>/<UTC-timestamp>-with-context/runs.json
```

## Step 4 — compute delta deterministically

If the eval harness is available, use it:

```python
from aievals.harness.comparison import comparison_delta, write_report

result = comparison_delta([
    {"name": "no-context", "runs_dir": "<baseline run dir>"},
    {"name": "with-context", "runs_dir": "<with-context run dir>"},
])
report = write_report("<output dir>", "<question>", result)
```

Do not estimate the delta in prose when deterministic tooling is available. If deterministic
tooling is unavailable but both reliability reports exist, state the limitation and compare
only the visible reliability outputs without claiming a full harness-computed delta.

## Step 5 — restore baseline

Always run:

```python
AIAnalystPlusAdapter().restore()
```

If restore fails, treat it as a blocker and tell the user how to restore before continuing
analysis.

## Step 6 — report

Show the generated `comparison_report.md` or a concise equivalent with:

- baseline verdict, distinct values, agreement rate, and definition citations;
- with-context verdict, distinct values, agreement rate, and definition citations;
- spread/drop or agreement-rate change;
- whether the answer moved;
- whether the context collapsed drift;
- artifact paths;
- restore status.

Use this framing:

- **Moves the answer / collapses drift**: without the context, runs drifted; with it, they
  converged and cited the definition. Same model, same data; the context did that.
- **No meaningful change**: spread, verdict, and citations did not materially move. The
  context was not the missing ambiguity.
- **Changed but still drifting**: context affects the answer but does not fully specify the
  metric or data scope; add more precise definitions.

## Safety rules

- Never write result numbers into setup overlays.
- Never permanently save temporary comparison definitions into the active metric dictionary.
- Never leave staged context active after the run.
- Never call repeated answers from one shared context independent.
- Never claim correctness from convergence alone.
