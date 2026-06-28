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
| `presentation-themes` | `$presentation-themes` | Ported | P2 | Marp/theme/deck structure standards. |
| `google-doc-export` | `$google-doc-export` | Ported | P2 | Docx-first Google Doc workflow; live upload requires tools/auth. |
| `google-slides-export` | `$google-slides-export` | Ported | P2 | Google Slides API safety/layout workflow; live export requires tools/auth. |
| `notion-export` | `$notion-export` | Ported | P2 | Notion page/gallery workflow; live export requires tools/auth. |
| `session-handoff` | `$session-handoff` | Ported | P2 | Saves state to `working/session_state.yaml`. |
| `forecast` | `$forecast` | Ported | P2 | Easy/medium Codex wrapper port; static parity only. |
| `teach` | `$teach` | Ported | P2 | Easy/medium Codex wrapper port; static parity only. |
| `theme-picker` | `$theme-picker` | Ported | P2 | Easy/medium Codex wrapper port; static parity only. |
| `pace` | `$pace` | Ported | P2 | Easy/medium Codex wrapper port; static parity only. |
| `trace` | `$trace` | Ported | P2 | Easy/medium Codex wrapper port; static parity only. |
| `runs` | `$runs` | Ported | P2 | Easy/medium Codex wrapper port; static parity only. |
| `patterns` | `$patterns` | Ported | P2 | Easy/medium Codex wrapper port; static parity only. |
| `history` | `$history` | Ported | P2 | Easy/medium Codex wrapper port; static parity only. |
| `metrics` | `$metrics` | Ported | P2 | Easy/medium Codex wrapper port; static parity only. |

## Recommended next ports

1. `$data-quality-check` shared standard extraction
2. `$run-pipeline` coded dry-run/runtime helper hardening
3. External integration tests for `$google-doc-export`, `$google-slides-export`, and `$notion-export`
4. Remaining expert/tool-heavy skills as needed (`setup`, `question-router`, `semantic-validation`, `visualization-patterns`, `north-star`)

Use `$skill-parity-review` for each port and save review artifacts under
`working/skill_parity_review/`.
