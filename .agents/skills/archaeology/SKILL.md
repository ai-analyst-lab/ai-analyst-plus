---
name: archaeology
description: Retrieve proven SQL patterns, table cheatsheets, and join patterns from `.knowledge/query-archaeology/curated` before writing new SQL. Use as a preflight for analysis or when users ask for known query/table patterns.
---

# Query Archaeology

## Purpose
Reuse validated SQL and table knowledge rather than rediscovering joins and gotchas from scratch.

## Workflow
1. Read `.knowledge/query-archaeology/curated/index.yaml`; if missing or all counts are zero, silently skip unless the user explicitly asked about archaeology.
2. Extract search terms from the analysis context: table names, metric names, and intent tags such as funnel, retention, revenue, or cohort.
3. Search cookbook entries in `curated/cookbook/*.yaml` by tables and tags.
4. Search table cheatsheets in `curated/tables/*.yaml` by table name.
5. Search join patterns in `curated/joins/*.yaml` by matching one or more tables.
6. Return matches as an additive context block containing title, SQL, tables, tags, caveats, grain, primary key, joins, cardinality, and validation status.
7. Pass useful matches into the analysis and note when archaeology patterns were used.

## Safety
- Read-only: never modify archaeology files.
- Use substring/fuzzy matching; do not require exact names.
- Do not block analysis if retrieval fails.
