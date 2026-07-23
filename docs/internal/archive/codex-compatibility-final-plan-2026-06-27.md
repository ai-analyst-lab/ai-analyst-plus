# Final Plan: Claude + Codex Compatibility

_Last updated: 2026-06-27_

## Objective

Make AI Analyst Plus genuinely usable from both Claude Code and Codex while preserving the
existing Claude Code experience. The end state is not “Codex can read the repo if it tries
hard enough”; the end state is that a Codex user has documented entrypoints, Codex-native
skills for the major workflows, deterministic helper/test coverage, and clear boundaries for
legacy Claude-only behavior.

## Current Baseline

The repository remains Claude-first, with an initial Codex compatibility layer.

Current migration state:

- Claude skills: `67`
- Codex skills: `2`
- Files outside `.claude/` referencing `.claude/skills`: approximately `39`
- Existing Codex-native skills:
  - `.agents/skills/independent-review/SKILL.md`
  - `.agents/skills/claude-review/SKILL.md`
- Legacy Claude review skill intentionally preserved:
  - `.claude/skills/codex-review/SKILL.md`
- Reconstructed migration history lives at:
  - `docs/internal/codex-migration-plan.md`

Known local-only Codex state:

```text
.codex/internet-mode-used_DO_NOT_REMOVE_MANUALLY_SECURITY_RISK
```

This appears to be session/security state, not source configuration, and should not be used
as the basis for productized Codex support.

## Compatibility Principles

1. **Preserve Claude compatibility.** Do not rewrite or delete legacy `.claude/skills/`
   workflows unless the replacement is explicitly tested for Claude Code users.
2. **Codex must have first-class entrypoints.** Codex users should not need to infer behavior
   from Claude-only slash command docs.
3. **Prefer provider-neutral standards where possible.** Shared analytical standards should
   be expressed once and referenced by both Claude and Codex.
4. **Do not fake independence.** Cross-model review workflows must use blind briefs and fresh
   model/session boundaries. Same-context rechecks are not independent validation.
5. **Separate legacy and Codex-native artifacts.** Keep `.knowledge/codex-review/` for legacy
   Claude `/codex-review`; use Codex-native paths such as `.knowledge/independent-review/`
   and `.knowledge/claude-review/` for Codex workflows.
6. **Automate compatibility checks.** Manual grep-based checks are useful during migration,
   but the final state should have tests or scripts that prevent regression.
7. **Do not over-port blindly.** Some `.claude/skills/` workflows are tightly coupled to
   Claude Code, MCP behavior, or slash-command semantics. Mark these explicitly rather than
   producing misleading Codex ports.

## Target End State

A dual-compatible repository should have:

- A Codex quickstart and operating guide.
- A Codex-native skill index or registry.
- Codex skills for the highest-value workflows.
- Shared deterministic helpers for review logging and validation.
- A compatibility matrix for all Claude skills.
- Agent templates that avoid hardcoded Claude-only paths where practical.
- CI or test coverage for skill metadata, forbidden legacy references, and audit logging.
- README language that accurately describes Claude and Codex support without overstating
  parity.

## Phase 0 — Guardrails and Hygiene

### Goals

Prevent accidental regression while later migration work proceeds.

### Tasks

1. Decide how to handle `.codex/`.
   - Recommended: add local/security Codex state to `.gitignore`, starting with:

     ```gitignore
     .codex/internet-mode-used_DO_NOT_REMOVE_MANUALLY_SECURITY_RISK
     ```

   - If a committed Codex config is needed later, document exactly which `.codex/` files are
     source-controlled and which are local-only.

2. Add automated validation for Codex skills.
   - Create tests that assert:
     - every `.agents/skills/*/SKILL.md` exists;
     - `name` frontmatter matches the directory;
     - `description` exists and is non-empty;
     - Codex skills do not reference forbidden Claude plugin mechanics unless explicitly
       allowed.

3. Add a compatibility grep/check script.
   - Suggested path: `scripts/check_codex_compat.py`
   - Initial checks:
     - forbidden references in `.agents/skills/`:
       - `/reload-plugins`
       - `/codex:setup`
       - `codex:codex-rescue`
       - `openai/codex-plugin-cc`
       - `~/.claude/plugins`
     - remaining `/codex-review` references outside `.claude/` must include “legacy” or be in
       explicitly allowed docs.

