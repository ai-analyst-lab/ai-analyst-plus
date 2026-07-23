# Shared Skill Resource Optimization Plan

Status: planned for a future PR.

Origin: captured from the Claude/Codex skill shared-resource audit after moving the North Star wiki corpus to `shared/north-star/wiki/`.

Scope: static scan of `.claude/skills/`, `.agents/skills/`, `shared/`, `docs/standards/`, and helper references after the North Star wiki relocation.

## What I looked for

- Provider-neutral corpora/assets/scripts/resources stored under `.claude/skills/*` but referenced or useful from Codex.
- Byte-identical resources duplicated under `.claude/skills/*` and `.agents/skills/*`.
- Codex skill files that directly reference `.claude/skills/<skill>/...` support resources.
- Existing shared-resource patterns that should be extended.

## High-confidence optimization opportunities

### 1. North Star remaining playbook files

Current state:

- `shared/north-star/wiki/` now holds the former Claude-only wiki corpus.
- `.claude/skills/north-star/wiki` is now a compatibility symlink.
- Codex still references `.claude/skills/north-star/_lib/core_principles.md` for framework claims.
- Claude-only support files remain:
  - `.claude/skills/north-star/_lib/core_principles.md`
  - `.claude/skills/north-star/verbs/audit.md`
  - `.claude/skills/north-star/verbs/drivers.md`
  - `.claude/skills/north-star/verbs/explain.md`
  - `.claude/skills/north-star/verbs/inputs.md`
  - `.claude/skills/north-star/verbs/triage.md`

Recommendation:

- Move `_lib/core_principles.md` and `verbs/*.md` to a provider-neutral location, e.g.:
  - `shared/north-star/_lib/core_principles.md`
  - `shared/north-star/verbs/*.md`
- Leave compatibility symlinks in `.claude/skills/north-star/_lib` and `.claude/skills/north-star/verbs`, or update the Claude skill to point directly to `shared/north-star/...`.
- Update Codex skill to read `shared/north-star/_lib/core_principles.md` instead of `.claude/...`.

Claude skill modification needed: **Yes** if direct paths are changed; **optional** if symlinks are left and only Codex is updated. Preferred: update `.claude/skills/north-star/skill.md` to make `shared/north-star/...` the canonical source.

### 2. Skill Creator bundled tooling

Current state:

- Codex `skill-creator` explicitly treats Claude-bundled scripts as legacy source material:
  - `.claude/skills/skill-creator/scripts/`
  - `.claude/skills/skill-creator/eval-viewer/`
- Provider-neutral contract exists at `shared/skill-creator/README.md`, but implementation remains Claude-bundled.
- Claude-only support files include:
  - `scripts/*.py`
  - `eval-viewer/generate_review.py`
  - `eval-viewer/viewer.html`
  - `references/schemas.md`
  - `agents/analyzer.md`
  - `agents/comparator.md`
  - `agents/grader.md`
  - `assets/eval_review.html`
  - `LICENSE.txt`

Recommendation:

- Extract reusable implementation to `shared/skill-creator/` or `helpers/skill_creator/`:
  - `shared/skill-creator/scripts/*.py`
  - `shared/skill-creator/eval-viewer/*`
  - `shared/skill-creator/references/schemas.md`
  - `shared/skill-creator/agents/*.md`
  - `shared/skill-creator/assets/*`
- Update both Claude and Codex skills to call/read the shared locations.
- Leave `.claude/skills/skill-creator/*` compatibility symlinks if legacy Claude invocation expects relative paths.
- Update `tests/test_codex_skills.py` shared-content contract, which currently expects Codex to reference `.claude/skills/skill-creator/scripts/`.

Claude skill modification needed: **Yes**. `.claude/skills/skill-creator/SKILL.md` currently instructs relative `agents/`, `references/`, `scripts/`, and `eval-viewer/` paths. It should declare `shared/skill-creator/` as canonical or rely on compatibility symlinks.

