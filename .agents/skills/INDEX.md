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
| `presentation-themes` | `.agents/skills/presentation-themes/SKILL.md` | The user is creating or reviewing stakeholder decks, Marp slides, theme selection, slide components, or speaker notes. | `themes/`, `templates/deck_skeleton.marp.md`, `templates/marp_components.md` |
| `session-handoff` | `.agents/skills/session-handoff/SKILL.md` | The user wants to save progress, pause, preserve external IDs, or continue later. | `working/session_state.yaml` |
| `google-doc-export` | `.agents/skills/google-doc-export/SKILL.md` | The user wants a Google Doc export or formatted analysis doc with local docx backup. | `outputs/*.docx`, `outputs/gdoc_export.yaml`, `working/session_state.yaml` |
| `google-slides-export` | `.agents/skills/google-slides-export/SKILL.md` | The user wants a Google Slides export or shareable online deck. | Google Slides URL/ID, `working/session_state.yaml` |
| `notion-export` | `.agents/skills/notion-export/SKILL.md` | The user wants a Notion page or Analysis Gallery entry for analysis results. | Notion page URL/ID, `working/session_state.yaml` |
| `independent-review` | `.agents/skills/independent-review/SKILL.md` | The user wants a provider-neutral blind second-pass validation, second opinion, cross-check, or independent re-derivation. | `working/independent_review/`, `.knowledge/independent-review/log.jsonl` |
| `claude-review` | `.agents/skills/claude-review/SKILL.md` | Codex produced an analysis and the user wants Claude to independently validate it from a blind brief. | `working/claude_review/`, `.knowledge/claude-review/log.jsonl` |
| `skill-parity-review` | `.agents/skills/skill-parity-review/SKILL.md` | The user wants to compare a Codex skill with its corresponding Claude skill, audit migration parity, port a Claude skill to Codex, or bring a Codex skill up to parity. | `working/skill_parity_review/` |
| `archaeology` | `.agents/skills/archaeology/SKILL.md` | Analysis can reuse known SQL patterns, table cheatsheets, or joins from query archaeology. | Query archaeology context block |
| `analysis-design-spec` | `.agents/skills/analysis-design-spec/SKILL.md` | A new analytical request needs a lightweight seven-field scope/spec before querying. | Analysis Design Spec |
| `analysis-design` | `.agents/skills/analysis-design/SKILL.md` | Complex investigation or stakeholder-feedback redesign needs a multi-stage plan. | Analysis Design Brief |
| `triangulation` | `.agents/skills/triangulation/SKILL.md` | Important findings need sanity checks across segments, tie-outs, sources, and plausibility. | Validation Report |
| `stress-test` | `.agents/skills/stress-test/SKILL.md` | User wants to challenge an analysis plan, hypothesis, or finding for failure modes. | Stress Test Scorecard |
| `experiment-brief` | `.agents/skills/experiment-brief/SKILL.md` | User has an experiment idea and needs hypothesis, primary metric, guardrails, success criteria, and feasibility. | Experiment Brief |
| `tracking-gaps` | `.agents/skills/tracking-gaps/SKILL.md` | Data needed for an analysis is missing, partial, or requires instrumentation. | Tracking Gap Report, instrumentation requests |
| `data-map` | `.agents/skills/data-map/SKILL.md` | User wants a first-contact dataset-wide overview, relationship map, and health summary. | Dataset map report, query logs |
| `explore` | `.agents/skills/explore/SKILL.md` | User wants quick interactive data exploration, table previews, or column distributions. | `working/explore_notes_*.md` |
| `causal` | `.agents/skills/causal/SKILL.md` | User asks whether a change caused an outcome or needs observational impact estimation. | `analyses/{slug}/working/`, `reports/causal_report_*.md` |
| `setup` | `.agents/skills/setup/SKILL.md` | The user wants to onboard, configure the analyst, resume setup, check setup status, or reset setup state. | `.knowledge/setup-state.yaml`, `.knowledge/user/profile.md`, `.knowledge/user/business-context.md` |
| `question-router` | `.agents/skills/question-router/SKILL.md` | An analytical request needs L1-L5 routing, pace choice, or NSM intent dispatch before execution. | L1-L5 route, pace mode, downstream skill choice |
| `semantic-validation` | `.agents/skills/semantic-validation/SKILL.md` | Analysis findings need structural/logical/business-rule/Simpson validation and confidence grading. | Semantic Validation Report, confidence grade, validation SQL |
| `visualization-patterns` | `.agents/skills/visualization-patterns/SKILL.md` | Any chart, graph, plot, or visual evidence needs SWD design standards. | `outputs/`, `working/`, chart review checklist |
| `north-star` | `.agents/skills/north-star/SKILL.md` | The user asks about North Star Metrics, NSM candidates, strategic anchor metrics, inputs, drivers, or lifecycle coaching. | `outputs/north-star/`, `.knowledge/organizations/{org}/business/north-star/profile.yaml` |
| `architect` | `.agents/skills/architect/SKILL.md` | The user wants a multi-persona project plan, implementation roadmap, wave structure, task specs, or build tracker. | `working/plans/`, `MASTER_PLAN.md`, `BUILD_STATUS.yaml` |
| `auth-preflight` | `.agents/skills/auth-preflight/SKILL.md` | Google Docs, Slides, Drive, or Workspace work needs authentication/tool availability checked before generation. | Auth status block, local fallback recommendation |
| `chart-to-drive` | `.agents/skills/chart-to-drive/SKILL.md` | Local charts/images must be uploaded to Drive for Google Docs or Slides insertion. | `working/chart_drive_manifest_*.yaml`, Drive URLs/IDs |
| `connect-snowflake` | `.agents/skills/connect-snowflake/SKILL.md` | The user wants to configure, validate, or troubleshoot a Snowflake analysis connection. | `.knowledge/datasets/{dataset}/`, `.knowledge/active.yaml` |
| `deck-critique` | `.agents/skills/deck-critique/SKILL.md` | A deck or slide draft needs scored review against stakeholder storytelling standards. | `working/deck_critique_*.md`, slide score table |
| `deck-rescue` | `.agents/skills/deck-rescue/SKILL.md` | A weak or overloaded deck needs a focused stakeholder-ready narrative rebuild. | `working/deck_rescue_*.marp.md`, `working/before_after_*.md` |
| `distribution-profiler` | `.agents/skills/distribution-profiler/SKILL.md` | A numeric metric distribution or statistical-test assumption needs profiling. | Distribution Profile report, diagnostic chart |
| `kickoff` | `.agents/skills/kickoff/SKILL.md` | The user wants to draft or post a community/Slack introduction. | `working/kickoff_intro_*.md` or Slack post |
| `codex-review` | `.agents/skills/codex-review/SKILL.md` | Legacy Codex-review requests need a safe Codex-native redirect to independent or Claude review. | Blind brief, verdict table, `$independent-review`/`$claude-review` handoff |
| `eval` | `.agents/skills/eval/SKILL.md` | The user wants to run/score the gold eval suite or compare train/test accuracy. | Gold-suite run record, accuracy/query-similarity report |
| `knowledge-bootstrap` | `.agents/skills/knowledge-bootstrap/SKILL.md` | Session or dataset context needs loading from `.knowledge/` before analysis. | `.knowledge/.bootstrap_timestamp`, readiness summary |
| `notion-ingest` | `.agents/skills/notion-ingest/SKILL.md` | Notion workspace/page/database content should populate organization knowledge. | `.knowledge/query-archaeology/raw/`, `.knowledge/organizations/` |
| `setup-dev-context` | `.agents/skills/setup-dev-context/SKILL.md` | Developers need codebase, dbt, SQL, schema, or team data conventions captured. | `.knowledge/user/dev-context.yaml` |
| `setup-notion` | `.agents/skills/setup-notion/SKILL.md` | Notion MCP/OAuth access needs configuration or verification. | Notion auth status, Analysis Gallery status |
| `setup-snowflake` | `.agents/skills/setup-snowflake/SKILL.md` | First-time Snowflake setup, connection testing, or dataset knowledge creation is needed. | `.env`/MCP guidance, `.knowledge/datasets/{dataset}/` |
| `show-off` | `.agents/skills/show-off/SKILL.md` | The user wants to share recent work with a narrative and ASCII diagram. | `working/show_off_*.md` or Slack post |
| `skill-creator` | `.agents/skills/skill-creator/SKILL.md` | The user wants to create, edit, evaluate, or package a skill. | `SKILL.md`, `evals/evals.json`, optional package/eval workspace |
| `log-correction` | `.agents/skills/log-correction/SKILL.md` | User explicitly wants to log/save/record a correction or mistake. | `.knowledge/corrections/log.yaml`, `.knowledge/corrections/index.yaml` |
| `feedback-capture` | `.agents/skills/feedback-capture/SKILL.md` | User corrects an answer, teaches a reusable preference, or asks to remember feedback. | `.knowledge/corrections/`, `.knowledge/learnings/index.md` |
| `business` | `.agents/skills/business/SKILL.md` | User wants documented business context: glossary, products, metrics, objectives, teams, or term lookup. | `.knowledge/organizations/` |
| `close-the-loop` | `.agents/skills/close-the-loop/SKILL.md` | A recommendation exists and needs owner, metric, target, check date, and fallback plan. | `working/followups/`, `.knowledge/analyses/` |
| `archive-analysis` | `.agents/skills/archive-analysis/SKILL.md` | User wants to save/archive completed analysis findings and outputs for future recall. | `.knowledge/analyses/index.yaml`, `.knowledge/datasets/{active}/manifest.yaml` |
| `data-profiling` | `.agents/skills/data-profiling/SKILL.md` | User wants table profiling for schema, nulls, distributions, freshness, keys, and outliers. | `working/data_profiles/` |
| `compare-datasets` | `.agents/skills/compare-datasets/SKILL.md` | User wants to compare metrics/findings/patterns across datasets or product lines. | `.knowledge/datasets/`, `.knowledge/analyses/` |
| `question-framing` | `.agents/skills/question-framing/SKILL.md` | User asks a broad/ambiguous analytics question that needs scoping before analysis. | Framed question block |
| `stakeholder-communication` | `.agents/skills/stakeholder-communication/SKILL.md` | Analysis output needs to be tailored to executives, product, engineering, data, or stakeholders. | Audience-adapted narrative/deck/update |
| `srm-check` | `.agents/skills/srm-check/SKILL.md` | Experiment/A-B test data or treatment/control assignment needs randomization integrity check. | SRM result table |
| `guardrails` | `.agents/skills/guardrails/SKILL.md` | A metric lift or metric definition needs guardrail checks for trade-offs. | Analysis report guardrail section |
| `forecast` | `.agents/skills/forecast/SKILL.md` | User asks to forecast, project, predict, or extrapolate a metric. | `working/forecast_*.png` |
| `teach` | `.agents/skills/teach/SKILL.md` | User asks to teach an analytics/statistics concept with visuals. | `outputs/charts/teach/` |
| `theme-picker` | `.agents/skills/theme-picker/SKILL.md` | Interactive chart/deck request needs a visual theme selection. | `working/session_state.yaml` default_theme |
| `pace` | `.agents/skills/pace/SKILL.md` | User wants to change narration/pausing/verbosity for analysis workflows. | `working/session_state.yaml` |
| `trace` | `.agents/skills/trace/SKILL.md` | User asks where a reported number came from or wants SQL provenance. | `working/trace_{analysis_id}.html` |
| `runs` | `.agents/skills/runs/SKILL.md` | User wants pipeline run history, latest run, run detail, compare runs, or cleanup. | `working/runs/`, `working/latest/`, `.knowledge/analyses/` |
| `patterns` | `.agents/skills/patterns/SKILL.md` | User asks what recurring patterns have been seen or whether a finding is known. | `.knowledge/analyses/_patterns.yaml` |
| `history` | `.agents/skills/history/SKILL.md` | User wants archived analysis history, prior findings, or similar past work. | `.knowledge/analyses/index.yaml` |
| `metrics` | `.agents/skills/metrics/SKILL.md` | User wants to browse, search, list, or explain metric definitions. | `.knowledge/datasets/{active}/metrics/` |

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
Use $presentation-themes when creating a Marp deck.
Use $session-handoff after creating an external Doc, Slide deck, or Notion page.
Use $google-doc-export to create a formatted Google Doc with local backup.
Use $google-slides-export to create a Google Slides deck when tools are available.
Use $notion-export to publish analysis to Notion when tools are available.
Use $skill-parity-review to port another Claude skill to Codex.
Use $archaeology before writing SQL for known tables/patterns.
Use $analysis-design-spec before starting analysis work.
Use $analysis-design for complex investigation planning.
Use $triangulation to sanity-check important findings.
Use $stress-test to find weaknesses before execution or presentation.
Use $experiment-brief before designing or launching an A/B test.
Use $tracking-gaps when required data is unavailable or incomplete.
Use $data-map to map a new dataset before analysis.
Use $explore to poke around data before formal analysis.
Use $causal when experiments are impossible but impact needs estimation.
Use $setup to onboard or check setup status.
Use $question-router to classify an analytical question before execution.
Use $semantic-validation to validate findings and assign confidence.
Use $visualization-patterns whenever creating or reviewing charts.
Use $north-star to explain, triage, audit, or work on an NSM.
Use $architect to create a multi-persona project plan.
Use $auth-preflight before Google Docs/Slides/Drive work.
Use $chart-to-drive to upload chart assets for Google insertion.
Use $connect-snowflake to configure a Snowflake dataset connection.
Use $deck-critique to score and improve a deck.
Use $deck-rescue to rebuild a weak deck into a focused story.
Use $distribution-profiler to profile a metric distribution and choose tests.
Use $kickoff to draft or post a community introduction.
Use $codex-review to safely route legacy Codex validation requests.
Use $eval to run a blind gold-suite evaluation.
Use $knowledge-bootstrap to load session/dataset knowledge context.
Use $notion-ingest to import Notion docs into knowledge context.
Use $setup-dev-context to capture codebase and SQL conventions.
Use $setup-notion to configure or verify Notion access.
Use $setup-snowflake to configure and test Snowflake.
Use $show-off to create a community showcase of recent work.
Use $skill-creator to create or improve a skill.
Use $log-correction to record a mistake and fix.
Use $feedback-capture when the user gives a correction or reusable preference.
Use $business to browse organization context.
Use $close-the-loop after making a recommendation.
Use $archive-analysis to save completed findings.
Use $data-profiling to profile a table before analysis.
Use $compare-datasets to compare behavior across datasets.
Use $question-framing to scope an ambiguous analytics question.
Use $stakeholder-communication to tailor findings for leadership.
Use $srm-check before analyzing experiment effects.
Use $guardrails before presenting a metric lift as a win.
Use $forecast to project a time-series metric.
Use $teach signal-vs-noise to generate a teaching visual.
Use $theme-picker to choose a chart theme.
Use $pace narrated to change workflow narration.
Use $trace to render SQL provenance for reported numbers.
Use $runs to inspect pipeline run history.
Use $patterns to search recurring findings.
Use $history to browse archived analyses.
Use $metrics to list metric definitions for the active dataset.
```

Do not use underscore slash commands such as `/skill_parity_review`; Codex treats those as unsupported built-in commands.

## Legacy Claude compatibility

- Legacy Claude skills remain under `.claude/skills/`.
- Legacy Claude `/codex-review` remains at `.claude/skills/codex-review/SKILL.md`.
- Codex users should prefer `$independent-review` for provider-neutral validation and
  `$claude-review` when Claude should validate a Codex result.
