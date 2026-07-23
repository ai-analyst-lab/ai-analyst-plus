# Codex Compatibility Migration Plan and Review

_Last reconstructed: 2026-06-27_

This document reconstructs the migration plan and compatibility review from the working
conversation after context was cleared. It captures both what has already been implemented
and what remains to make this repository genuinely dual-compatible with Claude Code and
Codex.

## Current Status

The repository is still primarily a Claude Code-first product analytics toolkit. A first
Codex-native compatibility layer has been added, focused on independent review workflows:

- `.agents/skills/independent-review/SKILL.md`
- `.agents/skills/claude-review/SKILL.md`
- `AGENTS.md`
- README/CLAUDE/helper documentation updates that distinguish legacy Claude workflows from
  Codex-native review skills

The legacy Claude review skill remains intentionally unchanged:

- `.claude/skills/codex-review/SKILL.md`

The latest committed migration work is:

```text
b31a658 feat(review): add codex-native review skills
```

## Original Codex-Review Migration Plan

### Summary

Keep the existing Claude-only `.claude/skills/codex-review/SKILL.md` unchanged for legacy
Claude Code users, because it depends on Claude plugin mechanics and a Claude-to-Codex
validation flow. Add a Codex-native replacement named `independent-review` that provides the
same analytical intent — blind second-pass validation — without Claude plugin assumptions.

### Key Changes

- Preserve `.claude/skills/codex-review/SKILL.md` as legacy Claude documentation and workflow.
- Do not copy it directly into `.agents/skills/codex-review/`, because its current
  instructions reference:
  - Claude slash command `/codex-review`
  - Claude plugin install commands
  - `/reload-plugins`
  - `/codex:setup`
  - `codex:codex-rescue` subagent dispatch
  - Claude-specific “no Claude fallback” framing
- Add a new Codex skill at `.agents/skills/independent-review/SKILL.md`.
- Define `independent-review` as a provider-neutral validation workflow:
  - identify the analysis or finding to validate;
  - create a blind validation brief that excludes original SQL, numbers, and conclusions;
  - run an independent re-derivation in a fresh model/session/subagent where available;
  - compare results as `AGREE`, `PARTIAL`, or `DISAGREE`;
  - save provenance artifacts.
- Store Codex-native review outputs under `.knowledge/independent-review/`, not
  `.knowledge/codex-review/`.
- Add docs language:
  - Claude users: use legacy `/codex-review`.
  - Codex users: use `$independent-review` or select `independent-review` from `/skills`.
- Update any Codex-facing docs that mention `codex-review` to point to `independent-review`
  instead.

### Replacement Skill Behavior

Frontmatter:

```yaml
name: independent-review
description: should trigger on “independent review”, “second opinion”, “validate this analysis”, “cross-check this finding”, and “blind re-derive”.
```

Workflow:

1. Resolve the finding, analysis artifact, or latest result to validate.
2. Extract only the question, dataset, metric definitions, scope, time window, and required
   data access instructions.
3. Save a blind brief to `working/independent_review/<timestamp>-<slug>/brief.md`.
4. Save the original result separately to `original_result.md`; do not include it in the
   blind brief.
5. Run an independent derivation using the best available Codex mechanism:
   - preferred: fresh Codex custom agent/subagent if configured;
   - fallback: instruct the user how to run a fresh Codex session against the brief;
   - no fallback to simply rechecking in the same context and calling it independent.
6. Save independent output to `independent_result.md`.
7. Compare results in `verdict.md` and `verdict.json`.
8. Append an audit line to `.knowledge/independent-review/log.jsonl`.
9. Report the verdict table and saved artifact paths.

### Helper Updates

- Do not modify `helpers/codex_validation.py` in the first pass unless required by tests.
- If helper reuse is desired, add a new provider-neutral wrapper later, such as
  `helpers/independent_review.py`.
- Avoid carrying over Claude-plugin checks from `codex_validation.py`, especially references
  to:
  - `~/.claude/plugins/cache`
  - `openai-codex`
  - Claude plugin setup flow.
- If logging support is needed, implement a small deterministic logger that reads
  `verdict.json` and appends to `.knowledge/independent-review/log.jsonl`.

### Adversarial Review

- Risk: keeping the name `codex-review` in Codex is confusing.
  - Mitigation: use `independent-review` for Codex and document `codex-review` as Claude
    legacy only.
- Risk: the “independent” run is not actually independent if it shares the same conversation
  context.
  - Mitigation: require a blind brief and prohibit original SQL/numbers/conclusions in that
    brief.
