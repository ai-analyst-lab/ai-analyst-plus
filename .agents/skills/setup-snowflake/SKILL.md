---
name: setup-snowflake
description: Guide first-time Snowflake setup, dependency/config checks, credential-safe configuration, connection testing, sample data exploration, and optional dataset knowledge creation. Use when users want to set up Snowflake, connect a Snowflake account, or troubleshoot Snowflake MCP/warehouse access.
---

# Setup Snowflake

## Purpose

Provide a safe Snowflake setup wizard that never exposes secrets, defaults to read-only access, verifies connectivity, and can create dataset knowledge for analysis.

## When to use

- the user asks to set up or connect Snowflake;
- Snowflake account/user/warehouse/MCP setup is incomplete;
- Snowflake connection needs testing or troubleshooting;
- sample Snowflake data should become an active dataset.

## Workflow

### 1. Check existing config without exposing secrets

Check for required environment/config presence by key name only. Do not print `.env` contents, passwords, private keys, or full token values. Check MCP/tool availability and dependency availability such as `uvx` when relevant.

### 2. Gather credentials safely

Ask for non-secret metadata normally: account identifier, username, warehouse, database, schema, role. For passwords/private keys, instruct users to place secrets in ignored local files or secure environment variables. Do not ask them to paste secrets into chat unless the environment explicitly provides a secure secret entry path.

### 3. Configure read-only access

Preserve existing `.env` and `.mcp.json` entries when editing. Default SQL permissions to SELECT/read-only. Prefer `$connect-snowflake` or `$connect-data type=snowflake` for the actual dataset setup when possible.

### 4. Restart/load guidance

If MCP configuration changed, tell the user a client restart or MCP reload may be required before tools become available. Stop before testing if tools cannot be loaded in the current session.

### 5. Test connection

Run a minimal connection query through available Snowflake tools or `ConnectionManager`: current account/user/warehouse/version. On failure, classify likely issue: account identifier, password/auth, activation, role/warehouse permission, network/VPN, or missing tool.

### 6. Explore and create dataset knowledge

Optionally list databases/schemas/tables, especially sample TPC-H. If user wants a named dataset, create `.knowledge/datasets/{dataset}/manifest.yaml`, `schema.md`, `quirks.md`, and update `.knowledge/active.yaml` after confirmation.

### Report

Return configuration status, connection status, accessible database/schema/table summary, and next query suggestion.

## Key contracts preserved from Claude

- `Snowflake`
- `read-only`
- `.env`
- `.mcp.json`
- `.knowledge/datasets`

## Codex adaptation notes

- Use natural language or `$setup-snowflake` invocation; do not rely on legacy slash-command-only mechanics.
- Prefer repository helpers, available MCP tools, and safe local fallbacks over provider-specific assumptions.
- Never print or commit credentials, tokens, secrets, private workspace content, or user-specific generated artifacts.
- If an external platform/tool is unavailable, state the blocker and offer the closest safe fallback.