4. Add this plan to any internal roadmap/index if the repo uses one.

### Acceptance Criteria

- `pytest tests/test_codex_skills.py` passes.
- `python scripts/check_codex_compat.py` passes.
- `.codex` local/security state is no longer shown as untracked noise.

## Phase 1 — Codex Documentation and Entry Points

### Goals

Make it obvious how to use the repository from Codex today, including limitations.

### Tasks

1. Add a Codex guide.
   - Suggested path: `docs/codex-guide.md`
   - Include:
     - Codex quickstart;
     - how to run tests using `.venv`;
     - available Codex skills;
     - how to invoke `$independent-review` and `$claude-review`;
     - how to use existing `agents/` templates;
     - known Claude-only workflows;
     - current limitations.

2. Add a Codex skill index.
   - Suggested path: `.agents/skills/INDEX.md`
   - Include:
     - skill name;
     - trigger phrases;
     - artifact paths;
     - relationship to Claude legacy skills;
     - migration status.

3. Update README into a true dual-mode README.
   - Replace or qualify “Claude Code Required”.
   - Add separate quickstarts:
     - Claude Code quickstart;
     - Codex quickstart.
   - Add a feature parity table:

     | Workflow | Claude Code | Codex | Notes |
     |---|---:|---:|---|

4. Update `AGENTS.md` to be more Codex-operational.
   - Include common commands.
   - Explain Codex skill locations.
   - Explain how to handle legacy Claude skill references.

### Acceptance Criteria

- A new Codex user can find `docs/codex-guide.md` from README.
- README does not imply full parity where it does not exist.
- `.agents/skills/INDEX.md` accurately lists all Codex skills.

## Phase 2 — Provider-Neutral Review Infrastructure

### Goals

Replace inline logging snippets in review skills with deterministic tested helpers.

### Tasks

1. Add a provider-neutral review logging helper.
   - Suggested path: `helpers/review_logging.py`
   - Functions:
     - `count_verdicts(findings)`
     - `load_verdict(path_or_run_dir)`
     - `append_review_log(run_dir, log_dir, reviewer_default)`
   - CLI examples:

     ```bash
     python3 helpers/review_logging.py --log <run_dir> --log-dir .knowledge/independent-review --reviewer independent-review
     python3 helpers/review_logging.py --log <run_dir> --log-dir .knowledge/claude-review --reviewer claude
     ```

2. Add tests.
   - Suggested path: `tests/test_review_logging.py`
   - Cover:
     - valid `verdict.json` appends one JSONL row;
     - malformed JSON returns or raises safely;
     - missing verdict file handled cleanly;
     - unknown verdicts bucketed into `unknown`;
     - audit directory created;
     - counts are deterministic.

3. Update `.agents/skills/independent-review/SKILL.md`.
   - Replace inline Python logger with helper invocation.

4. Update `.agents/skills/claude-review/SKILL.md`.
   - Replace inline Python logger with helper invocation.

5. Consider a Claude preflight helper.
   - Suggested path: `helpers/claude_validation.py` or folded into `helpers/model_review.py`.
   - Detect:
     - `claude` CLI on PATH;
     - basic `claude --version` success;
     - optional non-interactive `claude -p` smoke test if safe.

### Acceptance Criteria

- Review skills no longer embed large logging scripts.
- `pytest tests/test_review_logging.py` passes.
- Existing `tests/test_codex_validation.py` still passes.

## Phase 3 — Migration Matrix and Skill Strategy

### Goals

Avoid ad hoc skill migration by classifying every Claude skill.

### Tasks

1. Create a migration matrix.
   - Suggested path: `docs/internal/codex-skill-migration-matrix.md`
   - Columns:
     - Claude skill;
     - current path;
     - Codex equivalent;
     - status (`ported`, `compatible-as-reference`, `legacy-only`, `blocked`, `planned`);
     - priority;
     - notes;
     - blockers.

