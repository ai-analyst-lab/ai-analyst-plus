---
name: claude-review
description: Have Claude independently validate a Codex-produced analysis or finding through a blind second-pass re-derivation. Use when the user says claude review, validate with Claude, second opinion from Claude, ask Claude to check this, cross-check with Claude, have Claude independently verify this analysis, or wants a different model to blind re-derive Codex's result before acting on it.
---

# Claude Review

## Purpose

Use this skill when Codex has produced an analytical result and the user wants Claude to
independently re-derive the answer from the same data. Claude receives the question,
metric definitions, scope, time window, and data access instructions, but must not see
Codex's SQL, numbers, charts, or conclusions. The skill then reconciles the two results as
`AGREE`, `PARTIAL`, or `DISAGREE` per finding.

This is the Codex-native mirror of the legacy Claude `/codex-review` pattern: Codex asks a
separate Claude run for a blind second derivation. The point is independent agreement, not
a critique of Codex's work.

## Core rule: no Claude, no validation

This workflow is only meaningful if a fresh Claude context does the second derivation. If
you cannot run or arrange a Claude session that has not seen the original Codex SQL,
numbers, or conclusions, do not validate the result yourself and do not present same-model
rechecking as independent validation. Instead, save the blind brief and give the user the
exact command or prompt to run in a fresh Claude session.

## Invocation

Use `$claude-review [finding or artifact path]` or select `claude-review` from `/skills`.
By default, validate the most recent Codex-produced analysis in the conversation or
workspace.

## Workflow

### Step 1 — Preflight: is Claude usable from here?

Check whether the Claude CLI is available before preparing a live run:

```bash
command -v claude >/dev/null 2>&1 && claude --version
```

Route based on the result:

- **Claude CLI available** — continue to Step 2 and plan to run Claude with the blind brief.
- **Claude CLI unavailable or unauthenticated** — continue through Step 3 to create the blind
  brief and `original_result.md`, then stop before Step 4 with user-assisted instructions.
  Do not substitute Codex's own recheck.

Suggested setup guidance when the CLI is missing:

```text
Claude CLI is not available in this environment. I created a blind brief at <brief.md>.
Open a fresh Claude Code session in this repository and ask it to follow that brief only;
then save/paste the output to <run_dir>/claude_independent.md and rerun $claude-review to
compare.
```

If the CLI is installed but auth fails, tell the user to run the Claude login/setup flow for
their environment, then rerun `$claude-review`.

### Step 2 — Resolve what Claude should validate

Identify the finding, analysis artifact, or latest result to validate. Prefer an explicit
artifact path or named finding when supplied; otherwise use the most recent Codex-produced
analysis.

Capture Codex's original result separately:
- question answered;
- headline number(s) and conclusion(s);
- SQL, query log references, notebook cells, or artifact paths;
- metric definitions, scope, filters, cohort rules, and time window used;
- caveats or assumptions already stated.

If the target is ambiguous, ask the user which finding or artifact Claude should check.

### Step 3 — Write the blind Claude brief

Create a timestamped run directory:

```bash
working/claude_review/<UTC-timestamp>-<question-slug>/
```

Write **`brief.md`** containing only what Claude needs to independently answer the same
question the same way:
- the business question;
- metric definitions, numerator, denominator, grain, filters, segmentation, scope, cohort
  rules, and time window;
- active dataset id and data access instructions: read `.knowledge/active.yaml`, the active
  dataset manifest, `schema.md`, and `quirks.md`; use repository helpers such as
  `helpers.connection_manager.ConnectionManager` when applicable;
- repository expectations such as logging executed SQL with `scripts/log_query.py`;
- the output contract from Step 4.

Do **not** include Codex's SQL, result numbers, charts, conclusion, or hints like "confirm
Codex's 38% answer" in `brief.md`.

Separately write **`codex_original.md`** in the same run directory with Codex's original
headline number(s), SQL, conclusion, caveats, and artifact paths. This file is for the final
comparison only and must not be passed to Claude.

