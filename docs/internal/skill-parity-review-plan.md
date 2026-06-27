# Skill Parity Review Plan

_Last updated: 2026-06-27_

## Objective

Create a Codex-native skill named `skill-parity-review` that reviews a Codex skill against
the corresponding Claude skill, determines whether the Codex skill is compatible and on par,
and, when requested, updates the Codex skill without copying Claude-only mechanics.

This plan is separate from the broader Claude + Codex compatibility plan. It focuses on the
reviewer/upgrader skill that will make future skill migrations safer and more repeatable.

## Proposed Skill

Path:

```text
.agents/skills/skill-parity-review/SKILL.md
```

Frontmatter draft:

```yaml
---
name: skill-parity-review
description: Review a Codex skill against its corresponding Claude skill, identify compatibility gaps, and bring the Codex skill up to parity without copying Claude-only mechanics. Use when the user asks to compare Claude and Codex skills, port a Claude skill to Codex, make a Codex skill compatible, check skill parity, review whether a Codex skill is on par with the Claude version, or audit a skill migration.
---
```

## Core Principle

Compatibility does **not** mean copy-paste equivalence.

Claude and Codex skills should match in analytical intent, safety, expected outcomes,
artifacts, and user-facing guarantees. They may differ in invocation mechanics, tool calls,
platform-specific fallback behavior, and environment setup.

The reviewer should preserve this distinction:

| Dimension | Compatibility Standard |
|---|---|
| Analytical intent | Must match unless deliberately scoped differently |
| User outcome | Must match or explicitly document differences |
| Safety gates | Must match in principle; adapt mechanics per platform |
| Artifact/provenance expectations | Should match where possible; differences must be intentional |
| Invocation | Platform-specific adaptation is expected |
| Tool/MCP/plugin usage | Must be adapted; never blindly copied |
| Helper usage | Prefer shared/provider-neutral helpers |
| Tests/checks | Should exist for deterministic logic |

## Intended Use Cases

Use `skill-parity-review` when the user asks to:

- compare a Claude skill and Codex skill;
- check whether a Codex skill is on par with the Claude version;
- port a Claude skill to Codex;
- bring an existing Codex skill up to parity;
- audit a skill migration;
- identify Claude-only mechanics that leaked into a Codex skill;
- produce a migration gap report before editing;
- update a Codex skill while preserving legacy Claude behavior.

## Non-Goals

The skill should not:

- rewrite the Claude skill unless explicitly asked;
- blindly copy `.claude/skills/*` content into `.agents/skills/*`;
- claim parity when a platform capability is missing;
- hide user-assisted fallbacks as automation;
- port MCP-heavy workflows without labeling tool requirements;
- replace the broader migration matrix or compatibility plan.

## Compatibility Rubric

Each review should evaluate the following categories.

### 1. Metadata Parity

Check:

- Codex skill has required frontmatter.
- `name` matches the Codex skill directory.
- `description` captures the same user intent as the Claude skill.
- Codex description uses Codex-native trigger language.
- Description does not rely solely on Claude slash commands.

Possible findings:

- missing frontmatter;
- weak trigger coverage;
- overtriggering description;
- Claude-only command references;
- mismatched skill name.

### 2. Intent Parity

Check:

- Does the Codex skill solve the same underlying user problem?
- Are the same analytical standards preserved?
- Did the Codex skill omit a critical decision gate?
- Did the Codex skill broaden or narrow the scope without saying so?

### 3. Workflow Parity

Compare:

- step order;
- required inputs;
- preflight checks;
- user clarification points;
- validation logic;
- output contract;
- failure behavior;
- final reporting.

The workflow does not need identical wording, but critical outcomes should be represented.

### 4. Artifact and Provenance Parity

Check:

- working directory conventions;
- output filenames;
- audit log locations;
- JSON schema shapes;
- saved before/after artifacts;
- query logging and provenance requirements.

Provider-specific artifact paths are acceptable when explicitly justified.

### 5. Platform Assumption Safety

Flag Claude-only mechanics in Codex skills, including:

- `/reload-plugins`
- `/codex:setup`
- `/plugin install`
- `codex:codex-rescue`
- `~/.claude/plugins`
- “Claude must...” when referring to the current agent rather than a reviewer model;
- Claude Code restart gates;
- Claude-specific MCP assumptions not available to Codex.

