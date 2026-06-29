# Shared Skill Creator Tooling

This directory records the provider-neutral contract for skill creation and evaluation tooling.

Current state:

- Claude's legacy implementation bundles runnable scripts and viewer assets under
  `.claude/skills/skill-creator/`.
- Codex's skill-creator wrapper should prefer shared/provider-neutral tooling when it exists,
  but may reference the Claude-bundled scripts as legacy source material during migration.

Shared contract:

1. Skill bodies use `SKILL.md` with valid YAML frontmatter (`name`, `description`).
2. Large supporting material should use progressive disclosure via `references/`, `scripts/`,
   `assets/`, and `evals/`.
3. Objective skill behavior can be tested with `evals/evals.json` and assertion metadata.
4. Benchmark summaries compare with-skill vs baseline or old-skill behavior, including pass
   rate, runtime, token/cost where measurable, and qualitative output review.
5. Packaging must exclude secrets, generated outputs, and user-specific run artifacts.

Future extraction target:

Move reusable Claude-bundled scripts such as `aggregate_benchmark.py`, `generate_report.py`,
`improve_description.py`, `package_skill.py`, `quick_validate.py`, and the eval viewer into this
shared directory or a package under `helpers/` so both Claude and Codex wrappers can call the same
implementation directly.
