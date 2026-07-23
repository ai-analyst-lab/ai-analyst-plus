---
name: setup-notion
description: Guide Notion MCP/OAuth setup and verify Notion workspace access for exports or ingestion. Use when users want to connect Notion, set up Notion, export to Notion, authenticate Notion, or troubleshoot Notion MCP access.
---

# Setup Notion

## Purpose

Configure and verify Notion access safely, preserving existing MCP configuration and routing to `$notion-export` or `$notion-ingest` after setup.

## When to use

- the user asks to connect or set up Notion;
- Notion export/ingest fails because tools/auth are unavailable;
- the user wants an Analysis Gallery database;
- Notion OAuth scope or page sharing needs troubleshooting.

## Workflow

### 1. Check existing configuration

Inspect `.mcp.json` if present and available Notion tools/resources. Preserve other MCP servers. Do not print credentials.

### 2. Configure when missing

When local config editing is appropriate, add a Notion hosted MCP entry equivalent to an HTTP Notion server. If this Codex environment cannot manage MCP config directly, give exact user instructions and stop before claiming success.

### 3. Restart/authenticate guidance

Explain that new MCP server config may require restarting the client and completing OAuth through the MCP UI. Remind the user to share the target pages/databases with the integration.

### 4. Verify access

Use an available Notion search/list tool to verify pages/databases are accessible. If verification fails, diagnose OAuth expiration, unshared pages, missing workspace permissions, or tool unavailability.

### 5. Analysis Gallery

Search for an `Analysis Gallery` database. If found, record/return its database ID for exports. If missing, offer to create or document the required schema: Title, Date, Dataset, Confidence, Status.

### 6. Summary

Report server/config status, accessible page/database count, gallery status, and next available actions: `$notion-export` or `$notion-ingest`.

## Key contracts preserved from Claude

- `Notion`
- `OAuth`
- `Analysis Gallery`
- `.mcp.json`
- `notion-export`

## Codex adaptation notes

- Use natural language or `$setup-notion` invocation; do not rely on legacy slash-command-only mechanics.
- Prefer repository helpers, available MCP tools, and safe local fallbacks over provider-specific assumptions.
- Never print or commit credentials, tokens, secrets, private workspace content, or user-specific generated artifacts.
- If an external platform/tool is unavailable, state the blocker and offer the closest safe fallback.
