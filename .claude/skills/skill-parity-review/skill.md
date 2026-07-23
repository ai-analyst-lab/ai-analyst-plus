---
name: skill-parity-review
description: Review a Claude skill against its corresponding Codex skill for Claude/Codex skill parity and migration compatibility, then optionally bring the Claude skill up to parity without copying Codex-only mechanics. Use when the user asks to compare .agents/skills and .claude/skills, port a Codex skill to Claude, make a Claude skill compatible, check skill parity, audit a skill migration, verify a Claude skill is on par with the Codex version, review cross-provider compatibility, or build the Claude counterpart of a Codex skill.
---

# Skill Parity Review (Claude ← Codex)

## Purpose

Use this skill to perform a structured static parity review between a Codex skill and its
Claude counterpart. The goal is to determine whether the Claude skill is outcome-compatible
with the Codex skill, identify gaps, and, when the user asks for it, update or create only the
Claude skill to close safe gaps.

Compatibility does **not** mean copy-paste equivalence. Claude and Codex skills should match
in analytical intent, safety, expected outcomes, artifacts, and user-facing guarantees. They
may differ in invocation mechanics, tool calls, MCP/plugin behavior, session management, and
fallback instructions.

This skill is the mirror of the Codex-native `$skill-parity-review` (which reviews
Claude → Codex). This one reviews Codex → Claude.

## Non-goals and guardrails

- Do not edit the Codex skill unless the user explicitly asks you to.
- Do not blindly copy `.agents/skills/*` content into `.claude/skills/*`.
- Do not claim parity when a platform capability is missing; use `BLOCKED_BY_PLATFORM`.
- Do not hide MCP/plugin-based automation as equivalent to Codex user-assisted workflows.
- Do not port Codex-specific CLI workflows without labeling tool requirements and blockers.
- Treat the result as a **static parity review** unless you also run evals or smoke tests.

## When to edit vs report only

Default behavior:

- If the user asks to **review**, **compare**, **audit**, or **check parity**, produce the
  parity report and proposed changes only.
- If the user asks to **bring to parity**, **fix**, **port**, **update**, **create**, or
  **build the Claude version**, edit or scaffold the Claude skill as needed.
- Never edit the Codex skill unless explicitly requested.

Before editing, classify each gap as one of:

- safe direct edit;
- needs user decision;
- blocked by platform capability;
- better handled in shared standards/helpers.

For major rewrites, prefer a proposed patch unless the user clearly requested direct
implementation.

## Step 1 — Resolve the skill pair

Accept any of:

- explicit Codex skill path;
- explicit Claude skill path;
- skill name;
- migration request such as "port independent-review to Claude".

Resolve likely paths in this order:

```text
.agents/skills/<name>/SKILL.md
.claude/skills/<name>/SKILL.md
.claude/skills/<name>/skill.md
```

If the Claude skill does not exist:

- report `NEEDS_PORTING` and stop when the user only asked to review;
- scaffold `.claude/skills/<name>/skill.md` when the user asked to port, create, update, or
  bring to parity.

If the Codex skill does not exist, report the missing source and ask for the intended
Codex path or shared standard.

## Step 2 — Read the skills and relevant dependencies

Read the Codex skill and Claude skill in full. If either skill references directly relevant
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
| Metadata parity | Claude frontmatter exists; `name` matches directory; `description` has Claude-native parity/migration triggers and does not rely only on Codex `$` commands. |
| Intent parity | Same user problem, analytical standards, and scope unless differences are explicit. |
| Workflow parity | Critical steps, inputs, gates, validation logic, output contract, and failure behavior are represented. |
| Artifact/provenance parity | Working dirs, filenames, audit logs, JSON schemas, saved evidence, query logging, and provenance expectations are preserved or intentionally adapted. |
| Platform assumption safety | Codex-only mechanics are removed/adapted for Claude; Claude-only assumptions are flagged when reviewing in the reverse direction. |
| Safety/truthfulness parity | Blockers, privacy constraints, credential safety, data access rules, and confidence claims are preserved. |
| Helper/script parity | Shared helpers are reused when provider-neutral; provider-specific helpers are avoided or wrapped; helper changes get tests. |
| Testability parity | Metadata tests, forbidden-reference checks, helper tests, artifact schema tests, smoke prompts, or evals are recommended where needed. |
| Documentation parity | CLAUDE.md skill table, `.claude/skills/` index, migration matrix, README, or broader plans are updated when behavior changes. |

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

