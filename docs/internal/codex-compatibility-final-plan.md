# Active Plan: Claude + Codex Compatibility

_Last updated: 2026-06-27_

## Objective

Make AI Analyst Plus genuinely usable from both Claude Code and Codex while preserving the
existing Claude Code experience. The active strategy is:

```text
Implementation plan decides what and when.
$skill-parity-review handles how for each skill migration.
```

The goal is not to copy every Claude skill into Codex. The goal is to create first-class
Codex entrypoints for high-value workflows, preserve shared analytical standards, avoid
Claude-only mechanics in Codex skills, and make compatibility testable.

## Archived Prior Plan

The previous final plan has been archived at:

```text
docs/internal/archive/codex-compatibility-final-plan-2026-06-27.md
```

Migration history and rationale also live in:

```text
docs/internal/codex-migration-plan.md
docs/internal/skill-parity-review-plan.md
```

## Current Baseline

Implemented Codex-native skills:

- `.agents/skills/independent-review/SKILL.md`
- `.agents/skills/claude-review/SKILL.md`
- `.agents/skills/skill-parity-review/SKILL.md`
- `.agents/skills/metric-spec/SKILL.md`

Supporting docs/tests:

- `.agents/skills/INDEX.md`
- `docs/codex-guide.md`
- `tests/test_codex_skills.py`
- `tests/test_codex_validation.py`

Legacy Claude skills remain under `.claude/skills/`. The legacy Claude `/codex-review`
workflow remains intentionally unchanged at:

```text
.claude/skills/codex-review/SKILL.md
```

Known local-only Codex state:

```text
.codex/internet-mode-used_DO_NOT_REMOVE_MANUALLY_SECURITY_RISK
```

This should be treated as local/session security state, not a source-controlled config.

## Operating Strategy

### 1. Use the plan for sequencing and architecture

The plan answers:

- What should be ported next?
- Which skills are high leverage?
- Which workflows are blocked by platform or MCP assumptions?
- When should shared standards be extracted?
- What docs/tests should be added before claiming parity?

### 2. Use `$skill-parity-review` for each individual migration

For each selected skill, run a request like:

```text
Use $skill-parity-review to port reliability to Codex and bring it to parity with the Claude skill.
```

or, for report-only review:

```text
Use $skill-parity-review to review reliability between Claude and Codex.
```

The skill should:

1. read the Claude skill;
2. read or detect the missing Codex skill;
3. compare with the parity rubric;
4. scaffold/update the Codex skill when requested;
5. save artifacts under `working/skill_parity_review/`;
6. update `.agents/skills/INDEX.md` when behavior changes;
7. run metadata/forbidden-reference tests;
8. report verdict, changed files, and remaining gaps.

### 3. Prefer shared standards over duplicated prompt libraries

When large provider-neutral sections appear in both Claude and Codex skills, extract them to:

```text
docs/standards/<skill-name>.md
```

Then keep `.claude/skills/...` and `.agents/skills/...` as thin wrappers with platform-
specific invocation/tooling instructions.

## Compatibility Principles

1. **Preserve Claude compatibility.** Do not rewrite or delete legacy `.claude/skills/`
   workflows unless explicitly requested and tested.
2. **Codex must have first-class entrypoints.** Codex users should not need to infer behavior
   from Claude-only slash-command docs.
3. **Outcome parity beats copy-paste parity.** Codex and Claude skills should match in intent,
   safety, artifacts, and user outcomes; mechanics may differ.
4. **Do not fake platform capabilities.** If Codex cannot do something automatically, label
   the workflow user-assisted or blocked.
5. **Separate legacy and Codex-native audit paths.** Keep legacy `/codex-review` outputs under
   `.knowledge/codex-review/`; use Codex-native paths for Codex workflows.
6. **Automate regression checks.** Use tests/scripts to validate Codex skill metadata and
   guard against legacy Claude plugin mechanics leaking into Codex skills.
7. **Port deliberately.** Prioritize high-value, low-platform-risk skills before complex
   pipeline/MCP/export workflows.

## Phase 0 — Immediate Hygiene

### Tasks

