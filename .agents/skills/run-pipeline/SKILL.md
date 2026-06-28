---
name: run-pipeline
description: Execute a Codex-native end-to-end analysis pipeline from business question and active dataset to validated narrative, charts, and deck/export artifacts. Use when the user asks to run the full pipeline, analyze end-to-end, build a deck, investigate thoroughly, or needs a multi-phase analysis workflow.
---

# Run Pipeline

## Purpose

Run an end-to-end product analytics workflow using the repository agent registry and artifact
conventions. The goal is delivery: a validated narrative and presentation-ready outputs, not
just intermediate notes.

This is the Codex-native counterpart to the legacy Claude run-pipeline workflow. It preserves
the DAG, quality gates, artifact structure, and deck-delivery standard while adapting
execution to Codex capabilities.

## Completion guarantee

Make every reasonable effort to deliver a deck or shareable narrative. If the full DAG cannot
complete:

1. Produce a minimal viable deck or brief from completed phases.
2. Mark the pipeline state `degraded` and document skipped phases.
3. Save completed artifacts to `outputs/` and the run directory.
4. Tell the user what was completed and what `$resume-pipeline` can improve.

Do not stop with only question briefs, hypotheses, or raw inventories when enough context
exists to make a draft deliverable.

## Accepted arguments

| Argument | Required | Default | Description |
|---|---:|---|---|
| `question` | yes | — | Business question to answer |
| `data_path` | no when active dataset exists | active dataset | CSV/parquet/directory path if not using `.knowledge/active.yaml` |
| `context` | no | `stakeholder readout` | Presentation context |
| `theme` | no | `analytics` | `analytics` or `analytics-dark` |
| `audience` | no | `senior stakeholders` | Target audience |
| `dataset_name` | no | active dataset/data path slug | Naming prefix |
| `plan` | no | `full_presentation` | `full_presentation`, `deep_dive`, `quick_chart`, `refresh_deck`, `validate_only`, or agent allow-list |
| `dry-run` | no | `false` | Validate and print execution plan without running |

If required inputs are missing, ask concise clarifying questions before starting.

## Non-negotiable rules

- **Theme**: default to light `analytics`; use dark only when explicitly requested or for a
  workshop/talk context.
- **Chart title differs from slide headline**: chart title is the data claim; slide headline
  is narrative framing.
- **Chart background**: use SWD styling/warm off-white via `swd_style()` and theme helpers.
- **Recommendations**: order High → Medium → Low confidence.
- **Voice**: avoid sensational banned words and hype.
- **Pacing**: use breathing/takeaway slides every 3–4 insight slides.
- **Figsize**: charts use standard `(10, 6)` / 150 DPI unless a helper standard says
  otherwise.
- **Read agent files from disk** at each phase; do not rely on memory.
- **Cross-verification** after analysis and before storytelling; halt on low confidence.
- **Marp decks use HTML components** from `templates/marp_components.md` and skeleton from
  `templates/deck_skeleton.marp.md` when creating decks.
- **Export PDF and HTML** with `helpers/marp_export.py` when Marp CLI is available.
- **Query logging**: every SQL query gets logged via repository query logging tools.
- **Tier 1 validation**: boundary/sanity checks are always-on for data-touching analysis.
- **Data stamps**: every user-facing finding includes provenance/data stamp when available.

## Phase 0 — preflight

1. Read `agents/registry.yaml`.
2. Verify every `agent.file` exists.
3. Verify every `depends_on` and `depends_on_any` reference exists.
4. Topologically sort the dependency graph and halt on cycles.
5. Filter to agents relevant to the selected plan.
6. Compute execution tiers and dry-run display when requested.
7. Read `.knowledge/active.yaml` and active dataset schema/quirks unless a separate
   `data_path` is explicitly used.

Dry-run output should include active/skipped agents, tiers, checkpoints, and expected
artifacts. Do not execute agents during dry-run.

## Phase 1 — initialize run directory and state

Create an isolated run directory:

```text
working/runs/{YYYY-MM-DD}_{dataset}_{question-slug}/
├── working/
├── outputs/
├── pipeline_state.json
└── pipeline_metrics.json
```

