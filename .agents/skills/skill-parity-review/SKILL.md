---
name: skill-parity-review
description: Review a Codex skill against its corresponding Claude skill for Claude/Codex skill parity and migration compatibility, then optionally bring the Codex skill up to parity without copying Claude-only mechanics. Use when the user asks to compare .claude/skills and .agents/skills, port a Claude skill to Codex, make a Codex skill compatible, check skill parity, audit a skill migration, or verify a Codex skill is on par with the Claude version.
---

# Skill Parity Review

## Purpose

Use this skill to perform a structured static parity review between a Claude skill and its
Codex counterpart. The goal is to determine whether the Codex skill is outcome-compatible
with the Claude skill, identify gaps, and, when the user asks for it, update only the Codex
skill to close safe gaps.

Compatibility does **not** mean copy-paste equivalence. Claude and Codex skills should match
in analytical intent, safety, expected outcomes, artifacts, and user-facing guarantees. They
may differ in invocation mechanics, tool calls, MCP/plugin behavior, session management, and
fallback instructions.

## Non-goals and guardrails

- Do not edit the Claude skill unless the user explicitly asks you to.
- Do not blindly copy `.claude/skills/*` content into `.agents/skills/*`.
- Do not claim parity when a platform capability is missing; use `BLOCKED_BY_PLATFORM`.
- Do not hide user-assisted fallbacks as automation.
- Do not port MCP-heavy workflows without labeling tool requirements and blockers.
- Treat the result as a **static parity review** unless you also run evals or smoke tests.

## When to edit vs report only

Default behavior:

- If the user asks to **review**, **compare**, **audit**, or **check parity**, produce the
  parity report and proposed changes only.
- If the user asks to **bring to parity**, **fix**, **port**, **update**, or **create the
  Codex version**, edit or scaffold the Codex skill as needed.
- Never edit the Claude skill unless explicitly requested.

Before editing, classify each gap as one of:

- safe direct edit;
- needs user decision;
- blocked by platform capability;
- better handled in shared standards/helpers.

For major rewrites, prefer a proposed patch unless the user clearly requested direct
implementation.

## Step 1 — Resolve the skill pair

Accept any of:

- explicit Claude skill path;
- explicit Codex skill path;
- skill name;
- migration request such as “port data-quality-check”.

Resolve likely paths in this order:

```text
.claude/skills/<name>/SKILL.md
.claude/skills/<name>/skill.md
.agents/skills/<name>/SKILL.md
```

If the Codex skill does not exist:

- report `NEEDS_PORTING` and stop when the user only asked to review;
- scaffold `.agents/skills/<name>/SKILL.md` when the user asked to port, create, update, or
  bring to parity.

If the Claude skill does not exist, report the missing source and ask for the intended
Claude path or shared standard.

## Step 2 — Read the skills and relevant dependencies

Read the Claude skill and Codex skill in full. If either skill references directly relevant
resources needed to understand the workflow, read only those resources required for the
parity decision, such as:

- `references/` files that define the workflow;
- scripts/helpers invoked by the skill;
- templates that define required output shape;
- assets only when they affect behavior or output requirements.

Do not chase unrelated resources. In the report, include:

- `dependencies_reviewed` — resources you inspected;
- `dependencies_not_reviewed` — resources that may matter but were not inspected, with why.

If important referenced resources are missing or too large to inspect safely, mark the
relevant category `BLOCKED` or `MAJOR_GAP` rather than assuming compatibility.

## Step 3 — Extract comparable dimensions

For each skill, identify:

- intent and user problem solved;
- trigger language and invocation style;
- workflow steps;
- required inputs and clarification points;
- preflight checks and blocker conditions;
- safety gates and truthfulness constraints;
- helper/script calls;
- external tools, MCPs, plugins, subagents, or CLI assumptions;
- artifacts, audit logs, and output paths;
- output schema/report format;
- edge cases and failure behavior;
- tests or validation hooks.

## Step 4 — Evaluate the compatibility rubric

Use these categories for every parity review.

| Category | What to check |
|---|---|
| Metadata parity | Codex frontmatter exists; `name` matches directory; `description` has Codex-native parity/migration triggers and does not rely only on Claude slash commands. |
| Intent parity | Same user problem, analytical standards, and scope unless differences are explicit. |
| Workflow parity | Critical steps, inputs, gates, validation logic, output contract, and failure behavior are represented. |
| Artifact/provenance parity | Working dirs, filenames, audit logs, JSON schemas, saved evidence, query logging, and provenance expectations are preserved or intentionally adapted. |
| Platform assumption safety | Claude-only mechanics are removed/adapted for Codex; Codex-only assumptions are flagged when reviewing in the reverse direction. |
| Safety/truthfulness parity | Blockers, privacy constraints, credential safety, data access rules, and confidence claims are preserved. |
| Helper/script parity | Shared helpers are reused when provider-neutral; provider-specific helpers are avoided or wrapped; helper changes get tests. |
| Testability parity | Metadata tests, forbidden-reference checks, helper tests, artifact schema tests, smoke prompts, or evals are recommended where needed. |
| Documentation parity | `.agents/skills/INDEX.md`, `docs/codex-guide.md`, migration matrix, README, or broader plans are updated when behavior changes. |

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