### Step 4 — Run Claude independently

Use the best genuinely independent Claude mechanism available:

1. **Preferred:** run the Claude CLI in a fresh non-interactive session with `brief.md` only.
2. **Acceptable:** ask the user to open a fresh Claude Code session in this repository and
   provide only `brief.md`.
3. **Do not use:** Codex reading `codex_original.md` and rechecking its own answer.

When using the CLI, run from the repository root and save Claude's full response:

```bash
claude -p "$(cat <run_dir>/brief.md)" > <run_dir>/claude_independent.md
```

If the local Claude CLI uses a different non-interactive flag, adapt the command, but keep
these requirements unchanged: fresh Claude context, blind brief only, output saved to
`claude_independent.md`.

Use this output contract in the brief:

```markdown
Independently answer the analytics question in this brief against the active dataset.
Use the metric definitions, scope, and time window exactly as given. Write and run your own
queries; do not ask for or infer Codex's SQL, numbers, or conclusion. Log executed queries
according to repository instructions. Report only:

- headline: <single number or concise result per finding>
- sql: <query/queries actually run, or query log references>
- measured: <numerator, denominator, grain, window, filters>
- conclusion: <one or two sentences>
- caveats: <data or metric caveats, if any>
```

If Claude cannot access the data or the CLI run fails, save the failure output to
`claude_independent.md` or `blocked.md`, explain the blocker, and do not produce a verdict.

### Step 5 — Compare results skeptically

After `claude_independent.md` exists, compare it with `codex_original.md` and assign a
verdict per finding:

- `AGREE` — numbers match within a sensible stated tolerance and conclusions align.
- `PARTIAL` — same direction but different magnitude, agreement on some sub-results only,
  or caveats materially narrow the claim.
- `DISAGREE` — material difference in number, direction, metric definition, SQL grain,
  filters, cohort, time window, or conclusion.

Do not average conflicting numbers. For `PARTIAL` or `DISAGREE`, identify the likely cause
of divergence and recommend the next resolution step, such as clarifying the metric,
checking join grain, rerunning a query, or logging a correction.

Write:
- `verdict.md` — human-readable comparison table, e.g.
  `Finding | Codex | Claude | Verdict | Why`;
- `verdict.json` — deterministic audit payload:

```json
{
  "question": "<question>",
  "reviewer": "claude",
  "findings": [
    {
      "name": "<finding>",
      "verdict": "AGREE|PARTIAL|DISAGREE",
      "codex": "<brief Codex result summary>",
      "claude": "<brief Claude result summary>",
      "why": "<short rationale>"
    }
  ]
}
```

### Step 6 — Append the audit log

Append one JSONL row to `.knowledge/claude-review/log.jsonl`. Create the directory if
needed. Count verdicts from `verdict.json`, not from prose, using the deterministic helper:

```bash
python3 helpers/review_logging.py <run_dir> claude-review
```

The helper validates `verdict.json`, counts `AGREE`, `PARTIAL`, `DISAGREE`, and `UNKNOWN`,
and appends a stable JSONL audit entry.

### Step 7 — Report to the user

Report the verdict table and saved paths:
- run directory;
- `brief.md`;
- `codex_original.md`;
- `claude_independent.md`;
- `verdict.md` and `verdict.json`;
- `.knowledge/claude-review/log.jsonl`.

Use honest framing:
- all `AGREE`: Claude independently reproduced the result, which is strong evidence but not
  proof;
- any `PARTIAL` or `DISAGREE`: the second derivation found a material issue or ambiguity to
  resolve before acting.

## Relationship to other review skills

- `$claude-review` is Codex-native and specifically asks Claude to validate a Codex result.
- `$independent-review` is provider-neutral and should be used when the reviewer model or
  mechanism is not specified.
- Legacy Claude users can keep using `.claude/skills/codex-review/SKILL.md` via
  `/codex-review` to ask Codex to validate Claude's result.