2. Classify all `.claude/skills/*` directories.
   - Initial recommended categories:
     - **Port first:** reliability, connect-data, data-inspect, datasets, switch-dataset,
       question-framing, data-quality-check, metric-spec, run-pipeline.
     - **Reference initially:** visualization-patterns, presentation-themes, triangulation,
       stakeholder-communication.
     - **Legacy-only until MCP strategy is defined:** Google Docs/Slides, Notion, auth
       preflight, Claude plugin-specific review flows.

3. Decide the shared-standard strategy.
   - Option A: duplicate selected skills into `.agents/skills/`.
   - Option B: create provider-neutral docs under `docs/standards/` and make both Claude and
     Codex skills reference them.
   - Recommended: Option B for common analytical standards, with thin tool-specific skill
     wrappers.

### Acceptance Criteria

- Every Claude skill has an explicit migration status.
- New Codex ports are chosen from the matrix rather than guessed.

## Phase 4 — Port High-Value Codex Skills

### Goals

Make Codex useful for common analytics workflows without requiring Claude slash commands.

### Recommended Port Order

1. `$reliability`
   - Wrap `helpers/reliability_stats.py`.
   - Preserve audit trail behavior under `.knowledge/reliability/` or define a Codex-specific
     path if needed.

2. `$data-inspect`
   - Read `.knowledge/active.yaml` and dataset manifests/schema docs.
   - Provide table/column summaries.

3. `$datasets` and `$switch-dataset`
   - List known datasets.
   - Change `.knowledge/active.yaml` safely.

4. `$connect-data`
   - Provide Codex-native setup guidance for DuckDB/CSV/Postgres/Snowflake/BigQuery.
   - Avoid Claude MCP assumptions unless explicitly detected.

5. `$question-framing`
   - Port the business-question ladder and L1-L5 routing logic.

6. `$data-quality-check`
   - Port data readiness checks and severity conventions.

7. `$metric-spec`
   - Port metric definition template and validation rules.

8. `$run-pipeline`
   - Codex-native orchestrator over `agents/registry.yaml`.
   - Likely the largest port and should happen after lower-level skills are available.

### Acceptance Criteria

- Each new Codex skill has:
  - frontmatter validation;
  - docs in `.agents/skills/INDEX.md`;
  - artifact paths;
  - explicit relationship to any legacy Claude skill;
  - at least metadata tests and any deterministic helper tests.

## Phase 5 — Agent Template Decoupling

### Goals

Make `agents/*.md` usable by both Claude and Codex without hardcoded Claude-only skill paths.

### Tasks

1. Audit all references to `.claude/skills` outside `.claude/`.
2. Replace direct paths with neutral standard names where possible, such as:
   - “Data Quality Check standard”
   - “Visualization Patterns standard”
   - “Metric Spec standard”
3. Add a resolver note in `AGENTS.md`:
   - Claude should load `.claude/skills/<name>/...`.
   - Codex should load `.agents/skills/<name>/SKILL.md` if available, otherwise use the
     shared standard or legacy Claude skill as a reference only.
4. For agent templates that truly require Claude-only tools, label them explicitly.

### Acceptance Criteria

- The count of non-`.claude` files referencing `.claude/skills` decreases substantially or
  each remaining reference is justified.
- Codex users can run core agent templates without tripping over Claude-only instructions.

## Phase 6 — Pipeline and Export Compatibility

### Goals

Make the end-to-end analysis flow available to Codex, or explicitly document which parts are
not yet supported.

### Tasks

1. Define Codex pipeline execution.
   - Read `agents/registry.yaml`.
   - Execute agent prompts in dependency order.
   - Save intermediate artifacts under `working/`.
   - Save final artifacts under `outputs/`.
   - Resume from existing artifacts.

2. Port or wrap export workflows.
   - Local docx / markdown / HTML exports should come first.
   - Google Docs/Slides and Notion should wait for a clear MCP/tool availability story.

3. Add Codex acceptance examples.
   - Example: “Analyze why conversion dropped” using local CSV/DuckDB.
   - Example: run validation and produce a short report.

### Acceptance Criteria

- A Codex user can run a documented end-to-end local-data analysis.
- Unsupported export destinations are clearly labeled as Claude-only or MCP-dependent.

## Phase 7 — CI, Docs, and Release Readiness

### Goals

Make compatibility durable.

### Tasks

