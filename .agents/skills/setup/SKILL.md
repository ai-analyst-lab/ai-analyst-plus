---
name: setup
description: Run the Codex onboarding/setup interview to populate `.knowledge/` with user profile, data connection, business context, and communication preferences. Use when users want to set up, configure, onboard, initialize, connect first data, resume setup, check setup status, or reset setup state.
---

# Setup

## Purpose

Run a 4-phase conversational interview that turns a blank or partial `.knowledge/` directory into a usable analytical environment. This is the Codex-native counterpart to the legacy Claude setup skill, adapted to natural language and `$connect-data` instead of slash-command mechanics.

## When to use

- the user wants to get started, configure the analyst, onboard, initialize, or set up the environment;
- `.knowledge/user/profile.md` or `.knowledge/setup-state.yaml` is missing and the user asks for first-time setup;
- the user asks for setup status, setup reset, or setup reset everything;
- the user wants a guided first data connection plus business-context capture.

## Workflow

### Resolve mode first

- **Status**: if the user asks for setup status, read `.knowledge/setup-state.yaml` and summarize each phase, timestamps, and overall status. If missing, say setup has not started.
- **Tier 1 reset**: if the user asks to reset profile/preferences, require explicit plain-text confirmation `yes` before deleting `.knowledge/user/profile.md`. Preserve data connections and business context.
- **Tier 2 reset everything**: if the user asks to reset everything, require the exact confirmation phrase `reset everything` before deleting `.knowledge/user/profile.md`, `.knowledge/user/business-context.md`, `.knowledge/datasets/`, and `.knowledge/active.yaml`. Never combine reset tiers.
- **Start/resume**: otherwise read `.knowledge/setup-state.yaml` when present and resume at the first pending phase. If all phases are complete, report completion and offer status or reset.

### State file

Maintain `.knowledge/setup-state.yaml` with this shape:

```yaml
setup_version: 1
started_at: "YYYY-MM-DDTHH:MM:SS"
last_updated: "YYYY-MM-DDTHH:MM:SS"
status: "complete" | "partial" | "in-progress" | "pending"
phases:
  role_and_team:
    status: "complete" | "skipped" | "pending"
    completed_at: null
  data_connection:
    status: "complete" | "partial" | "skipped" | "pending"
    completed_at: null
    partial_reason: null
  business_context:
    status: "complete" | "skipped" | "pending"
    completed_at: null
  preferences:
    status: "complete" | "skipped" | "pending"
    completed_at: null
```

Use ISO-like local timestamps. Never store credentials in setup state.

### Phase 1 — Role & Team

Ask at most 2 questions, then stop for the user's response:

1. role;
2. technical level: beginner, intermediate, or advanced.

Then ask optional team/domain questions. Validate unusual answers once. Map common synonyms such as PM, DS, eng, and analyst.

Write `.knowledge/user/profile.md` with role/expertise, inferred SQL/statistics comfort, domain/team, a placeholder communication preferences section, and a corrections log. Update setup state and verify the file exists before moving on.

### Phase 2 — Data Connection

Ask what data source they want:

- CSV directory;
- DuckDB file;
- cloud warehouse: MotherDuck, Postgres, BigQuery, Snowflake;
- sample/no data yet.

For CSV/DuckDB, verify the path exists before invoking or following `$connect-data`. For cloud warehouses, route through `$connect-data` and mark the phase `partial` with `partial_reason: warehouse_mcp_needed` if credentials/MCP setup remains. For samples, inspect `data/examples/` and let the user choose or skip.

After the connection attempt, check for `.knowledge/datasets/{dataset}/manifest.yaml` where possible, update state, and summarize source, tables, and status.

### Phase 3 — Business Context

Ask in groups of 2 and wait between groups:

1. what the company/product does;
2. top 2-3 metrics;
3. current business question or problem;
4. current OKRs/goals;
5. key segments and known seasonality when relevant.

Write `.knowledge/user/business-context.md` with company/product, key metrics, current focus, segments, and patterns. If a dataset is connected and no metrics index exists, create stub metric entries under `.knowledge/datasets/{active}/metrics/index.yaml` without overwriting existing definitions.

### Phase 4 — Preferences

Ask in groups of 2:

1. detail level: executive summary, standard, or deep dive;
2. chart preference: minimal, standard, or chart-heavy;
3. preferred export channels;
4. custom work-style notes.

Update the Communication Preferences section in `.knowledge/user/profile.md`, update setup status to `complete` or `partial`, verify the profile no longer contains the placeholder, and provide a concise final setup summary.

## Key contracts preserved from Claude

- `.knowledge/setup-state.yaml`
- `.knowledge/user/profile.md`
- `.knowledge/user/business-context.md`
- `$connect-data`
- `reset everything`

## Codex adaptation notes

- Use natural language or `$setup` invocation; do not rely on legacy slash-command-only mechanics.
- Prefer repository helpers, standards, and existing skill composition over duplicating large provider-specific prompts.
- If a required external capability is unavailable, state the blocker and offer the closest safe manual fallback.