Flag Codex-only mechanics in Claude skills, including:

```text
$skill-name (as invocation instruction for the Claude agent)
codex exec
codex login
.agents/skills/ (used as instructions for the current Claude agent to follow)
AGENTS.md (as a skill reference path)
```

Also flag:

- "Codex must..." or "Codex should..." when referring to the current Claude agent rather
  than Codex as an external model;
- Codex CLI restart or session gates;
- Codex-specific environment assumptions not available to Claude Code;
- `$`-command-only invocation with no Claude slash-command alternative.

These references may be acceptable only when explicitly labeled as Codex behavior or
when discussing the Codex source skill rather than instructing Claude.

When reviewing in the reverse direction (checking Claude-only mechanics that leaked into
Codex skills), also flag:

```text
/reload-plugins
/codex:setup
/plugin install
codex:codex-rescue
openai/codex-plugin-cc
~/.claude/plugins
```

## Step 6 — Update the Claude skill safely, if requested

When editing or scaffolding the Claude skill:

- preserve Claude-native invocation language (slash commands, skill triggers);
- preserve provider-neutral analytical standards;
- adapt platform mechanics rather than copying Codex mechanics;
- leverage MCP tools, plugins, and subagents where available in Claude Code;
- document intentional differences from Codex;
- keep frontmatter valid;
- recommend shared standards/helpers when provider-neutral logic is large or duplicated;
- do not remove deliberate Claude-native behavior unless it conflicts with parity or safety.

If creating a new Claude skill, scaffold:

```text
.claude/skills/<name>/skill.md
```

with valid `name` and `description`, then adapt the workflow from the Codex skill using this
rubric.

After creating or editing a Claude skill, also check whether the CLAUDE.md skill table needs
updating with the new skill entry (path, trigger condition).

## Step 7 — Save run artifacts

Create a timestamped run directory:

```text
working/skill_parity_review/<UTC-timestamp>-<skill-name>/
```

Write:

- `codex_skill.md` — source Codex skill snapshot;
- `claude_skill_before.md` — original Claude skill, or `(missing)` if absent;
- `parity_report.md` — human-readable report;
- `parity_report.json` — structured report;
- `claude_skill_after.md` — when the Claude skill is edited or created;
- `patch.diff` — when practical;
- `notes.md` — optional assumptions, blockers, user decisions, and static-review limits.

## Step 8 — Report schema

`parity_report.json` should use these stable required fields and may include optional fields
for richer migrations:

```json
{
  "skill": "<skill-name>",
  "direction": "codex-to-claude",
  "codex_path": ".agents/skills/<skill-name>/SKILL.md",
  "claude_path": ".claude/skills/<skill-name>/skill.md",
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
  "quality_notes": ["<shared issue not specific to Claude parity>"]
}
```

The `direction` field distinguishes this from Codex-side reports (`claude-to-codex`).

The primary verdict is parity, not intrinsic quality. Put problems shared by both skills in
`quality_notes` unless the Claude version worsens them.

## Step 9 — Validate

Run applicable checks:

- frontmatter/name match for edited Claude skill;
- forbidden-reference grep for edited Claude skill;
- helper unit tests if helpers changed;
- focused tests if available.

At minimum, validate edited Claude skill metadata with a small script or test:

```bash
python3 - <<'PY'
from pathlib import Path
for p in list(Path('.claude/skills').glob('*/SKILL.md')) + list(Path('.claude/skills').glob('*/skill.md')):
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
print('Claude skill metadata ok')
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

## Cross-direction coordination

This skill (Claude ← Codex) and the Codex-native `$skill-parity-review` (Claude → Codex)
share the same rubric, verdict system, artifact structure, and report schema. This is
intentional — it means:

- A parity report from either direction uses the same categories and verdicts.
- Artifact directories under `working/skill_parity_review/` are compatible regardless of
  which direction produced them.
- The `direction` field in `parity_report.json` distinguishes `codex-to-claude` from
  `claude-to-codex`.
- After running both directions on a skill, the combined reports give a complete
  bidirectional parity picture.

## Static review limitation

A static parity review can find missing requirements, unsafe platform assumptions, and
artifact mismatches. It does not prove behavioral parity. For high-value skills, recommend
smoke prompts or evals after static parity gaps are resolved.