- Risk: Codex cannot automatically spawn a truly fresh second model/session in every
  environment.
  - Mitigation: define a user-assisted fallback that tells the user to run a fresh Codex
    session with `brief.md`; do not fake independence.
- Risk: output paths split historical audit trails.
  - Mitigation: intentionally separate `.knowledge/codex-review/` for Claude legacy and
    `.knowledge/independent-review/` for Codex-native reviews.
- Risk: the old skill’s hard gate is copied too literally and becomes nonsensical inside
  Codex.
  - Mitigation: preserve the principle “no fake validation,” but remove Claude plugin setup
    gates from the Codex skill.
- Risk: duplicate helper logic emerges.
  - Mitigation: start with a lightweight skill and only add `helpers/independent_review.py`
    if deterministic logging or validation becomes repeated.

### Test Plan

- Validate the new skill metadata:
  - `.agents/skills/independent-review/SKILL.md` exists.
  - frontmatter includes `name` and concise `description`.
  - `name` matches the directory.
- Search Codex-facing files for legacy-only references:
  - `/codex-review`
  - `codex:codex-rescue`
  - `/reload-plugins`
  - `openai/codex-plugin-cc`
  - `~/.claude/plugins`
- Confirm each remaining hit is either inside `.claude/` or explicitly labeled legacy.
- Add a small logging test if a new helper is created:
  - valid `verdict.json` appends one JSONL row;
  - malformed verdict exits safely;
  - missing audit directory is created;
  - verdict counts are deterministic.
- Manual acceptance:
  - Claude docs still mention `/codex-review`.
  - Codex docs mention `$independent-review`.
  - Codex skill does not instruct users to install Claude plugins.

### Assumptions

- Dual Codex + legacy Claude support remains the target.
- `.claude/skills/codex-review/SKILL.md` should not be deleted or rewritten during the Codex
  migration.
- Codex-native validation should optimize for honest independence over automation.
- A fresh-session/user-assisted fallback is acceptable when automatic subagent execution is
  unavailable.

## Additional Request: Codex Skill to Review Using Claude

After `independent-review` was added, the follow-up request was to create a Codex skill that
uses Claude as the independent reviewer, analogous to the legacy Claude skill that uses
Codex as reviewer.

Implemented skill:

- `.agents/skills/claude-review/SKILL.md`

### Claude Review Behavior

Purpose:

- Codex has produced an analytical result.
- The user wants Claude to independently re-derive the answer from the same data.
- Claude must receive only a blind brief, not Codex's SQL, numbers, charts, or conclusion.
- Codex then reconciles the two outputs as `AGREE`, `PARTIAL`, or `DISAGREE`.

Invocation:

```text
$claude-review [finding or artifact path]
```

or select `claude-review` from `/skills`.

Workflow:

1. Check whether Claude CLI is available:

   ```bash
   command -v claude >/dev/null 2>&1 && claude --version
   ```

2. Resolve the Codex-produced result to validate.
3. Create a blind brief under:

   ```text
   working/claude_review/<UTC-timestamp>-<question-slug>/brief.md
   ```

4. Save Codex's original output separately as:

   ```text
   codex_original.md
   ```

5. Run Claude independently where possible:

   ```bash
   claude -p "$(cat <run_dir>/brief.md)" > <run_dir>/claude_independent.md
   ```

6. If Claude CLI is unavailable, stop with user-assisted instructions rather than letting
   Codex recheck itself.
7. Compare results in:

   ```text
   verdict.md
   verdict.json
   ```

8. Append deterministic audit entry to:

   ```text
   .knowledge/claude-review/log.jsonl
   ```

### Relationship to Review Skills

- `$claude-review`: Codex-native and specifically asks Claude to validate a Codex result.
- `$independent-review`: provider-neutral; use when the reviewer model/mechanism is not
  specified.
- `/codex-review`: legacy Claude Code workflow that asks Codex to validate Claude's result.

## Implemented So Far

### Files Added

- `.agents/skills/independent-review/SKILL.md`
- `.agents/skills/claude-review/SKILL.md`
- `AGENTS.md`

### Files Updated

- `.gitignore`
  - added `.knowledge/independent-review/`
  - added `.knowledge/claude-review/`
  - relabeled `.knowledge/codex-review/` as legacy Claude audit output
- `README.md`
  - mentions `.agents/skills/`
  - mentions `$independent-review`
  - mentions `$claude-review`
  - partially reframes project as Claude/Codex-assisted