1. Ignore local Codex security/session state.

   Add to `.gitignore`:

   ```gitignore
   .codex/internet-mode-used_DO_NOT_REMOVE_MANUALLY_SECURITY_RISK
   ```

   Do not ignore all of `.codex/` unless we decide no source-controlled Codex config will be
   used.

2. Keep Codex skill tests passing:

   ```bash
   .venv/bin/python -m pytest tests/test_codex_skills.py tests/test_codex_validation.py
   ```

3. Optional: add `scripts/check_codex_compat.py` for a CLI-friendly compatibility check that
   mirrors `tests/test_codex_skills.py` and doc-reference checks.

### Acceptance Criteria

- `.codex/internet-mode-used_DO_NOT_REMOVE_MANUALLY_SECURITY_RISK` no longer appears as
  untracked noise.
- Codex skill tests pass.

## Phase 1 — Foundation Docs and Indexes

### Already implemented

- `.agents/skills/INDEX.md`
- `docs/codex-guide.md`
- README usage note for `$skill-name` invocation
- `$skill-parity-review`
- `$metric-spec`

### Remaining tasks

1. Keep `.agents/skills/INDEX.md` updated after every new Codex skill.
2. Expand `docs/codex-guide.md` as new workflows are ported.
3. Add a feature parity table to README once more skills are ported.
4. Add `docs/internal/codex-skill-migration-matrix.md` to classify every Claude skill.

## Phase 2 — Port High-Leverage Skills with `$skill-parity-review`

Port skills in this order unless user priorities change.

### 1. `reliability` — next recommended skill

Why next:

- high analytical value;
- deterministic helper already exists: `helpers/reliability_stats.py`;
- likely low MCP/platform risk;
- good test of helper-backed Codex workflow.

Command:

```text
Use $skill-parity-review to port reliability to Codex and bring it to parity with the Claude skill.
```

Expected Codex skill:

```text
.agents/skills/reliability/SKILL.md
```

Expected validation:

```bash
.venv/bin/python -m pytest tests/test_codex_skills.py tests/test_codex_validation.py
```

Consider adding focused tests if the Codex wrapper changes helper behavior.

### 2. `data-inspect`

Why:

- lets Codex inspect active dataset schema;
- prerequisite for useful analysis workflows.

Command:

```text
Use $skill-parity-review to port data-inspect to Codex and bring it to parity with the Claude skill.
```

### 3. `datasets`

Why:

- lets Codex list available datasets and status;
- pairs naturally with `data-inspect`.

### 4. `switch-dataset`

Why:

- lets Codex safely update `.knowledge/active.yaml`;
- needed before multi-dataset workflows are practical.

### 5. `question-framing`

Why:

- improves analytical quality and routing;
- less helper-dependent but core to product analytics behavior.

### 6. `data-quality-check`

Why:

- necessary before trusted analysis;
- may require careful helper/reference review.

### 7. `run-pipeline`

Why later:

- complex orchestration;
- likely depends on multiple lower-level skills;
- may expose hidden Claude slash-command or pacing assumptions.

Do not port `run-pipeline` until `data-inspect`, `datasets`, `switch-dataset`,
`question-framing`, and `data-quality-check` have Codex-native equivalents or documented
compatibility shims.

## Phase 3 — Shared Standards Extraction

After porting two or three more skills, review duplication and extract provider-neutral
standards.

Initial candidates:

- `docs/standards/metric-spec.md`
- `docs/standards/blind-review.md`
- `docs/standards/reliability.md`
- `docs/standards/data-quality-check.md`

Rules:

- Shared standards contain analytical substance and output schemas.
- Claude skills contain Claude Code slash/MCP mechanics.
- Codex skills contain Codex invocation/tool/fallback mechanics.

## Phase 4 — Migration Matrix

Create:

```text
docs/internal/codex-skill-migration-matrix.md
```

Columns:

- Claude skill
- Claude path
- Codex path
- Status: `ported`, `planned`, `compatible-as-reference`, `legacy-only`, `blocked`
- Priority
- Platform blockers
- Shared standard candidate
- Notes

Use this matrix to prevent ad hoc porting.

## Phase 5 — Agent Template Decoupling

Many `agents/*.md` files still reference `.claude/skills/...`. After the first wave of Codex
skills lands:

