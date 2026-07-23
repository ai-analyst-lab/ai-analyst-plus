---
name: reliability
description: Check whether an analytics answer is stable by running the same question several independent times and computing deterministic agreement/drift statistics. Use when the user asks if an answer is reliable/stable, to run a question multiple times, compare repeated answers, trust a number, or invokes $reliability.
---

# Reliability Check

## Purpose

Run one analytics question several independent times and determine whether the reported
answer is stable or drifting. Stability is necessary, not sufficient: a wrong query can be
perfectly stable. This check needs no answer key and measures consistency, not correctness.

This is the Codex-native counterpart to the legacy Claude reliability workflow.

## Invocation pattern

```text
$reliability "<analytics question>" [N]
```

Default `N = 5` unless the user specifies another count. Keep `N` small unless the user asks
for more, because each run may query real data.

## Required independence standard

The repeated runs must be genuinely independent:

- each run sees only the question and normal dataset context;
- no run sees another run’s SQL, result, assumptions, or conclusion;
- do not sequentially “revise” one answer and call it independent;
- do not reuse cached model reasoning as if it were a fresh run.

If this Codex environment cannot spawn fresh subagents/sessions, do not fake independence.
Instead, create the run directory and brief, then give the user clear instructions to run the
brief in fresh Codex sessions and paste/save the results into `runs.json`.

## Step 1 — prepare the independent-run brief

Resolve the active dataset context each independent run should load:

- `.knowledge/active.yaml`;
- `.knowledge/datasets/{active}/schema.md`;
- `.knowledge/datasets/{active}/quirks.md` if present;
- `.knowledge/datasets/{active}/metrics/index.yaml` if present.

Each independent run should receive only this instruction shape:

```text
You are answering one analytics question against the active dataset. Load the normal session
context first: `.knowledge/active.yaml`, the active dataset's `schema.md`, `quirks.md`, and
metrics index. If the metric is defined in the dictionary, use that definition exactly. If it
is not defined, independently choose the best defensible definition. Query the real data with
`helpers.connection_manager.ConnectionManager` when needed.

Answer this question: "<QUESTION>"

Return only:
headline: <the single number or short answer you'd report>
measured: <one line: numerator, denominator, grain, window, filters, and source tables>
definition_source: <"metric dictionary" if used, else "my own choice">
```

## Step 2 — run N independent attempts

Preferred: launch N fresh Codex subagents/sessions when the environment supports it.

Fallback: ask the user to run N fresh sessions manually using the brief. Stop after creating
instructions rather than having the same context answer repeatedly.

## Step 3 — record the runs

Create a timestamped directory:

```text
.knowledge/reliability/<UTC-timestamp>-<question-slug>/
```

Write `runs.json` shaped exactly as:

```json
{
  "question": "<the question>",
  "runs": [
    {
      "run": 1,
      "headline": "25.3%",
      "measured": "numerator, denominator, grain, window, filters",
      "definition_source": "metric dictionary"
    }
  ]
}
```

## Step 4 — compute statistics deterministically

Run the helper; do not estimate these statistics in prose:

```bash
python3 helpers/reliability_stats.py .knowledge/reliability/<UTC-timestamp>-<question-slug>
```

The helper writes:

- `stats.json`;
- `report.md`;
- one audit line to `.knowledge/reliability/log.jsonl`.

It computes distinct values, min/max/range, mean, standard deviation, CV, agreement count,
agreement rate, dictionary usage, and `STABLE`/`DRIFT`/`UNKNOWN` verdict.

## Step 5 — report to the user

Show the generated `report.md` summary, including:

- the run table;
- verdict;
- distinct values;
- agreement rate;
- CV and range when numeric;
- saved run directory and audit log path.

Use this framing:

- **STABLE** — the same answer appeared every run or varied only within the helper’s
  tolerance. The result is consistent, but still not guaranteed correct.
- **DRIFT** — runs chose materially different readings or definitions. Define the metric,
  denominator, window, and filters before trusting any single number.
- **UNKNOWN** — the helper could not parse enough numeric headlines. Review run outputs or
  adapt the question/answer shape.

## Notes and cautions

- The fix for drift is usually context, not a smarter model: define the metric with
  `$metric-spec`, then rerun reliability.
- Do not permanently save temporary comparison definitions into the metric dictionary when
  running with/without comparisons; use an overlay/staging mechanism instead.
- Query real data only through repository connection helpers and log queries when the broader
  analysis workflow requires query logging.
- Keep credentials out of run artifacts.