Also flag Codex-only assumptions if the review is being used in the reverse direction.

### 6. Safety and Truthfulness Parity

Check:

- blocker conditions are preserved;
- the Codex skill does not fake unavailable automation;
- privacy/credential warnings are retained;
- data access instructions remain safe;
- blind-review workflows do not leak original SQL, numbers, or conclusions;
- confidence/validation claims are not overstated.

### 7. Helper and Script Parity

Check:

- helper calls in the Claude skill;
- whether those helpers are provider-neutral or Claude-specific;
- whether the Codex skill should reuse the helper, avoid it, or use a new wrapper;
- whether helper changes require tests.

### 8. Testability Parity

Check whether the migration should add or update:

- metadata/frontmatter tests;
- forbidden-reference checks;
- helper unit tests;
- artifact schema tests;
- smoke prompts;
- acceptance criteria.

### 9. Documentation Parity

Check whether the change should update:

- `.agents/skills/INDEX.md`;
- `docs/codex-guide.md`;
- `docs/internal/codex-skill-migration-matrix.md`;
- README feature parity table;
- broader compatibility plans.

## Verdict System

Per-category verdicts:

```text
PASS
MINOR_GAP
MAJOR_GAP
BLOCKED
NOT_APPLICABLE
```

Overall verdicts:

```text
COMPATIBLE
COMPATIBLE_WITH_NOTES
NEEDS_PORTING
BLOCKED_BY_PLATFORM
LEGACY_ONLY
```

Severity labels for gaps:

```text
INFO
MINOR
MAJOR
BLOCKER
```

## Expected Artifacts

Each run should create:

```text
working/skill_parity_review/<timestamp>-<skill-name>/
├── claude_skill.md
├── codex_skill_before.md
├── parity_report.md
├── parity_report.json
├── codex_skill_after.md        # only when the Codex skill is changed
├── patch.diff                  # when practical
└── notes.md                    # optional assumptions, blockers, or user decisions
```

The reviewer should save before/after copies when it edits the Codex skill.

## Report Schema

`parity_report.json` should follow this shape:

```json
{
  "skill": "<skill-name>",
  "claude_path": ".claude/skills/<skill-name>/skill.md",
  "codex_path": ".agents/skills/<skill-name>/SKILL.md",
  "overall": "COMPATIBLE|COMPATIBLE_WITH_NOTES|NEEDS_PORTING|BLOCKED_BY_PLATFORM|LEGACY_ONLY",
  "categories": [
    {
      "name": "intent_parity",
      "verdict": "PASS|MINOR_GAP|MAJOR_GAP|BLOCKED|NOT_APPLICABLE",
      "evidence": "<short evidence>"
    }
  ],
  "gaps": [
    {
      "severity": "INFO|MINOR|MAJOR|BLOCKER",
      "category": "<category>",
      "issue": "<gap>",
      "recommendation": "<fix>"
    }
  ],
  "files_changed": [
    "<path>"
  ]
}
```

## Skill Workflow

### Step 1 — Resolve Skill Pair

Accept any of:

- explicit Claude skill path;
- explicit Codex skill path;
- skill name;
- migration request such as “port data-quality-check”.

Resolve likely paths:

```text
.claude/skills/<name>/SKILL.md
.claude/skills/<name>/skill.md
.agents/skills/<name>/SKILL.md
```

If the Codex skill does not exist and the user asked to port or bring to parity, scaffold a
new Codex skill. If the user only asked to review, report that the Codex skill is missing.

### Step 2 — Read Both Skills Fully

Read the Claude skill and Codex skill in full. If either skill references directly relevant
bundled resources needed to understand the workflow, read only those resources required for
the parity decision.

Do not chase unrelated resources.

### Step 3 — Extract Skill Dimensions

For each skill, identify:

- intent;
- trigger language;
- workflow steps;
- required inputs;
- preflight checks;
- safety gates;
- helper/script calls;
- external tools/MCP assumptions;
- artifacts and output paths;
- output schema/report format;
- edge cases;
- tests or validation hooks.

### Step 4 — Compare with Rubric

Evaluate all compatibility categories and assign per-category verdicts. Capture evidence in
plain language and, where possible, quote short path/section references.

### Step 5 — Decide Whether to Edit

Default behavior:

