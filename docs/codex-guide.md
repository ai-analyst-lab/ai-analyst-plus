# Codex Guide

This guide explains how to use this repository with Codex. The repo still supports legacy
Claude Code workflows under `.claude/skills/`, but Codex-native workflows live under
`.agents/skills/`.

## Start here

1. Read `AGENTS.md` for repository rules.
2. Check available Codex skills in `.agents/skills/INDEX.md`.
3. Check the active dataset pointer in `.knowledge/active.yaml` before data analysis.
4. Use repository helpers in `helpers/` rather than writing one-off statistical or warehouse
   logic.
5. Save intermediate artifacts in `working/` and final outputs in `outputs/`.

## Core Codex workflow

### 1. Connect or choose data

- Use `$connect-data` to add a dataset.
- Use `$datasets` to list connected datasets.
- Use `$switch-dataset {name}` to change the active dataset.
- Use `$data-inspect` to inspect the active schema.

Dataset knowledge is stored under:

```text
.knowledge/datasets/{dataset}/manifest.yaml
.knowledge/datasets/{dataset}/schema.md
.knowledge/datasets/{dataset}/quirks.md
.knowledge/datasets/{dataset}/metrics/index.yaml
```

The active dataset is stored in:

```text
.knowledge/active.yaml
```

### 2. Define metrics before analysis

Use `$data-quality-check` before drawing conclusions from a dataset or table. Use
`$metric-spec` when a metric lacks a denominator, time window, grain, filters,
attribution rule, source table, or threshold. Registered metric specs live under:

```text
.knowledge/datasets/{active}/metrics/
```

### 3. Run analysis with repo helpers

For warehouse/data access, prefer:

```python
from helpers.connection_manager import ConnectionManager
```

For experiment, validation, charts, exports, and provenance, reuse existing modules under
`helpers/`. Do not duplicate statistical routines.

Before SQL analysis, read active dataset metadata in `.knowledge/`, verify connectivity, and
log executed queries with `scripts/log_query.py` when applicable.

### 4. Validate important results

- Use `$reliability` to test whether an analytics answer is stable across independent runs.
- Use `$independent-review` for provider-neutral blind second-pass validation.
- Use `$claude-review` when Claude should independently validate a Codex-produced result.

## Codex skill invocation

Codex skills are invoked by natural language or `$skill-name`, for example:

```text
Use $datasets to show what data is connected.
Use $data-inspect orders to show the orders table schema.
Use $metric-spec to define activation rate.
Use $reliability "What is our 30-day retention rate?" 5.
```

Legacy Claude slash commands such as `/connect-data` or `/reliability` are documented in
`.claude/skills/`; Codex users should prefer the `$skill-name` equivalents where available.

## Current Codex-native skills

See `.agents/skills/INDEX.md` for the canonical list. The current core set includes:

- `$connect-data`
- `$datasets`
- `$switch-dataset`
- `$data-inspect`
- `$data-quality-check`
- `$metric-spec`
- `$reliability`
- `$compare`
- `$experiment`
- `$independent-review`
- `$claude-review`
- `$skill-parity-review`

## Known limitations

Codex migration is in progress. Some legacy Claude workflows do not yet have Codex-native
counterparts, including several export, presentation, pipeline orchestration, and integration
skills. When a Codex skill is missing, use `$skill-parity-review` to port the corresponding
Claude skill safely instead of copying Claude-specific mechanics.

## Development checks

Run:

```bash
pytest tests/test_codex_skills.py
pytest
```

For chart/theme changes, also run:

```bash
python scripts/lint_chart_colors.py
python scripts/lint_wcag.py
python scripts/check_theme_sync.py
```
