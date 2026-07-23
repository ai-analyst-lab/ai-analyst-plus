---
name: eval
description: Run or orchestrate a held-out analytics gold-suite evaluation from Codex, keeping gold answers blind until grading and writing a run record with accuracy, query similarity, latency, and cost where measurable. Use when users ask to run eval, score the system, check train/test split, or report accuracy on gold cases.
---

# Eval

## Purpose

Evaluate the analyst system against a gold suite by making fresh blind attempts per question, grading only after answers are locked, and producing a self-describing run record.

## When to use

- the user asks to run evals, score the system, run train/test/all, or check accuracy;
- a model/config comparison needs a live gold-suite score;
- a context or metric-definition change needs measured impact;
- the user wants failure-mode analysis from gold cases.

## Workflow

### 1. Parse scope

Support natural language equivalent of:

```text
$eval train
$eval test
$eval all
$eval train --slice N
```

Default to `train`. Treat `test` as held-out: run sparingly and never tune iteratively on its failures.

### 2. Preflight data and driver

Use `helpers.eval_driver.preflight()` when available. If the required warehouse, gold suite path, or eval package is unavailable, fail loudly with setup guidance. Do not grade against a substitute engine unless the eval configuration explicitly supports it.

### 3. Load questions blind

Load only question text and split metadata for analyst runs. Do not expose gold SQL, values, or expected answers to the analyst attempt.

### 4. Run fresh analyst attempts

For each question, run a fresh isolated attempt with normal knowledge bootstrap, active dataset schema, quirks, and metric dictionary. Capture:

- analyst value;
- query used;
- definition source;
- latency;
- cost/tokens when measurable;
- errors.

If true subagent isolation is unavailable, run sequentially and record that limitation.

### 5. Grade after lock

Only after all attempts are saved, call the grading helper to compare against gold and write the run record. Capture accuracy, query similarity, failure modes, latency, and cost/cost-per-correct when available.

### 6. Report and diagnose

Report:

- accuracy `passed/total`;
- average query similarity;
- latency/cost if measured;
- context state;
- top failure modes such as undefined-metric drift, fan-out, wrong filter, wrong grain, or wrong source;
- next fixes for train runs.

For test runs, report the held-out score and caution against tuning on test failures.

## Key contracts preserved from Claude

- `held-out`
- `blind`
- `accuracy`
- `query similarity`
- `helpers.eval_driver`

## Codex adaptation notes

- Use natural language or `$eval` invocation; do not rely on legacy slash-command-only mechanics.
- Prefer repository helpers, available MCP tools, and safe local fallbacks over provider-specific assumptions.
- Never print or commit credentials, tokens, secrets, private workspace content, or user-specific generated artifacts.
- If an external platform/tool is unavailable, state the blocker and offer the closest safe fallback.