- If the user asks to “review”, produce the report and proposed changes only.
- If the user asks to “bring to parity”, “fix”, “port”, or “update”, edit the Codex skill.
- Never edit the Claude skill unless explicitly requested.

Before editing, classify gaps:

- safe to fix directly;
- needs user decision;
- blocked by platform capability;
- should be handled in shared docs/helper instead of the skill.

### Step 6 — Update Codex Skill Safely

When editing the Codex skill:

- preserve Codex-native invocation language;
- preserve provider-neutral analytical standards;
- remove Claude-only mechanics;
- add user-assisted fallbacks for unavailable automation;
- document intentional differences from Claude;
- keep frontmatter valid;
- avoid overlong copy-paste ports where shared references would be better.

If creating a new Codex skill, scaffold:

```text
.agents/skills/<name>/SKILL.md
```

with a valid `name` and `description`, then adapt the workflow using the compatibility
rubric.

### Step 7 — Save Artifacts

Create the run directory and write:

- `claude_skill.md`;
- `codex_skill_before.md`;
- `parity_report.md`;
- `parity_report.json`;
- `codex_skill_after.md` if edited;
- `patch.diff` if practical;
- `notes.md` for blockers or assumptions.

### Step 8 — Validate

Run applicable checks:

- frontmatter/name match for edited Codex skill;
- forbidden-reference grep for Codex skill;
- helper unit tests if helpers changed;
- focused skill tests if available.

Suggested forbidden reference check for Codex skills:

```text
/reload-plugins
/codex:setup
codex:codex-rescue
openai/codex-plugin-cc
~/.claude/plugins
```

### Step 9 — Report to User

Report:

- overall verdict;
- category table;
- top gaps fixed or remaining;
- files changed;
- artifact paths;
- validation commands run;
- recommended next action.

## Compatibility Model for Long-Term Maintenance

The best long-term model is three-layered.

### Layer 1 — Shared Standard

Provider-neutral analytical instructions live in shared documentation, for example:

```text
docs/standards/<skill-name>.md
```

Shared standards should contain:

- analytical principles;
- required inputs;
- validation criteria;
- artifact expectations;
- examples;
- output schemas.

They should avoid Claude/Codex invocation mechanics.

### Layer 2 — Claude Wrapper Skill

Claude-specific wrappers live under:

```text
.claude/skills/<skill-name>/skill.md
```

or:

```text
.claude/skills/<skill-name>/SKILL.md
```

They contain:

- Claude Code slash-command semantics;
- Claude/MCP/plugin assumptions;
- references to the shared standard;
- Claude-specific fallback behavior.

### Layer 3 — Codex Wrapper Skill

Codex-specific wrappers live under:

```text
.agents/skills/<skill-name>/SKILL.md
```

They contain:

- Codex trigger phrasing;
- Codex-safe tool assumptions;
- Codex artifact paths where different;
- user-assisted fallbacks for unavailable automation;
- references to the shared standard.

This model avoids two large prompt libraries drifting apart.

## Adversarial Review

### Risk 1 — The reviewer overfits to textual similarity

A naive parity review may treat wording differences as gaps while missing deeper behavioral
mismatches.

Mitigation:

- The rubric prioritizes intent, outcomes, safety, artifacts, and platform assumptions over
  exact wording.
- The report should include evidence and explain why a difference matters.

### Risk 2 — The reviewer copies Claude-only mechanics into Codex

When asked to “bring to parity,” the model may paste Claude slash commands, plugin setup, or
MCP assumptions into the Codex skill.

Mitigation:

- The skill must maintain a forbidden-reference list.
- Platform-specific mechanics should be adapted, not copied.
- Validation should grep edited Codex skills for known Claude-only mechanics.

### Risk 3 — The reviewer weakens the Claude skill by editing it

A migration task could accidentally modify legacy Claude behavior.

Mitigation:

- Default rule: never edit the Claude skill unless explicitly requested.
- Save `claude_skill.md` as input evidence, not as an edit target.

### Risk 4 — The reviewer claims parity despite missing platform capabilities

For example, a Claude skill might rely on MCP tools that Codex cannot access in the current
environment.

Mitigation:

- Use `BLOCKED_BY_PLATFORM` when a critical feature cannot be implemented honestly.
- Add user-assisted fallback instructions when appropriate.
- Document unsupported workflows rather than pretending parity.

### Risk 5 — The skill creates too many one-off Codex ports

