---
name: knowledge-bootstrap
description: Load session knowledge context from `.knowledge/`: setup state, active dataset, schema, quirks, semantic layer, user profile, integrations, organization context, corrections, learnings, query archaeology, and analysis history. Use at session start, after connecting/switching datasets, or before analysis when context may be stale.
---

# Knowledge Bootstrap

## Purpose

Initialize analytical context safely and read-only so Codex knows the active dataset, user preferences, known corrections, and prior work before answering data questions.

## When to use

- a new session starts or context may be stale;
- after `$connect-data` or `$switch-dataset`;
- before analytical work that depends on active dataset knowledge;
- the user asks what context is loaded or why the analyst lacks dataset/profile awareness.

## Workflow

### 1. Load setup and active dataset

Read `.knowledge/setup-state.yaml` and `.knowledge/active.yaml` if present. Missing files are non-blocking; note setup or dataset is not initialized and suggest `$setup` or `$connect-data`.

### 2. Resolve dataset context

For an active dataset, load context from `.knowledge/datasets/{active}/` or the configured team context source when `helpers.context_sync.resolve_context_dir()` is available. Read manifest, schema, quirks, metrics index, and semantic layer files.

Semantic files to prefer before SQL:

- `semantic/entities.yaml`;
- `semantic/relationships.yaml`;
- `semantic/custom_instructions.md`;
- `semantic/dimensions.yaml`;
- `semantic/measures.yaml`;
- `semantic/filters.yaml`;
- `semantic/verified_queries.yaml`.

If `schema.md` is missing or empty, regenerate through available schema/profiling helpers or report that schema generation is needed before SQL.

### 3. Load user and org context

Read `.knowledge/user/profile.md`, `.knowledge/user/integrations.yaml`, and organization business context when linked from setup state or dataset manifest. Apply communication preferences, chart preferences, and export defaults.

### 4. Load corrections, learnings, archaeology, and history

Read summary/index files only unless the active analysis needs details:

- `.knowledge/corrections/index.yaml`;
- `.knowledge/learnings/index.md`;
- `.knowledge/query-archaeology/curated/index.yaml`;
- `.knowledge/analyses/index.yaml`;
- `.knowledge/analyses/_patterns.yaml`.

Highlight critical/high corrections internally so future SQL checks them.

### 5. Mark bootstrap completion

Write `.knowledge/.bootstrap_timestamp` when appropriate with timestamp and status. Do not modify manifests or user data beyond this lightweight completion marker unless another skill requested it.

### 6. Report readiness

Show a concise user-facing summary: dataset, table count/date range if known, metrics count, profile loaded/new, and status. Do not dump raw YAML or secrets.

## Key contracts preserved from Claude

- `.knowledge/active.yaml`
- `schema.md`
- `semantic/entities.yaml`
- `corrections`
- `.bootstrap_timestamp`

## Codex adaptation notes

- Use natural language or `$knowledge-bootstrap` invocation; do not rely on legacy slash-command-only mechanics.
- Prefer repository helpers, available MCP tools, and safe local fallbacks over provider-specific assumptions.
- Never print or commit credentials, tokens, secrets, private workspace content, or user-specific generated artifacts.
- If an external platform/tool is unavailable, state the blocker and offer the closest safe fallback.