1. Add CI targets or documented local checks:

   ```bash
   python scripts/check_imports.py
   python scripts/check_codex_compat.py
   pytest tests/test_codex_skills.py tests/test_review_logging.py tests/test_codex_validation.py
   ```

2. Update README badges and requirements.
   - Avoid “Claude Code Required” unless the statement is scoped to Claude mode.

3. Add a changelog entry.
   - Mention Codex compatibility as partial/beta until high-value skills are ported.

4. Add release notes for users.
   - Explain legacy `/codex-review` vs `$independent-review` vs `$claude-review`.

### Acceptance Criteria

- Fresh clone instructions work for both Claude and Codex paths.
- CI/local checks catch common compatibility regressions.
- Docs accurately represent support level.

## Adversarial Review of This Final Plan

### Risk 1 — The plan creates two divergent systems

If every Claude skill is copied into `.agents/skills/`, the repo may drift into two separate
prompt libraries that disagree over time.

Mitigation:

- Prefer provider-neutral shared standards for common analytics logic.
- Keep model-specific skills thin and focused on invocation/tool mechanics.
- Add a migration matrix so duplication is deliberate.

### Risk 2 — “Codex compatibility” is overstated before parity exists

README changes could imply Codex can run the full product when only review workflows are
currently native.

Mitigation:

- Add a feature parity table.
- Label Codex support as partial/beta until core skills and pipeline are ported.
- Keep limitations visible in `docs/codex-guide.md`.

### Risk 3 — Blind review can still leak original results

Even with separate files, a model may accidentally include original SQL/numbers in the blind
brief if it is summarizing from the same context.

Mitigation:

- Add tests/lints for review brief generation only if generation becomes scripted.
- Keep review skill instructions explicit: original result goes in `*_original.md`, never in
  `brief.md`.
- Consider a checklist in `helpers/review_logging.py` or a future `helpers/blind_brief.py`.

### Risk 4 — The Claude CLI preflight is too shallow

`command -v claude` and `claude --version` do not prove a non-interactive blind review can
run successfully.

Mitigation:

- Add a deterministic `helpers/claude_validation.py` smoke test if safe.
- Treat auth/CLI success as advisory; the live run remains the real gate.
- Save failed Claude output to `blocked.md` and avoid verdicts on failed independent runs.

### Risk 5 — Codex pipeline orchestration may expose hidden Claude assumptions

The pipeline likely depends on Claude-specific pacing, slash commands, MCP behavior, or
implicit skill triggering.

Mitigation:

- Port lower-level skills first.
- Build a minimal local-data Codex pipeline before tackling MCP-heavy workflows.
- Classify MCP-heavy exports as legacy/blocked until proven.

### Risk 6 — Agent-template decoupling may reduce clarity

Replacing concrete `.claude/skills/...` paths with generic names could make instructions less
actionable.

Mitigation:

- Use a resolver table instead of vague references.
- Example: “Apply Data Quality Check standard: Claude path X, Codex path Y, shared reference
  Z.”

### Risk 7 — Tests may focus on metadata rather than actual usefulness

Skill metadata checks are necessary but insufficient; a skill can validate structurally and
still fail users.

Mitigation:

- Add at least one smoke/manual acceptance scenario per high-value Codex skill.
- For deterministic helpers, write real unit tests.
- For workflow skills, document example prompts and expected artifacts.

### Risk 8 — `.codex/` handling could accidentally hide important config

Ignoring all `.codex/` may hide future source-controlled Codex config.

Mitigation:

- Ignore only known local/security files initially.
- If a Codex source config is introduced, add explicit negation patterns and documentation.

## Recommended Immediate Next PR

The next PR should be small and infrastructure-focused:

1. Add `.gitignore` entry for the local `.codex/internet-mode-used_DO_NOT_REMOVE_MANUALLY_SECURITY_RISK` file.
2. Add `.agents/skills/INDEX.md`.
3. Add `docs/codex-guide.md` with current support level and quickstart.
4. Add `tests/test_codex_skills.py` for metadata and forbidden-reference checks.
5. Add `scripts/check_codex_compat.py` if the test alone is not enough for docs/reference
   checks.

Do not port more large workflows until the index, guide, and compatibility checks are in
place.