If every review creates a full copied Codex skill, maintenance burden will grow quickly.

Mitigation:

- Prefer shared `docs/standards/` references for provider-neutral logic.
- Keep wrappers thin where possible.
- Recommend shared helper/doc extraction when duplicate logic grows.

### Risk 6 — Reports become too verbose to act on

A full rubric can produce long reports that obscure the top fixes.

Mitigation:

- The final user response should lead with the overall verdict and top 3 gaps.
- Detailed category evidence goes into `parity_report.md`/`.json`.

### Risk 7 — Missing Codex skill scaffolding is ambiguous

If no Codex skill exists, “review parity” and “create a port” are different tasks.

Mitigation:

- If the user says “review,” report `NEEDS_PORTING` and stop.
- If the user says “port,” “bring to parity,” or “create,” scaffold the Codex skill.

### Risk 8 — The reviewer misses bundled resources

Some Claude skills rely on referenced files in `references/`, `scripts/`, or `assets/`.

Mitigation:

- Step 2 allows reading directly relevant bundled resources.
- Do not chase unrelated resources; document unreviewed dependencies if they may matter.

## Acceptance Criteria for Implementing `skill-parity-review`

The implementation is acceptable when:

- `.agents/skills/skill-parity-review/SKILL.md` exists.
- Frontmatter `name` is exactly `skill-parity-review`.
- Description includes compare/port/parity/compatibility trigger language.
- The skill contains the compatibility rubric.
- The skill contains the verdict system.
- The skill contains the artifact contract.
- The skill says not to edit Claude skills unless explicitly asked.
- The skill includes forbidden Claude-only mechanics for Codex skills.
- The skill supports both report-only and edit-to-parity modes.
- Metadata validation passes.

## Recommended Implementation Steps

1. Create `.agents/skills/skill-parity-review/SKILL.md` from this plan.
2. Optionally create `.agents/skills/INDEX.md` and list the skill.
3. Add metadata/forbidden-reference tests for Codex skills.
4. Use `skill-parity-review` on the next target skill migration, likely one of:
   - reliability;
   - data-inspect;
   - datasets;
   - switch-dataset;
   - metric-spec.
5. After two or three real migrations, reassess whether a helper script is needed for report
   scaffolding or JSON generation.

## Second Adversarial Review and Final Decisions

This second review challenges the plan from the perspective of implementation failure modes,
maintenance cost, and user trust.

### Challenge 1 — “On par” may be interpreted as feature-identical

A user may expect the Codex skill to support every Claude feature, including slash commands,
Claude Code MCP servers, plugin-specific subagents, or browser/session behavior. That is not
always possible or desirable.

Final decision:

- Define “on par” as **outcome-compatible** rather than feature-identical.
- The parity report must separate:
  - shared analytical requirements;
  - platform-specific mechanics;
  - unsupported or user-assisted features;
  - intentional differences.
- If a critical Claude feature cannot be implemented in Codex, the verdict should be
  `BLOCKED_BY_PLATFORM`, not `COMPATIBLE_WITH_NOTES`.

### Challenge 2 — The skill may make risky edits too eagerly

A “bring to parity” instruction could cause the reviewer to rewrite a Codex skill heavily,
possibly introducing regressions or removing deliberate Codex-native behavior.

Final decision:

- The skill should edit only the Codex skill by default.
- The skill should preserve a `codex_skill_before.md` artifact before editing.
- The skill should classify changes as:
  - safe direct edits;
  - needs user decision;
  - blocked by platform;
  - better handled in shared standards/helpers.
- Major rewrites should be staged as proposed patches unless the user explicitly asked for
  direct implementation.

### Challenge 3 — The reviewer may under-detect hidden dependencies

Claude skills often rely on referenced files, helper scripts, hooks, MCP settings, or implicit
Claude Code behavior. A shallow comparison of only `skill.md`/`SKILL.md` can miss those
requirements.

Final decision:

- The skill must inspect directly referenced resources that are necessary to understand the
  workflow.
- The report must include a `dependencies_reviewed` section and a `dependencies_not_reviewed`
  section when relevant.
- If important referenced resources are missing or too large to inspect safely, the category
  should be `BLOCKED` or `MAJOR_GAP`, not assumed compatible.

### Challenge 4 — The skill could normalize duplication instead of reducing it

