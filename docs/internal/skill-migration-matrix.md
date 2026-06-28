# Skill Migration Matrix

Tracks migration from legacy Claude skills in `.claude/skills/` to Codex-native skills in
`.agents/skills/`. Compatibility means equivalent intent, safety, artifacts, and user-facing
outcomes, not copy-paste prompt parity.

| Claude skill | Codex skill | Status | Priority | Notes |
|---|---|---:|---:|---|
| `connect-data` | `$connect-data` | Ported | P0 | Core dataset onboarding workflow. Static parity review only. |
| `datasets` | `$datasets` | Ported | P0 | Lists registry/knowledge datasets and active state. |
| `switch-dataset` | `$switch-dataset` | Ported | P0 | Includes in-progress work safeguard. |
| `data-inspect` | `$data-inspect` | Ported | P0 | Schema-only active dataset inspection. |
| `metric-spec` | `$metric-spec` | Ported | P0 | Existing Codex skill; should continue to receive parity reviews as Claude source evolves. |
| `reliability` | `$reliability` | Ported | P0 | Uses deterministic `helpers/reliability_stats.py`; independence may require manual fresh sessions. |
| `independent-review` | `$independent-review` | Ported | P0 | Provider-neutral blind validation. |
| `claude-review` | `$claude-review` | Codex-only | P0 | Codex asks Claude for blind validation. |
| `skill-parity-review` | `$skill-parity-review` | Ported | P0 | Migration utility for additional skills. |
| `data-quality-check` | `$data-quality-check` | Ported | P1 | Pre-analysis completeness, consistency, coverage, freshness, and sanity checks. |
| `run-pipeline` | `$run-pipeline` | Ported | P1 | Codex-native DAG orchestration over `agents/registry.yaml`; static parity only. |
| `resume-pipeline` | `$resume-pipeline` | Ported | P1 | Resumes from V2 state, legacy state, or consistent artifacts. |
| `experiment` | `$experiment` | Ported | P1 | Lifecycle workflow using `helpers/experiment_stats/`. |
| `compare` | `$compare` | Ported | P1 | With/without context comparison; external overlay adapter may be required. |
| `export` | `$export` | Ported | P1 | Local exports plus gated Google/Notion/receipt paths. |
| `presentation-themes` | missing | Not started | P2 | Presentation layer migration. |
| `google-doc-export` | missing | Not started | P2 | MCP/integration availability must be explicit. |
| `google-slides-export` | missing | Not started | P2 | MCP/integration availability must be explicit. |
| `notion-export` | missing | Not started | P2 | MCP/integration availability must be explicit. |
| `session-handoff` | missing | Not started | P2 | Useful for long-running Codex sessions. |

## Recommended next ports

1. `$presentation-themes`
2. `$session-handoff`
3. `$google-doc-export`
4. `$google-slides-export`
5. `$notion-export`

Use `$skill-parity-review` for each port and save review artifacts under
`working/skill_parity_review/`.
