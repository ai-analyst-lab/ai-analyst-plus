---
name: data-inspect
description: Show the active dataset schema from Codex: tables, columns, row counts, relationships, or details for a specific table. Use when the user asks what data is available, lists tables, asks for schema/columns/data dictionary/table structure, invokes $data-inspect, or needs to understand the active dataset before analysis.
---

# Data Inspect

## Purpose

Show the active dataset's cached schema — tables, columns, row counts, keys, and
relationships — without querying live data. This is the Codex-native counterpart to the
legacy Claude schema inspector.

Use this for structure only. For row samples or statistical profiling, use the relevant data
exploration/profiling workflow instead.

## Required first step

Before answering any schema-inspection request:

1. Read `.knowledge/active.yaml`.
2. Resolve `active_dataset`.
3. Read `.knowledge/datasets/{active_dataset}/schema.md`.
4. If useful for display metadata, also read `.knowledge/datasets/{active_dataset}/manifest.yaml`.

Never guess the dataset from filenames, examples, or prior conversation. The active pointer
is the source of truth.

## Mode A — full schema overview

Use when the user asks for available data, tables, schema, data dictionary, or invokes
`$data-inspect` without a table name.

Steps:

1. Confirm an active dataset exists and its `schema.md` exists.
2. Extract dataset display name, connection type/location when available, table names, row
   counts, column counts, and primary/composite keys when documented.
3. Return a compact scannable summary, for example:

```text
Active Dataset: {display_name}
Connection: {type} ({database/schema/path if non-sensitive})

Tables:
  users          ~50,000 rows   8 columns   user_id (PK)
  products           500 rows   7 columns   product_id (PK)
  events        ~6.5M rows      9 columns   event_id (PK)

Use `$data-inspect {table}` for column details.
```

Format rules:

- Keep this as a quick reference, not a raw dump of `schema.md`.
- Left-align table names when practical.
- Use `~` for estimates.
- If row counts, keys, or descriptions are missing, say so rather than fabricating them.

## Mode B — specific table detail

Use when the user asks what columns are in a table or invokes `$data-inspect {table}`.

Steps:

1. Confirm an active dataset exists and its `schema.md` exists.
2. Find the requested table section, allowing case-insensitive matching.
3. If no exact table exists, use Mode D.
4. Display:
   - active dataset;
   - table name and description;
   - row count if available;
   - full column listing: name, type, nullable, description;
   - primary key(s) and foreign key relationships when documented;
   - important grain/completeness/quirk notes from the schema.

Example:

```text
Active Dataset: {dataset_name}
Table: users

Description: User dimension table with demographics and signup info
Row count: ~25,000 rows
Primary Key: user_id

Columns:
  user_id          BIGINT       NOT NULL    Unique user identifier
  email            VARCHAR      NOT NULL    User email address
  signup_date      DATE         NULL        Date user first registered

Relationships:
  ← orders.customer_id          one user, many orders
  ← events.user_id              one user, many events
```

## Mode C — no active dataset

Use when `.knowledge/active.yaml` is missing, empty, lacks `active_dataset`, or points to a
missing dataset directory.

Return:

```text
No active dataset configured.

To get started:
- Use `$connect-data` to connect a new dataset.
- Use `$datasets` to see available datasets.
- Use `$switch-dataset {name}` to activate an existing dataset.
```

Stop. Do not query databases, inspect example data, or guess a source.

## Mode D — table not found

When a requested table is not present in the active schema:

1. Confirm the table is truly absent with case-insensitive matching.
2. List available tables.
3. Suggest the closest match when obvious.
4. Suggest `$switch-dataset {name}` if they may mean another dataset or `$connect-data` if
   the table should exist but has not been connected/profiled.

Example:

```text
Table `{table}` was not found in {dataset_name}.

Available tables:
  users, orders, products, events

Use `$data-inspect` to see the full schema or `$switch-dataset {name}` for another dataset.
```

## Safety and anti-patterns

- Do not query the database merely to show schema; use cached knowledge files for speed and
  reproducibility.
- Do not expose credentials from manifests. Show only non-sensitive connection metadata.
- Do not show raw `schema.md` unless the user explicitly asks for the file contents.
- Do not inspect data rows; this skill is schema-only.
- Do not fabricate row counts, keys, descriptions, or relationships.