Maintain `working/latest` as a symlink or pointer to the run when supported.

Initialize:

- `pipeline_state.json` with `schema_version: 2`, run id, dataset, question, plan, agent
  statuses, and `status: running`.
- `pipeline_metrics.json` with timing placeholders.
- query log in the run working directory and backward-compatible `working/query_log_*.jsonl`
  when needed.

Before creating a fresh state, detect stale `running` pipeline states older than 30 minutes.
Archive stale state if the user agrees; otherwise route to `$resume-pipeline`.

## Phase 2 — execute the DAG

Walk tiers from the registry:

1. Determine READY agents:
   - all `depends_on` agents completed;
   - at least one `depends_on_any` agent completed when present.
2. If no READY agents exist while pending agents remain, halt with a deadlock report.
3. For each READY agent:
   - mark running with timestamp;
   - assemble dynamic context;
   - read the agent file from disk;
   - execute sequentially or with fresh subagents if available.
4. On completion:
   - record status, outputs, timestamps, and errors;
   - update pipeline metrics;
   - apply degradation policy for non-critical agents;
   - halt after circuit breaker threshold of 3 critical failures in a tier.
5. Update `working/pipeline_summary.md` and run directory copies.

If Codex cannot spawn true parallel subagents in this environment, execute sequentially and
record that the run was sequential.

## Dynamic context assembly

For each agent, assemble:

- `{{DATE}}` current date;
- `{{DATASET_NAME}}` from arguments or active dataset;
- `{{ACTIVE_DATASET}}` from `.knowledge/active.yaml`;
- relevant `knowledge_context` paths from the registry, replacing `{active}`;
- output files from completed dependencies;
- user arguments: question, context, theme, audience, data path;
- query log path.

## Checkpoints

### Checkpoint 1 — frame verification

After framing/hypothesis work, verify the question is specific, decision-oriented, uses real
schema/table context, and has plausible hypotheses. Ask to proceed unless the user said “just
do it.”

### Checkpoint 2 — analysis verification

After cross-verification:

- require confidence score ≥ 8/10 where available;
- require no Tier 1a boundary failures;
- require query-log/provenance coverage sufficient for claims;
- ensure root cause is specific and actionable.

Halt or rerun analysis when verification fails.

### Checkpoint 3 — story and charts

Before deck creation, validate story arc, chart files, chart-title/headline differences,
backgrounds, banned words, and chart sizing. Run at most one chart fix loop unless the user
asks for deeper iteration.

### Checkpoint 4 — final deck

Validate:

- theme;
- recommendations ordered by confidence;
- pacing;
- HTML components;
- Marp frontmatter;
- deck size and speaker notes when expected;
- data stamps/provenance;
- receipt if Tier 3.

Run `helpers/marp_linter.py` on the deck. Export PDF/HTML via `helpers/marp_export.py` when
available; log warnings if export fails but keep the Marp deck as the primary deliverable.

## Fast path

Use a simplified path when the question is focused, inputs are complete, or time/context is
limited:

1. Abbreviate framing.
2. Run `$data-quality-check` and focused analysis.
3. Generate 2–3 key charts.
4. Create a short 5–10 slide deck or brief.
5. Export when possible.

Fast path still requires at least one chart when building a deck, documented caveats, and a
shareable output.

## Finalization

At the end:

1. Copy artifacts from root `working/` and `outputs/` into the run directory.
2. Mark state `completed` or `degraded` with `completed_at`.
3. Record export paths and metrics.
4. Note new/undefined metrics and suggest `$metric-spec`.
5. Archive or summarize analysis metadata when the archive workflow is available.
6. Report output files, checkpoint results, duration, validation status, and manual follow-ups.

## Failure handling

- Missing registry/agent file: halt during preflight.
- Data quality blocker: halt or scope around it explicitly.
- Cross-verification low confidence: halt before storytelling.
- Non-critical design/review failure: degrade with warning and continue if safe.
- Critical agent failures: halt with resume instructions.
- Export failure: warn and keep local Markdown/Marp deliverable.
