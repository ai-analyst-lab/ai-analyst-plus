---
name: connect-data
description: Guided Codex workflow to connect a new dataset for analysis. Use when the user wants to add/connect/set up data, configure CSV/DuckDB/PostgreSQL/BigQuery/Snowflake/MotherDuck access, create a dataset brain, test connectivity, profile schema, or invokes $connect-data.
---

# Connect Data

## Purpose

Guide the user through connecting a new dataset by creating knowledge files, testing
connectivity, profiling schema, and setting the dataset active. This is an execution
workflow, not just documentation: make safe filesystem changes and run validation steps when
the needed details are available.

This is the Codex-native counterpart to the legacy Claude connect-data workflow.

## Supported connection types

- CSV directory
- Local DuckDB file
- MotherDuck
- PostgreSQL
- BigQuery
- Snowflake

If the user provides a type up front, such as `type=postgres` or “connect my Snowflake
warehouse,” skip type selection and continue with that type.

## Workflow

### Step 1 — choose connection type

If unspecified, ask the user which source they want to connect:

1. CSV files — local directory of `.csv` files.
2. DuckDB — local `.duckdb` file.
3. MotherDuck — cloud DuckDB database.
4. PostgreSQL — database connection via environment-backed credentials.
5. BigQuery — Google BigQuery project/dataset.
6. Snowflake — Snowflake warehouse.

### Step 2 — collect non-secret connection details

Collect only the fields needed for the selected type.

For CSV:

- ask for the CSV directory path relative to the repo or absolute path;
- verify it exists and contains `.csv` files;
- list found files and confirm before proceeding.

For DuckDB:

- ask for the `.duckdb` file path;
- verify it exists;
- test with `ConnectionManager` or a read-only `SELECT 1` through the manager.

For MotherDuck:

- ask for database and schema;
- explain that token/auth must be configured outside the manifest, usually through the
  environment or the user’s MCP/warehouse setup.

For PostgreSQL, BigQuery, and Snowflake:

- start from the matching file in `connection_templates/` when useful;
- ask for host/project/account/database/schema/warehouse/user fields as applicable;
- never ask the user to paste raw passwords, private keys, service account JSON, or tokens
  into chat;
- use environment variable references in manifests, such as `$PG_PASSWORD`,
  `$GOOGLE_APPLICATION_CREDENTIALS`, or `$SNOWFLAKE_PASSWORD`.

### Step 3 — create the dataset brain

1. Generate `dataset_id` from the display name using lowercase hyphenated text:
   - `Production Analytics` -> `production-analytics`
   - `GA4 Event Data` -> `ga4-event-data`
2. If `.knowledge/datasets/{dataset_id}/` already exists, ask before overwriting. If the
   user wants a new dataset, append a numeric suffix such as `-2`.
3. Create:

```text
.knowledge/datasets/{dataset_id}/
.knowledge/datasets/{dataset_id}/manifest.yaml
.knowledge/datasets/{dataset_id}/schema.md
.knowledge/datasets/{dataset_id}/quirks.md
.knowledge/datasets/{dataset_id}/metrics/index.yaml
```

4. Write `manifest.yaml` with non-secret connection metadata, local fallback metadata when
   available, empty/unknown summary fields, `status: active`, and current creation timestamp.
5. Write `quirks.md` with section headers for known caveats, grain notes, freshness, and
   data quality issues.
6. Initialize `metrics/index.yaml` as an empty list or documented empty metric index.

### Step 4 — test connectivity

Use `ConnectionManager` from `helpers/connection_manager.py`. Do not write one-off warehouse
connection code when the manager supports the source.

Example pattern:

```python
from helpers.connection_manager import ConnectionManager

mgr = ConnectionManager(config=config)
result = mgr.test_connection()
```

If the test fails:

- show the sanitized error;
- do not declare success;
- offer to edit the manifest/config and retry;
- leave the dataset brain in place if already created, clearly marked as not fully profiled.

### Step 5 — profile schema

Use `ConnectionManager` methods where possible:

1. `mgr.list_tables()`;
2. `mgr.get_table_schema(table_name)`;
3. render `.knowledge/datasets/{dataset_id}/schema.md` via
   `schema_to_markdown()` from `helpers/data_helpers.py` or an equivalent structured
   markdown format.

For very large schemas, profile table names and column headers first, then note that deep
profiling was skipped or limited.

### Step 6 — set active

Update `.knowledge/active.yaml`:

- preserve unrelated fields such as `active_org`;
- set `active_dataset: {dataset_id}`;
- for remote warehouses, set/use a remote flag only when the user explicitly wants live
  remote access rather than local fallback.

Confirm:

```text
Connected! {display_name} is now the active dataset.
Tables: {table_count}
Connection: {type}
Schema: .knowledge/datasets/{dataset_id}/schema.md
```

Suggest next steps:

- `$data-inspect` to inspect schema;
- `$metric-spec` to define key metrics;
- ask an analysis question.

## Security rules

- Never print or commit credentials.
- Never write raw passwords/tokens/private keys to `manifest.yaml`; write environment
  variable references instead.
- Redact secret-looking fields from errors and summaries.
- Do not commit generated user connection manifests unless the user explicitly asks and they
  contain no secrets.

## Edge cases

- Directory does not exist: offer to create it for local data, or ask for the correct path.
- No CSV files found: check whether files are Parquet/JSON and explain current support.
- Dataset ID collision: ask before overwrite or choose a suffixed ID.
- Connection repeatedly fails: suggest credentials, VPN/firewall, package installation, or
  warehouse permissions checks.
- Schema profiling fails after connection succeeds: keep the manifest, mark profiling as
  incomplete, and tell the user how to retry.
