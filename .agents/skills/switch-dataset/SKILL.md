---
name: switch-dataset
description: Change the active dataset from Codex after validating the target exists and checking for in-progress work. Use when the user asks to switch/change/use another dataset or data source, invokes $switch-dataset, or names a dataset that differs from the current active dataset.
---

# Switch Dataset

## Purpose

Change `.knowledge/active.yaml` to point to a different connected dataset, with safeguards
against accidental context loss. This is the Codex-native counterpart to the legacy Claude
switch-dataset workflow.

## When to use

Use when the user explicitly wants to analyze a different dataset, for example:

- `$switch-dataset sales-prod`;
- “switch to sales data”;
- “use the marketing dataset instead”;
- “change to the production warehouse”.

Do not silently switch datasets merely because another dataset is mentioned. If intent is
ambiguous, briefly confirm before changing state.

## Workflow

### Step 1 — discover and validate target dataset

1. List available datasets by scanning `.knowledge/datasets/` for subdirectories with
   `manifest.yaml` files.
2. Normalize the requested target to lowercase for comparison, but preserve the actual
   dataset ID when writing files.
3. If there is an exact case-insensitive match, use it.
4. If no exact match exists, try fuzzy matching:
   - substring match;
   - case-insensitive partial match;
   - obvious hyphen/space normalization.
5. If exactly one fuzzy match exists, tell the user: `Matched {requested} to {actual}`.
6. If multiple matches exist, list matches and ask the user to choose; do not switch yet.
7. If no match exists, list available datasets and suggest `$connect-data` to add a new one.

### Step 2 — check current active dataset

Read `.knowledge/active.yaml` and get `active_dataset`.

If the target is already active:

- say it is already active;
- show a short summary from its manifest;
- list other available datasets if any;
- stop without rewriting the file.

### Step 3 — validate the dataset brain

Confirm `.knowledge/datasets/{target}/manifest.yaml` exists. If it is missing, stop and say
the dataset directory exists but is not fully set up. Suggest `$connect-data` or restoring the
manifest.

### Step 4 — check in-progress work

Before switching, inspect `working/` and count non-hidden files/directories, excluding
`.gitkeep`.

If there are **3 or more** items:

1. Warn that in-progress artifacts may be tied to the old dataset’s schema and become harder
   to resume after switching.
2. Show the count and first 3–5 item names.
3. Ask for explicit confirmation before editing `.knowledge/active.yaml`.
4. If the user declines or does not clearly confirm, cancel the switch.

If there are fewer than 3 items, continue without confirmation.

### Step 5 — update active pointer

1. Read existing `.knowledge/active.yaml` as YAML when possible.
2. Preserve unrelated keys such as `active_org` and `use_remote`.
3. Set `active_dataset` to the exact target dataset ID.
4. Write `.knowledge/active.yaml`.

### Step 6 — confirm switch

Read the target manifest and return:

```text
✓ Switched to: {target}
Tables: {table_count or unknown}
Date range: {start} to {end, or unknown}
Connection: {connection_type}
Last analysis: {last_used or never/unknown}
Row counts: {top 3 tables by row count when available}
```

If the user proceeded despite in-progress work, add:

```text
To return to the previous dataset, use `$switch-dataset {old_dataset}`.
```

## Safety and anti-patterns

- Never silently switch; always provide a confirmation summary after a successful switch.
- Never skip the in-progress work check when `working/` has 3+ artifacts.
- Never fail solely due to case mismatch.
- Never assume `data_sources.yaml` is populated; `.knowledge/datasets/` is the source of
  truth for switch targets.
- Never print credentials from manifests.
- Never overwrite unrelated `active.yaml` fields.