1. Audit references outside `.claude/`.
2. Replace direct Claude paths with neutral standard names where practical.
3. Add resolver notes:
   - Claude loads `.claude/skills/<name>/...`.
   - Codex loads `.agents/skills/<name>/SKILL.md` if available.
   - Otherwise Codex may use the Claude skill as a legacy reference only.
4. Label truly Claude-only or MCP-dependent workflows.

## Phase 6 — Pipeline and Export Compatibility

Only after foundational skills are ported:

1. Define Codex pipeline execution over `agents/registry.yaml`.
2. Port local exports before MCP-heavy exports.
3. Label Google Docs/Slides, Notion, and other MCP-backed workflows as Claude-only or
   MCP-dependent until proven in Codex.

## Current Recommended Next Move

1. Add the `.codex` local security file to `.gitignore`.
2. Run:

   ```text
   Use $skill-parity-review to port reliability to Codex and bring it to parity with the Claude skill.
   ```

3. Update `.agents/skills/INDEX.md` and `docs/codex-guide.md` if the reliability port changes
   user-facing Codex capabilities.
4. Run tests.
5. Commit.

## Adversarial Review of This Strategy

### Risk 1 — `$skill-parity-review` becomes a rubber stamp

If every port gets `COMPATIBLE_WITH_NOTES`, the process loses value.

Mitigation:

- Require category-level evidence in every parity report.
- Use `BLOCKED_BY_PLATFORM` when automation or MCP/tooling cannot be honestly reproduced.
- Keep report artifacts in `working/skill_parity_review/` for auditability.

### Risk 2 — We still create duplicate prompt libraries

Even with parity review, repeated ports can duplicate provider-neutral text.

Mitigation:

- After two or three ports, pause and extract shared standards.
- Add `shared_standard_candidates` to parity reports.

### Risk 3 — Port order ignores user value

The recommended sequence may not match actual user needs.

Mitigation:

- Treat the sequence as default, not mandatory.
- Use the migration matrix to reprioritize explicitly.

### Risk 4 — Tests validate structure but not behavior

`tests/test_codex_skills.py` catches metadata and forbidden references, not whether a skill
actually works well.

Mitigation:

- Add smoke prompts for high-value skills.
- Add helper tests when helpers are involved.
- Treat parity reports as static reviews unless evals are run.

### Risk 5 — README may overstate Codex parity

As more Codex skills are added, docs may imply full support prematurely.

Mitigation:

- Keep `docs/codex-guide.md` explicit that support is partial.
- Add a feature parity table before marketing full dual compatibility.

## Definition of Done for Each Port

A Codex skill port is done when:

- `.agents/skills/<name>/SKILL.md` exists.
- Frontmatter is valid and name matches directory.
- `.agents/skills/INDEX.md` is updated.
- `$skill-parity-review` artifacts are saved under `working/skill_parity_review/`.
- The parity report has category evidence and an honest overall verdict.
- Tests pass:

  ```bash
  .venv/bin/python -m pytest tests/test_codex_skills.py tests/test_codex_validation.py
  ```

- Any helper behavior changes have focused helper tests.
- Platform blockers or user-assisted fallbacks are documented.

## Adversarial Review Addendum: Strategy Stress Test

This addendum stress-tests the updated strategy: use the implementation plan for sequencing
and `$skill-parity-review` for each individual skill migration.

### Failure Mode 1 — The process becomes too procedural and slows useful migration

The plan adds indexes, reports, artifacts, tests, and migration-matrix expectations. This can
make every skill port feel heavier than the actual work, especially for small prompt-only
skills.

Mitigation:

- Use the full process for high-value or risky skills.
- Allow a lightweight path for low-risk skills:
  - create/update Codex skill;
  - update `.agents/skills/INDEX.md`;
  - run `tests/test_codex_skills.py`;
  - save a short parity report.
- Do not require a shared-standard extraction before there is real duplication pain.

### Failure Mode 2 — `$skill-parity-review` is treated as an implementation engine, not a reviewer

The skill can scaffold and edit Codex skills, but it is still a prompt workflow. It may miss
subtle behavioral differences, especially in skills with hidden dependencies or long examples.

Mitigation:

- Treat `$skill-parity-review` output as a static review unless smoke prompts or evals are
  run.
