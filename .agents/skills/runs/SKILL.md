---
name: runs
description: Browse, inspect, compare, and clean up past pipeline runs under `working/runs/` and archived analyses under `.knowledge/analyses`. Use when users ask for run history, latest runs, completed analyses, or cleanup.
---

# Runs

## Purpose
Provide a window into pipeline execution history and archived analysis history.

## Sources
- `working/runs/`: active, partial, failed, or recently completed pipeline state.
- `.knowledge/analyses/`: durable archived analyses and findings.

## Workflow
1. Parse the requested mode: list, latest, detail, compare, or clean.
2. For list/history requests, scan both sources and label source clearly.
3. For run detail, read `pipeline_state.json`, recent output files, status, started/completed timestamps, dataset, question, and errors.
4. For latest, prefer `working/latest/pipeline_state.json` if it exists, otherwise newest run directory.
5. For compare, show differences in question, dataset, status, agents completed, outputs, confidence, and findings.
6. For clean, never delete automatically. Show candidates older than the retention threshold and ask for explicit confirmation.

## Output contract
- Use a table for lists: run/archive id, date, dataset, question/title, status, source.
- Mark missing/corrupt state files without crashing.
- Recommend `$resume-pipeline` for incomplete runs and `$history` for archived analysis detail.

## Safety
- Do not delete files without explicit user confirmation.
- Never expose credentials that may appear in run artifacts.