- `CLAUDE.md`
  - labels `Codex Review` as legacy Claude
  - points Codex users to `$independent-review` and `$claude-review`
- `helpers/INDEX.md`
  - labels `helpers/codex_validation.py` as legacy Claude support
- `helpers/codex_validation.py`
  - docstring now says this is legacy Claude `/codex-review` support
- `tests/test_codex_validation.py`
  - test docstrings now clarify legacy Claude support

### Verification Performed

- Metadata validation passed for:
  - `independent-review`
  - `claude-review`
- Confirmed `claude-review` does not include legacy Claude/Codex plugin mechanics:
  - `/reload-plugins`
  - `openai/codex-plugin-cc`
  - `~/.claude/plugins`
  - `/codex:setup`
  - `codex:codex-rescue`
  - `helpers/codex_validation.py`
- Focused tests passed after creating a local `.venv` and installing dev dependencies:

  ```bash
  .venv/bin/python -m pytest tests/test_codex_validation.py
  ```

  Result:

  ```text
  19 passed
  ```

## Compatibility Review: What Is Not Yet Implemented

The repo now has a good start for Codex compatibility, but it is still mostly a Claude
Code-first project with a thin Codex-native layer.

### 1. Most Claude skills have not been ported to Codex

Current snapshot from the review:

- Claude skills: `67`
- Codex skills: `2`

Codex-native skills currently exist only for:

- `$independent-review`
- `$claude-review`

The core product analytics skills are still only under `.claude/skills/`, including:

- connect data
- run pipeline
- resume pipeline
- data quality
- question framing
- metric spec
- visualization patterns
- export
- experiment
- reliability
- switch dataset
- datasets
- archive analysis
- session handoff

### 2. No Codex-native equivalent of `CLAUDE.md`

`CLAUDE.md` is still the main agent behavior document. `AGENTS.md` now exists and mentions
`.agents/skills/`, but it is much thinner than `CLAUDE.md`.

Missing: a Codex-oriented operating manual that maps the analysis workflow, rules, skill
routing, dataset handling, artifact conventions, and command equivalents for Codex.

### 3. Slash-command workflows are still Claude-specific

Many workflows are invoked as Claude slash commands:

- `/run-pipeline`
- `/connect-data`
- `/reliability`
- `/switch-dataset`
- `/datasets`
- `/data`
- `/export`
- `/experiment`
- `/history`
- `/metrics`

Codex equivalents are not implemented as `$skills`, scripts, or documented command
patterns. Codex users would need to manually infer how to run these from Claude docs.

### 4. Pipeline orchestration remains Claude-framed

The pipeline docs and skills assume “Claude orchestrates” the DAG. The agent templates in
`agents/` are model-agnostic in principle, but many reference Claude skills directly.

Review finding:

- `38` files outside `.claude` reference `.claude/skills`.

Missing: a Codex-native pipeline entrypoint that tells Codex how to:

- load `agents/registry.yaml`
- execute phases
- enforce contracts
- save artifacts
- resume from partial state
- apply validation and export steps

### 5. Agent templates still reference Claude skill paths

Many `agents/*.md` files say things like “Apply `.claude/skills/data-quality-check/skill.md`”.
That means Codex can read them as files, but they are not presented as Codex-native skills.

Possible fixes:

- port core skills into `.agents/skills/`; or
- create a compatibility shim telling Codex how to load legacy Claude skills safely; or
- refactor agent templates to refer to neutral skill names/standards.

### 6. README is only partially dual-platform

The README now mentions Codex skills, but still contains Claude-first language:

- badge says “Claude Code Required”
- quickstart says “Start Claude Code” and runs `claude`
- examples say “Claude queries the data”
- pipeline section says “Claude orchestrates”
- requirements list Claude Pro/Max

Missing: a true dual quickstart:

- Claude Code path
- Codex path
- feature parity table
- known limitations for Codex

### 7. No Codex setup guide

There is no clear “How to use this repo with Codex” doc.

Missing:

- where Codex should start
- which skills exist
- how to invoke `$independent-review` and `$claude-review`
- how to run tests
- how to connect data
- how to run analysis workflows without Claude slash commands

### 8. No Codex-native skill index

`.agents/skills/` has two skills, but no `INDEX.md` or registry.

Missing:

- list of Codex skills
- trigger phrases
- artifact locations
- relationship to legacy Claude skills
- migration status

### 9. No deterministic helper for new review logs

`$independent-review` and `$claude-review` currently embed inline Python logging snippets.
The original plan intentionally avoided adding helpers in the first pass, but this is still
a missing productization step.