- For helper-backed skills, rely on helper unit tests more than prose parity.
- For high-risk skills, add at least one manual acceptance prompt and inspect the generated
  artifacts.

### Failure Mode 3 — Porting order optimizes for ease rather than user value

`reliability` is a sensible next port because it is helper-backed and low-risk, but users may
need `connect-data`, `data-inspect`, or `run-pipeline` sooner.

Mitigation:

- Keep the proposed order as a default, not a mandate.
- Add a migration matrix with two independent scores:
  - user value;
  - platform/implementation risk.
- If user value is urgent, port a higher-risk skill with explicit blockers and partial-support
  notes instead of waiting for the ideal sequence.

### Failure Mode 4 — Shared standards extraction is deferred too long

The plan says to wait until two or three more ports before extracting shared standards. That
could allow copied templates to drift quickly.

Mitigation:

- Mark shared-standard candidates in every parity report.
- Extract immediately when a section is both long and provider-neutral, such as metric
  templates, data-quality severity rules, or reliability interpretation rules.
- Keep wrappers short once a shared standard exists.

### Failure Mode 5 — Tests catch forbidden references but not misleading references

A Codex skill might avoid literal forbidden strings like `/reload-plugins` while still saying
“restart Claude Code” or assuming Claude-only MCP lifecycle behavior.

Mitigation:

- Expand compatibility checks over time from exact strings to semantic patterns:
  - Claude Code restart assumptions;
  - slash-command-only invocation;
  - MCP tools without availability checks;
  - “Claude will automatically...” phrasing in Codex skills.
- Add review checklist items for platform assumptions that are not easy to grep.

### Failure Mode 6 — The plan conflates Codex compatibility with full product parity

Adding Codex skills does not automatically make the whole product usable from Codex,
especially the pipeline, Google/Notion export, and MCP-heavy workflows.

Mitigation:

- Keep `docs/codex-guide.md` explicit that Codex support is partial.
- Add a README feature parity table before claiming dual-platform support.
- Use status labels such as `ported`, `partial`, `reference-only`, `blocked`, and
  `legacy-only`.

### Failure Mode 7 — Working-directory parity artifacts are not durable

`working/` is gitignored, so parity reports are useful locally but not durable in the repo.
Important migration rationale may be lost.

Mitigation:

- Keep detailed per-run artifacts in `working/`.
- For decisions that should survive, summarize them in durable docs:
  - `docs/internal/codex-skill-migration-matrix.md`;
  - `docs/internal/codex-migration-plan.md`;
  - relevant skill comments or index notes.
- Do not commit large run artifacts by default.

### Failure Mode 8 — Codex wrappers may become too concise

The `metric-spec` port intentionally shortened examples. That is acceptable now, but repeated
compression could remove teaching value or edge-case guidance from Codex skills.

Mitigation:

- Track “content depth” as a parity note.
- Keep critical examples when they encode non-obvious behavior.
- Move examples to shared standards when they are useful to both Claude and Codex.

### Failure Mode 9 — Legacy Claude users may be affected indirectly

Even if `.claude/skills/` files are not edited, changes to README, helpers, or shared docs
could confuse Claude users or alter expectations.

Mitigation:

- Clearly label legacy Claude workflows in docs.
- Do not repoint Claude skills to new shared standards until tested.
- Keep Claude-specific slash-command docs intact unless replacing them is a deliberate task.

### Failure Mode 10 — The plan does not yet define success metrics

Without measurable checkpoints, the migration can continue indefinitely without clear status.

Mitigation:

Add milestone metrics:

- number of Codex skills ported;
- number of high-priority workflows with Codex entrypoints;
- number of `.claude/skills` references outside `.claude/` remaining;
- test coverage for Codex skills/helpers;
- feature parity table completion;
- number of workflows marked `blocked` with explicit reasons.

### Final Adversarial Recommendation

The updated strategy is sound if treated as a **governed migration loop**, not a bureaucracy
and not an autopilot. The next best move remains:

1. ignore the local `.codex` security marker;
2. port `reliability` with `$skill-parity-review`;
3. add or update durable migration-matrix notes;
4. run focused tests;
5. only then proceed to more complex data and pipeline skills.
