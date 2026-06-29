---
name: resume-pipeline
description: Resume an interrupted or paused Codex analysis pipeline from saved state or artifacts. Use when the user asks to continue, resume, pick up where they left off, finish an incomplete analysis, recover a failed pipeline, or when pipeline state exists and the user references prior work.
---

# Resume Pipeline

## Purpose

Resume interrupted pipeline work without starting from scratch. Recover from
`working/latest/pipeline_state.json`, `working/runs/{id}/pipeline_state.json`, legacy
`working/pipeline_state.json`, or consistent artifacts when state is missing.

This is the Codex-native counterpart to the legacy Claude resume-pipeline workflow.

## Step 0 — validate request against artifacts first

Before deep state reconstruction, compare the user's requested topic with available artifact
topics.

1. Extract topic keywords from the user request.
2. Quickly scan recent `outputs/question_brief_*.md`, `outputs/narrative_*.md`, and
   `outputs/analysis_*.md` files.
3. If artifacts are clearly about a different topic, stop and surface the mismatch:

```text
I found pipeline artifacts, but they appear to be about [actual topic], not [requested topic].

What I found: [one-sentence summary]
What you asked for: [request]

Options:
1. Resume the [actual topic] analysis.
2. Start a new [requested topic] analysis.
3. Search other runs for matching work.
```

Do not proceed until the user chooses.

## Step 1 — locate pipeline state

Search in order:

1. `working/latest/pipeline_state.json`.
2. `working/runs/{run_id}/pipeline_state.json` if the user supplied a run ID.
3. `working/pipeline_state.json` for legacy runs.
4. Artifact-based fallback if no state exists.

Extract:

- `run_id`;
- `run_dir`;
- `dataset`;
- `question`;
- `status`;
- `agents` status map;
- output files and errors.

## Step 1a — migrate V1 state when needed

Use the helper instead of hand-editing schema migrations:

```python
from helpers.pipeline_state import detect_schema_version, migrate_v1_to_v2

if detect_schema_version(state) < 2:
    state = migrate_v1_to_v2(state, dataset=dataset)
```

Write the migrated state back to the same path after making a backup copy when practical.

## Step 1b — artifact fallback when no state exists

Only use this when no state file exists. Scan known artifact patterns:

| Agent | Expected artifacts |
|---|---|
| question-framing | `outputs/question_brief_*.md` |
| hypothesis | `outputs/hypothesis_doc_*.md` |
| data-explorer | `outputs/data_inventory_*.md`, `working/data_inventory_raw.md` |
| descriptive-analytics | `outputs/analysis_report_*.md`, `outputs/charts/*.png` |
| root-cause-investigator | `working/investigation_*.md` |
| cross-verification | `working/cross_verification_*.md`, `working/provenance_*.yaml` |
| validation | `outputs/validation_*.md` |
| opportunity-sizer | `working/sizing_*.md` |
| story-architect | `working/storyboard_*.md` |
| narrative-coherence-reviewer | `working/coherence_review_*.md` |
| chart-maker | `outputs/charts/*.png` |
| visual-design-critic | `working/design_review_*.md` |
| storytelling | `outputs/narrative_*.md` |
| deck-creator | `outputs/deck_*.md`, `outputs/deck_*.marp.md` |
| receipt-generator | `outputs/analysis_receipt_*.md` |

Also scan query logs and provenance files. Mark agents completed only when artifacts are
non-empty and do not contain obvious failure markers. If topics conflict across artifacts,
stop and ask rather than reconstructing a misleading state.

## Step 2 — normalize statuses and compute READY set

1. Read `agents/registry.yaml`.
2. For each agent in state:
   - `completed`, `complete`, `skipped`, `degraded` → terminal;
   - `failed` → reset to `pending` for retry after reporting;
   - `running` or `in_progress` → reset to `pending` because the run was interrupted.
3. Compute READY agents:
   - all `depends_on` terminal-complete;
   - at least one `depends_on_any` complete when specified.
4. If pending agents remain but none are READY, report the dependency deadlock and likely
   missing upstream artifacts.

## Step 3 — build context summary

Read completed outputs and summarize:

- question/decision context;
- active dataset;
- completed agents and one-line outputs;
- top findings from analysis reports;
- validation/cross-verification grade;
- storyboard/deck status;
- known blockers and warnings.

Verify again that this summary matches the user’s requested topic.

## Step 4 — present resume plan

Show:

```text
Resuming pipeline: {run_id}
Question: {question}
Dataset: {dataset}
Status: {status}

Completed agents: {n}
Failed/interrupted agents to retry: {n}
Next READY agents: {list}
Run directory: {run_dir}

Resume execution?
```

If there is any topic mismatch, present options and wait for the user before continuing.

## Step 5 — resume through `$run-pipeline`

After confirmation:

1. Update state to `status: running`.
2. Preserve completed outputs.
3. Reset failed/running agents to `pending`.
4. Continue with the `$run-pipeline` DAG walker from the READY set.
5. Keep writing to the original run directory when available.

## Special cases

- Storyboard says `NEEDS ADDITIONS`: reset story-architect to pending.
- Partial chart generation: compare expected chart specs to generated files and rerun missing
  charts.
- Cross-verification or validation failed: do not continue to deck until resolved.
- Stale data: warn if source data or active dataset changed materially since the original run.
- State and artifacts disagree: trust state, but surface the inconsistency.

## Limitations

Resuming restores artifacts and state, not the exact conversational reasoning. If critical
context is missing, summarize uncertainty and ask for confirmation before proceeding.
