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
| `archaeology` | `$archaeology` | Ported | P2 | Medium Codex wrapper port; static parity only. |
| `analysis-design-spec` | `$analysis-design-spec` | Ported | P2 | Medium Codex wrapper port; static parity only. |
| `analysis-design` | `$analysis-design` | Ported | P2 | Medium Codex wrapper port; static parity only. |
| `triangulation` | `$triangulation` | Ported | P2 | Medium Codex wrapper port; static parity only. |
| `stress-test` | `$stress-test` | Ported | P2 | Medium Codex wrapper port; static parity only. |
| `experiment-brief` | `$experiment-brief` | Ported | P2 | Medium Codex wrapper port; static parity only. |
| `tracking-gaps` | `$tracking-gaps` | Ported | P2 | Medium Codex wrapper port; static parity only. |
| `data-map` | `$data-map` | Ported | P2 | Medium Codex wrapper port; static parity only. |
| `explore` | `$explore` | Ported | P2 | Medium Codex wrapper port; static parity only. |
| `causal` | `$causal` | Ported | P2 | Medium Codex wrapper port; static parity only. |
| `setup` | `$setup` | Ported | P2 | Expert/tool-heavy Codex wrapper port; static parity only. |
| `question-router` | `$question-router` | Ported | P2 | Expert/tool-heavy Codex wrapper port; static parity only. |
| `semantic-validation` | `$semantic-validation` | Ported | P2 | Expert/tool-heavy Codex wrapper port; static parity only. |
| `visualization-patterns` | `$visualization-patterns` | Ported | P2 | Expert/tool-heavy Codex wrapper port; static parity only. |
| `north-star` | `$north-star` | Ported | P2 | Expert/tool-heavy Codex wrapper port; static parity only. |
| `architect` | `$architect` | Ported | P2 | Remaining Codex wrapper port; static parity only. |
| `auth-preflight` | `$auth-preflight` | Ported | P2 | Remaining Codex wrapper port; static parity only. |
| `chart-to-drive` | `$chart-to-drive` | Ported | P2 | Remaining Codex wrapper port; static parity only. |
| `connect-snowflake` | `$connect-snowflake` | Ported | P2 | Remaining Codex wrapper port; static parity only. |
| `log-correction` | `$log-correction` | Ported | P2 | Easy/medium Codex wrapper port; static parity only. |
| `feedback-capture` | `$feedback-capture` | Ported | P2 | Easy/medium Codex wrapper port; static parity only. |
| `business` | `$business` | Ported | P2 | Easy/medium Codex wrapper port; static parity only. |
| `close-the-loop` | `$close-the-loop` | Ported | P2 | Easy/medium Codex wrapper port; static parity only. |
| `archive-analysis` | `$archive-analysis` | Ported | P2 | Easy/medium Codex wrapper port; static parity only. |
| `data-profiling` | `$data-profiling` | Ported | P2 | Easy/medium Codex wrapper port; static parity only. |
| `compare-datasets` | `$compare-datasets` | Ported | P2 | Easy/medium Codex wrapper port; static parity only. |
| `question-framing` | `$question-framing` | Ported | P2 | Easy/medium Codex wrapper port; static parity only. |
| `stakeholder-communication` | `$stakeholder-communication` | Ported | P2 | Easy/medium Codex wrapper port; static parity only. |
| `srm-check` | `$srm-check` | Ported | P2 | Easy/medium Codex wrapper port; static parity only. |
| `guardrails` | `$guardrails` | Ported | P2 | Easy/medium Codex wrapper port; static parity only. |
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