Missing:

- `helpers/independent_review.py` or `helpers/review_logging.py`
- tests for:
  - valid `verdict.json`
  - malformed JSON
  - missing audit directory creation
  - deterministic verdict counts
  - `.knowledge/independent-review/`
  - `.knowledge/claude-review/`

### 10. No preflight helper for Claude review

`$claude-review` checks `command -v claude` in prose, but there is no deterministic helper
equivalent to `helpers/codex_validation.py`.

Missing:

- `helpers/claude_validation.py` or neutral `helpers/model_review.py`
- CLI/auth detection
- safe error handling
- tests

### 11. Legacy Claude plugin assumptions still exist

This is intentional for `.claude/skills/codex-review/SKILL.md`, but compatibility is not
cleanly separated everywhere.

`helpers/codex_validation.py` still checks:

- `~/.claude/plugins/cache`
- `openai-codex`

It is now labeled legacy, but Codex users could still stumble into it if docs or helpers are
not clearer.

### 12. No Codex-native reliability skill

`/reliability` is a major quality feature for Claude. Codex has no `$reliability` equivalent.

Missing:

- Codex skill wrapping `helpers/reliability_stats.py`
- artifact and audit path docs
- examples

### 13. No Codex-native data connection skill

`/connect-data`, `/setup-snowflake`, `/setup-notion`, `/datasets`, `/data`, and
`/switch-dataset` are Claude skills. Codex users can inspect helpers manually but lack guided
workflows.

Missing:

- `$connect-data`
- `$datasets`
- `$data-inspect`
- `$switch-dataset`
- Codex-specific setup docs for MCP/warehouse access

### 14. No Codex-native export/presentation workflows

Slides/docs/export functionality remains Claude skill-driven.

Missing:

- `$export`
- `$presentation-themes`
- `$google-doc-export`
- `$google-slides-export`

Also unclear how Codex should handle MCP-backed Google integrations.

### 15. No Codex-native skill creation/testing workflow

The available skill-creator skill is Claude-oriented and heavily references Claude
triggering, `claude -p`, Claude Code, and Claude eval mechanics.

Missing:

- Codex-specific skill authoring guidance
- Codex trigger eval guidance
- packaging/install conventions for `.agents/skills`

### 16. No CI/check ensuring dual compatibility

There is no test that validates:

- all `.agents/skills/*/SKILL.md` frontmatter
- Codex skill names match directories
- Codex skills do not reference Claude-only plugin mechanics
- docs do not accidentally route Codex users to Claude-only commands

Manual checks were performed, but this is not automated.

### 17. No migration matrix

There is no tracker showing which Claude skills are:

- legacy only
- Codex-compatible as-is
- ported to `.agents/skills`
- intentionally not portable
- replaced by provider-neutral skills

This would make future migration much clearer.

### 18. Untracked `.codex/` is not productized

The only `.codex` file visible during the review was:

```text
.codex/internet-mode-used_DO_NOT_REMOVE_MANUALLY_SECURITY_RISK
```

That is session/environment-specific, not a real Codex config.

Missing:

- committed Codex config if needed
- explicit `.gitignore` treatment for local `.codex` state
- docs explaining what belongs there, if anything

## Suggested Next Implementation Sequence

1. Add `docs/codex-guide.md` with a true Codex quickstart and current limitations.
2. Add `.agents/skills/INDEX.md`.
3. Add automated validation tests for `.agents/skills`.
4. Add `helpers/review_logging.py` and tests for both `$independent-review` and
   `$claude-review`.
5. Port the highest-value Claude skills:
   - `$reliability`
   - `$connect-data`
   - `$data-inspect`
   - `$question-framing`
   - `$data-quality-check`
   - `$metric-spec`
   - `$run-pipeline`
6. Refactor agent templates to refer to neutral standards instead of hardcoded
   `.claude/skills/...` paths, or add a Codex compatibility shim.
7. Update README into a true Claude/Codex dual-mode guide.

## Open Questions

- Should Codex directly reuse legacy `.claude/skills/*` content as compatibility references,
  or should every high-value skill be ported into `.agents/skills/`?
- Should the review logging helpers be provider-neutral from the start, or split by reviewer
  type (`independent-review`, `claude-review`, legacy `codex-review`)?
- Should slash-command equivalents be implemented as Codex skills only, CLI scripts only, or
  both?
- Should `.codex/` be entirely ignored as local state, or should a curated Codex config be
  committed?
