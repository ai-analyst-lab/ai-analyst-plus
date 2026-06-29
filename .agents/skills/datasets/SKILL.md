---
name: datasets
description: List connected datasets from Codex with active status, connection type, table counts, date ranges, and safe summaries. Use when the user asks what datasets or data sources are available, what dataset is active, to list/switch data, invokes $datasets, or needs to choose a dataset before analysis.
---

# Datasets

## Purpose

List all connected datasets with their active status, table counts, connection type, date
coverage, and last-known profiling metadata. This is the Codex-native counterpart to the
legacy Claude datasets workflow.

## Sources of truth

Use two discovery paths, in this order:

1. **Registry-first**: read `data_sources.yaml`. If it exists and has non-empty `sources`,
   treat those source IDs as the official registered datasets.
2. **Brain-first fallback**: if the registry is missing or empty, scan
   `.knowledge/datasets/` for subdirectories. Each directory with a `manifest.yaml` is a
   connected dataset.

Then read `.knowledge/active.yaml` to determine `active_dataset`.

Many local installations have an empty registry but populated `.knowledge/datasets/`; that
is normal. Use whichever path yields results.

## Workflow

### Step 1 — discover datasets

- Read `data_sources.yaml` when present.
- If registry entries exist, use their keys as candidate dataset IDs.
- Otherwise scan `.knowledge/datasets/*/manifest.yaml`.
- Include incomplete dataset directories in a Notes section when a manifest is missing, but
  mark them as needing profiling/setup.

### Step 2 — read active pointer

Read `.knowledge/active.yaml`. If it is missing or lacks `active_dataset`, mark all datasets
as inactive and state that no active dataset is configured.

### Step 3 — enrich with manifest data

For each dataset, read `.knowledge/datasets/{id}/manifest.yaml` when available and extract:

- `display_name`;
- `connection.type`, `connection_type`, or equivalent connection metadata;
- non-sensitive database/schema/path details;
- `summary.table_count`;
- `summary.date_range`;
- `summary.row_counts`;
- `summary.last_updated` or similar timestamp.

If fields are missing, show `unknown` rather than inventing values.

### Step 4 — optional North Star surface

If `.knowledge/active.yaml` includes `active_org`, and
`.knowledge/organizations/{active_org}/business/north-star/index.yaml` exists, read it. If
`quick_ref.active_nsm` is set, prepend:

```text
North Star: "{quick_ref.active_nsm}"
  Last audited: {quick_ref.last_audit_at} ({quick_ref.last_audit_verdict}) | Phase: {quick_ref.journey_phase}
```

Skip this block silently when the org or North Star file is absent.

### Step 5 — display the list

Use a compact, safe format:

```text
Connected Datasets:

  * your-dataset (active)
    Your Dataset Name — 6 tables, 2024-01-01 to 2026-03-31
    Connection: snowflake (ANALYTICS.PUBLIC)
    Last updated: 2026-06-27

  - other-dataset
    Other Dataset — table count unknown, date range unknown
    Connection: csv (data/other)
    Last updated: unknown

Commands:
  $switch-dataset {name}  — switch active dataset
  $connect-data           — connect a new dataset
  $data-inspect           — inspect active dataset schema
```

Mark the active dataset with `*`; others with `-`.

## Empty state

If no datasets are found, return:

```text
No connected datasets found.

Next steps:
- Use `$connect-data` to add a dataset.
- If a dataset was manually added, make sure it has `.knowledge/datasets/{id}/manifest.yaml`.
```

## Security and quality rules

- Never display credentials, tokens, passwords, private keys, or secret environment variable
  values from manifests or registry files.
- Show only non-sensitive connection type, database, schema, project, or local path metadata.
- Do not query warehouses to enrich this list; this skill reads registry/knowledge files.
- If a manifest is malformed, include the dataset with a warning and continue listing other
  datasets.
- If two datasets appear to point to the same non-sensitive location, mention it in Notes so
  the user can clean up duplicates.