### 3. Teach topic wrappers

Current state:

- Core implementation is already shared:
  - `shared/teach/topics/signal_vs_noise.py`
- Claude and Codex each have byte-identical compatibility wrappers:
  - `.claude/skills/teach/topics/signal_vs_noise.py`
  - `.agents/skills/teach/topics/signal_vs_noise.py`

Recommendation:

- Low-risk cleanup: remove duplicate wrapper files and update both skill docs to run `shared/teach/topics/signal_vs_noise.py` directly; or replace wrapper files with symlinks.
- Current setup is already mostly optimized; this is a small dedupe rather than a blocker.

Claude skill modification needed: **Optional**. Required only if removing the `.claude/skills/teach/topics/` compatibility wrapper or changing instructions to no longer mention it.

### 4. Distribution Profiler eval prompts

Current state:

- Claude has `.claude/skills/distribution-profiler/evals/evals.json`.
- Codex has no equivalent eval resource.
- The eval prompts are provider-neutral test assets.

Recommendation:

- Move to `shared/distribution-profiler/evals/evals.json` or a repo-level eval suite location.
- Update any eval runner/docs to read from the shared path.
- If neither skill references this file, this is mostly repository hygiene rather than runtime behavior.

Claude skill modification needed: **Probably no skill-body change** unless the Claude skill or eval tooling starts documenting the new path. File relocation may still require test/eval runner updates.

### 5. Run Pipeline `plans.md`

Current state:

- Claude has `.claude/skills/run-pipeline/plans.md`.
- Codex `run-pipeline` is a wrapper and does not reference this file.
- The file appears to be a plan/design artifact rather than runtime instructions.

Recommendation:

- Archive or move to `docs/internal/` if it is historical design context.
- If it is still intended as runtime guidance, move to `shared/run-pipeline/plans.md` and reference from both wrappers.

Claude skill modification needed: **Likely no** if archived; **yes** only if the Claude skill should actively read it after move.

## Existing good shared patterns to preserve

These are already provider-neutral and do not need the same treatment:

- `architect` uses `shared/PLANNING_METHODOLOGY.md` from both wrappers.
- `data-quality-check` has `docs/standards/data-quality-check.md` as shared standard.
- `causal`, `experiment`, `semantic-validation`, `visualization-patterns`, and related analytical skills mostly use provider-neutral helpers under `helpers/`.
- `north-star` helper code already lives under `helpers/north_star/`.
- `teach` core topic code already lives under `shared/teach/topics/`.

## Claude skills that would require modifications if we apply all recommended optimizations

Required:

1. `.claude/skills/north-star/skill.md`
   - Update canonical references for `_lib/core_principles.md`, `verbs/*.md`, and probably `wiki/...` to `shared/north-star/...`.

2. `.claude/skills/skill-creator/SKILL.md`
   - Update relative references to `scripts/`, `references/`, `agents/`, `assets/`, and `eval-viewer/` to shared paths or document compatibility symlinks.

Conditional / optional:

3. `.claude/skills/teach/skill.md`
   - Only if removing or symlinking the duplicate wrapper under `.claude/skills/teach/topics/`.

4. `.claude/skills/distribution-profiler/skill.md`
   - Only if we want the skill body to document/use the shared eval path. The current skill body does not appear to depend on the eval file path.

5. `.claude/skills/run-pipeline/skill.md`
   - Only if `plans.md` is converted from historical sidecar into shared runtime guidance.

## Suggested implementation order

1. Finish North Star by moving `_lib/` and `verbs/` into `shared/north-star/`.
2. Extract Skill Creator tooling into `shared/skill-creator/` and update both wrappers/tests.
3. Optionally replace Teach wrappers with symlinks or direct shared-script invocation.
4. Move Distribution Profiler evals to shared eval assets if there is an eval runner that consumes them.
5. Decide whether `run-pipeline/plans.md` is historical docs or runtime shared guidance.