Repeated parity reviews may create large Codex copies of Claude skills, increasing drift and
maintenance burden.

Final decision:

- The reviewer should explicitly recommend shared standards when large provider-neutral
  sections are duplicated.
- The report should include a `shared_standard_candidate` boolean or note when applicable.
- For substantial migrations, prefer this architecture:

  ```text
  docs/standards/<skill-name>.md         # provider-neutral substance
  .claude/skills/<skill-name>/skill.md   # Claude wrapper
  .agents/skills/<skill-name>/SKILL.md   # Codex wrapper
  ```

### Challenge 5 — The report schema may become stale as migrations evolve

A rigid JSON schema may not capture all useful migration details, especially for MCP-heavy
or multi-file skills.

Final decision:

- Keep the core JSON fields stable but allow optional extension fields.
- Required fields remain:
  - `skill`
  - `claude_path`
  - `codex_path`
  - `overall`
  - `categories`
  - `gaps`
  - `files_changed`
- Optional fields may include:
  - `dependencies_reviewed`
  - `dependencies_not_reviewed`
  - `shared_standard_candidates`
  - `platform_blockers`
  - `user_decisions_needed`

### Challenge 6 — The skill may conflate “migration review” with “quality review”

A Codex skill can be faithful to a Claude skill even if the Claude skill itself is flawed.
The reviewer may accidentally validate bad shared logic instead of only parity.

Final decision:

- The primary verdict is parity, not intrinsic quality.
- The report may include a separate `quality_notes` section for problems present in both
  skills.
- Shared flaws should not be marked as Codex parity gaps unless the Codex port worsens them.

### Challenge 7 — The skill may be unable to prove behavioral parity without evals

Prompt workflows are probabilistic. Static review can find obvious gaps, but it cannot prove
that Claude and Codex skills behave identically in real use.

Final decision:

- The skill should call its output a **static parity review** unless it also runs evals.
- For high-value skills, it should recommend smoke prompts or evals.
- The implementation should not require eval infrastructure on day one, but it should leave a
  clear path to add it.

### Challenge 8 — The reviewer itself can be triggered too broadly

If the skill description is too broad, it might trigger for ordinary code review or product
review requests.

Final decision:

- The description should emphasize **Claude/Codex skill parity**, **skill migration**, and
  **`.claude/skills` vs `.agents/skills`**.
- Avoid generic “review this skill” language unless paired with compatibility, parity, or
  migration context.

## Final Plan Summary

Proceed with `skill-parity-review` as a Codex-native skill, but implement it as a structured
static parity reviewer and guarded Codex-skill updater, not as an automatic proof of behavior.

Final implementation requirements:

1. Create `.agents/skills/skill-parity-review/SKILL.md`.
2. Use the name `skill-parity-review` exactly.
3. Make the skill compare `.claude/skills/<name>/(skill.md|SKILL.md)` with
   `.agents/skills/<name>/SKILL.md`.
4. Default to report-only mode unless the user asks to port, fix, update, or bring to parity.
5. Edit only Codex skills by default; never edit Claude skills unless explicitly requested.
6. Save run artifacts under:

   ```text
   working/skill_parity_review/<timestamp>-<skill-name>/
   ```

7. Use outcome-compatible parity, not copy-paste parity.
8. Preserve or recommend shared standards for provider-neutral logic.
9. Flag platform blockers honestly.
10. Validate edited Codex skills for frontmatter and forbidden Claude-only mechanics.
11. Report static parity limitations and recommend evals for high-value workflows.

Final acceptance checklist:

- [ ] `.agents/skills/skill-parity-review/SKILL.md` exists.
- [ ] Frontmatter `name` equals `skill-parity-review`.
- [ ] Description targets Claude/Codex skill parity and migration, not generic reviews.
- [ ] Skill includes the compatibility rubric.
- [ ] Skill includes the per-category and overall verdict systems.
- [ ] Skill includes artifact paths and JSON report schema.
- [ ] Skill distinguishes report-only mode from edit-to-parity mode.
- [ ] Skill forbids editing Claude skills unless explicitly requested.
- [ ] Skill has forbidden-reference checks for Codex skills.
- [ ] Skill requires platform blockers to be surfaced instead of hidden.
- [ ] Skill encourages shared standards rather than duplicated ports.
- [ ] Metadata validation passes after implementation.