Gap severities:

```text
INFO
MINOR
MAJOR
BLOCKER
```

## Step 5 — Platform assumption checks

Flag Claude-only mechanics in Codex skills, including:

```text
/reload-plugins
/codex:setup
/plugin install
codex:codex-rescue
openai/codex-plugin-cc
~/.claude/plugins
```

Also flag:

- “Claude must...” or “Claude should...” when referring to the current Codex agent rather
  than Claude as an external reviewer model;
- Claude Code restart gates;
- Claude-specific MCP assumptions not available to Codex;
- slash-command-only invocation with no Codex skill alternative.

These references may be acceptable only when explicitly labeled as legacy Claude behavior or
when discussing the Claude source skill rather than instructing Codex.

## Step 6 — Update the Codex skill safely, if requested

When editing or scaffolding the Codex skill:

- preserve Codex-native invocation language;
- preserve provider-neutral analytical standards;
- adapt platform mechanics rather than copying Claude mechanics;
- add user-assisted fallbacks for unavailable automation;
- document intentional differences from Claude;
- keep frontmatter valid;
- recommend shared standards/helpers when provider-neutral logic is large or duplicated;
- do not remove deliberate Codex-native behavior unless it conflicts with parity or safety.

If creating a new Codex skill, scaffold:

```text
.agents/skills/<name>/SKILL.md
```

with valid `name` and `description`, then adapt the workflow from the Claude skill using this
rubric.

## Step 7 — Save run artifacts

Create a timestamped run directory:

```text
working/skill_parity_review/<UTC-timestamp>-<skill-name>/
```

Write:

- `claude_skill.md` — source Claude skill snapshot;
- `codex_skill_before.md` — original Codex skill, or `(missing)` if absent;
- `parity_report.md` — human-readable report;
- `parity_report.json` — structured report;
- `codex_skill_after.md` — when the Codex skill is edited or created;
- `patch.diff` — when practical;
- `notes.md` — optional assumptions, blockers, user decisions, and static-review limits.

## Step 8 — Report schema

`parity_report.json` should use these stable required fields and may include optional fields
for richer migrations:

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
  "files_changed": ["<path>"],
  "dependencies_reviewed": ["<path>"],
  "dependencies_not_reviewed": ["<path or note>"],
  "shared_standard_candidates": ["<section or topic>"],
  "platform_blockers": ["<blocker>"],
  "user_decisions_needed": ["<decision>"],
  "quality_notes": ["<shared issue not specific to Codex parity>"]
}
```

The primary verdict is parity, not intrinsic quality. Put problems shared by both skills in
`quality_notes` unless the Codex version worsens them.

## Step 9 — Validate

Run applicable checks:

- frontmatter/name match for edited Codex skill;
- forbidden-reference grep for edited Codex skill;
- helper unit tests if helpers changed;
- focused tests if available.

At minimum, validate edited Codex skill metadata with a small script or test:

```bash
python3 - <<'PY'
from pathlib import Path
for p in Path('.agents/skills').glob('*/SKILL.md'):
    text = p.read_text()
    assert text.startswith('---\n'), p
    front = text.split('---\n', 2)[1]
    vals = {}
    for line in front.splitlines():
        if ':' in line:
            k, v = line.split(':', 1)
            vals[k.strip()] = v.strip()
    assert vals.get('name') == p.parent.name, (p, vals.get('name'))
    assert vals.get('description'), p
print('Codex skill metadata ok')
PY
```

## Step 10 — Report to the user

Lead with:

1. overall verdict;
2. top 3 gaps fixed or remaining;
3. whether the review was static-only or included tests/evals;
4. files changed;
5. artifact paths;
6. validation commands run;
7. recommended next action.

Keep detailed evidence in `parity_report.md` and `parity_report.json`.

## Long-term compatibility model

Prefer a three-layer architecture for substantial migrations:

```text
docs/standards/<skill-name>.md         # provider-neutral substance
.claude/skills/<skill-name>/skill.md   # Claude wrapper
.agents/skills/<skill-name>/SKILL.md   # Codex wrapper
```

Use this model to avoid two large prompt libraries drifting apart. The parity reviewer should
recommend shared-standard extraction when both skills contain large provider-neutral sections
that would otherwise be duplicated.

## Static review limitation

A static parity review can find missing requirements, unsafe platform assumptions, and
artifact mismatches. It does not prove behavioral parity. For high-value skills, recommend
smoke prompts or evals after static parity gaps are resolved.
