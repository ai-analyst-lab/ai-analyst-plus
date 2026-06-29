---
name: setup-dev-context
description: Capture developer/codebase context for analytics workflows: repository type, data layer, SQL conventions, integration mode, output conventions, and team-specific database practices. Use when developers want to configure AI Analyst for a codebase, dbt project, warehouse conventions, schema prefixes, or team data stack.
---

# Setup Dev Context

## Purpose

Store lightweight development-environment conventions so future SQL and analysis work respect team/database/codebase practices without creating full dataset connections.

## When to use

- developers ask to configure the analyst for their codebase or team;
- the user mentions dbt, schema prefixes, SQL style, warehouse conventions, or data-stack integration;
- team-wide development setup is needed after basic user/data setup;
- the user asks to reset or update dev context.

## Workflow

### 1. Check prerequisites

Read `.knowledge/setup-state.yaml` when present. If basic setup/data connection is incomplete, suggest `$setup` or `$connect-data` first. Do not block if the user explicitly wants to record conventions before data is connected; just mark limitations.

### 2. Interview and confirm

Ask for the five groups, pre-filling known answers but still confirming:

1. repository type;
2. data layer: database, schema convention, model/schema locations;
3. SQL conventions: naming, timezone, null handling, style guide;
4. integration mode: ad-hoc, dbt models, replica, exports, warehouse direct;
5. file conventions: output dir, SQL naming, branch strategy.

### 3. Write exactly the dev-context file

Create `.knowledge/user/dev-context.yaml` with schema version, timestamps, codebase, data layer, SQL conventions, integration, and file conventions. Do not create dataset manifests, helper scripts, or setup guides from this skill.

### 4. Update setup state lightly

If `.knowledge/setup-state.yaml` exists, add or update `dev_context.status: complete` and `completed_at`. Preserve unrelated setup state.

### 5. Reset mode

If the user requests reset, delete `.knowledge/user/dev-context.yaml` after confirmation and remove/mark the dev-context state. Do not touch dataset connections.

### 6. Report

Summarize the exact conventions captured and path saved.

## Key contracts preserved from Claude

- `.knowledge/user/dev-context.yaml`
- `SQL conventions`
- `dbt`
- `dev_context`
- `schema prefix`

## Codex adaptation notes

- Use natural language or `$setup-dev-context` invocation; do not rely on legacy slash-command-only mechanics.
- Prefer repository helpers, available MCP tools, and safe local fallbacks over provider-specific assumptions.
- Never print or commit credentials, tokens, secrets, private workspace content, or user-specific generated artifacts.
- If an external platform/tool is unavailable, state the blocker and offer the closest safe fallback.
