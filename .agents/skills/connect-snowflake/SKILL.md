---
name: connect-snowflake
description: Configure and validate a Snowflake data connection for analysis. Use when users want to connect Snowflake, set up Snowflake credentials, validate warehouse access, troubleshoot Snowflake queries, or create Snowflake dataset knowledge under `.knowledge/`.
---

# Connect Snowflake

## Purpose

Guide Snowflake setup safely, validate connectivity, and hand off to `$connect-data` so Snowflake becomes an active dataset without leaking credentials.

## When to use

- the user asks to connect Snowflake or configure a Snowflake warehouse;
- Snowflake credentials, account, database, schema, warehouse, or role need validation;
- a Snowflake MCP/connector setup is failing;
- a dataset manifest/schema should be created from Snowflake.

## Workflow

### 1. Gather non-secret connection metadata

Ask for account/host, database, schema, warehouse, role, and authentication method. Do not ask the user to paste passwords or private keys into chat. Direct secrets to environment variables, local credential files ignored by git, or the MCP/auth mechanism configured for this repo.

### 2. Validate local configuration

Check for expected config files such as `.mcp.json`, `snowflake-mcp-config.yaml`, or environment variables without printing secrets. Confirm required Python packages or MCP tools are available.

### 3. Test connectivity

Use the repository connector path where available, preferably through `$connect-data type=snowflake` or `helpers.connection_manager.ConnectionManager`. Run a minimal query such as current database/schema/role and a small table list. Log queries when required.

### 4. Create dataset knowledge

After connectivity succeeds, ensure `.knowledge/datasets/{dataset}/manifest.yaml`, `schema.md`, and `quirks.md` exist. Record schema/database/warehouse metadata but never credentials. Update `.knowledge/active.yaml` only after user confirmation or connect-data success.

### 5. Troubleshoot safely

For auth failures, separate causes:

- missing/expired credentials;
- network/VPN allowlist;
- role/warehouse permissions;
- database/schema not found;
- package/MCP unavailable.

Report exact next action without revealing secrets.

### Output

Return connection status, active dataset name, table count or schema coverage, query-log path when applicable, and any remaining limitations.

## Key contracts preserved from Claude

- `Snowflake`
- `.knowledge/datasets`
- `.knowledge/active.yaml`
- `ConnectionManager`
- `credentials`

## Codex adaptation notes

- Use natural language or `$connect-snowflake` invocation; do not rely on legacy slash-command-only mechanics.
- Prefer existing repository helpers, MCP tools exposed to the current session, and safe local fallbacks over provider-specific assumptions.
- Never print or commit credentials, tokens, private document contents, or user-specific generated artifacts.
- If automation is unavailable, state the blocker and provide the closest safe manual or local-export path.
