---
name: trace
description: Show provenance for reported numbers by linking findings to SQL/query logs with confidence badges. Use after analysis when users ask where a number came from, want proof, or need an audit trail.
---

# Trace

## Purpose
Render a provenance trace tying findings to query log entries and SQL.

## Workflow
1. Resolve the analysis id. Prefer the current analysis context; if absent, ask for an analysis id or run id.
2. Resolve the dataset from `.knowledge/active.yaml` or the referenced run/archive.
3. Use `helpers.trace_viewer.build_trace(analysis_id, dataset, date)` when possible.
4. Report the generated artifact path, usually `working/trace_{analysis_id}.html`.
5. Summarize each finding with its confidence badge:
   - `cited`: finding explicitly named the query;
   - `value-match`: query result matches the finding value;
   - `inferred`: likely match by time/proximity only;
   - unmatched: no supporting query found.
6. Call out unmatched findings and orphan queries as issues to fix, not as noise.

## Safety
- `inferred` is not proof; label it as a hint.
- If no query logs or findings manifest exist, say that provenance cannot be reconstructed.
- Do not hide unverified numbers.
