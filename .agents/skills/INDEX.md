# Codex Skills Index

Codex-native skills live under `.agents/skills/`. These skills complement, but do not fully
replace, legacy Claude Code skills under `.claude/skills/`.

| Skill | Path | Use when | Key artifacts |
|---|---|---|---|
| `connect-data` | `.agents/skills/connect-data/SKILL.md` | The user wants to add/connect/set up data or configure CSV, DuckDB, MotherDuck, PostgreSQL, BigQuery, or Snowflake for analysis. | `.knowledge/datasets/{dataset}/manifest.yaml`, `.knowledge/datasets/{dataset}/schema.md`, `.knowledge/active.yaml` |
| `datasets` | `.agents/skills/datasets/SKILL.md` | The user wants to list connected datasets, see the active dataset, or choose which data source to analyze. | `data_sources.yaml`, `.knowledge/datasets/`, `.knowledge/active.yaml` |
| `switch-dataset` | `.agents/skills/switch-dataset/SKILL.md` | The user wants to change the active dataset or use a different connected data source. | `.knowledge/active.yaml` |
| `data-inspect` | `.agents/skills/data-inspect/SKILL.md` | The user wants to see active dataset schema, tables, columns, row counts, keys, or table structure. | `.knowledge/datasets/{active}/schema.md` |
| `data-quality-check` | `.agents/skills/data-quality-check/SKILL.md` | The user is about to analyze/query data, asks whether data is clean, or needs table-level quality probes and caveats. | `working/data_quality/`, `.knowledge/datasets/{active}/quirks.md` |
| `metric-spec` | `.agents/skills/metric-spec/SKILL.md` | The user wants to define, clarify, document, standardize, or register a business/product metric with denominator, time window, filters, thresholds, and source SQL. | `.knowledge/datasets/{active}/metrics/` |
| `reliability` | `.agents/skills/reliability/SKILL.md` | The user wants to check whether an analytics answer is stable across independent repeated runs. | `.knowledge/reliability/<run>/`, `.knowledge/reliability/log.jsonl` |
| `compare` | `.agents/skills/compare/SKILL.md` | The user wants to compare an analytics question with and without a context or metric-definition overlay. | `.knowledge/comparisons/` |
| `experiment` | `.agents/skills/experiment/SKILL.md` | The user wants to design, power, monitor, analyze, interpret, or report on an experiment or A/B test. | `experiments/{slug}/` |
| `run-pipeline` | `.agents/skills/run-pipeline/SKILL.md` | The user wants an end-to-end multi-phase analysis workflow, validated narrative, charts, and deck/export artifacts. | `working/runs/{run}/`, `outputs/` |
| `resume-pipeline` | `.agents/skills/resume-pipeline/SKILL.md` | The user wants to continue, recover, or finish an interrupted pipeline run. | `working/latest/pipeline_state.json`, `working/runs/` |
| `export` | `.agents/skills/export/SKILL.md` | The user wants to export/share/send analysis results as slides, email, Slack, brief, data, docx, Google Doc, Notion, or receipt. | `outputs/` |
| `independent-review` | `.agents/skills/independent-review/SKILL.md` | The user wants a provider-neutral blind second-pass validation, second opinion, cross-check, or independent re-derivation. | `working/independent_review/`, `.knowledge/independent-review/log.jsonl` |
| `claude-review` | `.agents/skills/claude-review/SKILL.md` | Codex produced an analysis and the user wants Claude to independently validate it from a blind brief. | `working/claude_review/`, `.knowledge/claude-review/log.jsonl` |
| `skill-parity-review` | `.agents/skills/skill-parity-review/SKILL.md` | The user wants to compare a Codex skill with its corresponding Claude skill, audit migration parity, port a Claude skill to Codex, or bring a Codex skill up to parity. | `working/skill_parity_review/` |

## Invocation

Codex skills are not slash commands. Invoke them with natural language or `$skill-name`, for example:

```text
Use $connect-data to add a CSV directory.
Use $datasets to list connected data sources.
Use $switch-dataset production-analytics to change the active dataset.
Use $data-inspect to inspect the active schema.
Use $data-quality-check orders before analyzing the orders table.
Use $metric-spec to define checkout conversion rate.
Use $reliability "What is our 30-day retention rate?" 5 to check answer stability.
Use $compare "What's our retention rate?" --with .knowledge/comparisons/conditions/c1_retention_contract.
Use $experiment analyze checkout-redesign to analyze an A/B test.
Use $run-pipeline question="Why did conversion drop?" to run the full workflow.
Use $resume-pipeline to continue an interrupted run.
Use $export brief to create a stakeholder decision brief.
Use $skill-parity-review to port another Claude skill to Codex.
```

Do not use underscore slash commands such as `/skill_parity_review`; Codex treats those as unsupported built-in commands.

## Legacy Claude compatibility

- Legacy Claude skills remain under `.claude/skills/`.
- Legacy Claude `/codex-review` remains at `.claude/skills/codex-review/SKILL.md`.
- Codex users should prefer `$independent-review` for provider-neutral validation and
  `$claude-review` when Claude should validate a Codex result.
