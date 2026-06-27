---
name: independent-review
description: Run a provider-neutral blind second-pass validation of an analysis or finding. Use when the user asks for an independent review, second opinion, validate this analysis, cross-check this finding, independently verify this, blind re-derive, or wants honest independent validation before acting on a high-stakes analytical result. Also use when the user says "have another model check this", "does this hold up", "sanity check this independently", or "verify this from scratch".
---

# Independent Review

## Purpose

Use this skill to get an honest second-pass validation of an analytical result. The
reviewer must re-derive the answer from the same question, dataset, metric definitions,
scope, and time window while staying **blind** to the original SQL, numbers, and conclusions.
The goal is independent agreement or useful disagreement — not a critique of the original
work, but an independent re-derivation.

This is provider-neutral. It works by dispatching a fresh Claude subagent (via the Agent
tool) that receives only the blind brief and has no access to the original analysis context.
The isolation is what makes it independent — the subagent writes its own queries and computes
its own results.

This skill supersedes the legacy `/codex-review` workflow for independent validation. The
legacy skill remains at `.claude/skills/codex-review/SKILL.md` for users who specifically
want Codex as the second model.

## Core rule: do not fake independence

> ### ⛔ HARD GATE
> A review is only independent if the second derivation does not see the original SQL,
> headline numbers, or conclusions. The subagent must receive **only** the blind brief.
>
> **You (the main Claude session) must NOT perform the validation yourself.** Re-checking
> your own analysis in the same context is circular — it produces a confident "validated ✓"
> that means nothing and actively misleads the user.
>
> If you cannot dispatch a subagent (e.g., Agent tool is unavailable), your ONLY job is to:
> 1. Write the `brief.md` and `original_result.md` to the run directory.
> 2. Tell the user to run a fresh Claude Code session (or any other model) with `brief.md`.
> 3. Stop. Do not produce a verdict yourself.

## When to Use

- User says `/independent-review`, "independently verify this", "second opinion",
  "validate this analysis", "cross-check this", "blind re-derive", "sanity check this"
- After producing a finding the user is about to act on and wants independent confirmation
- Routed here whenever independent validation of an analytical result is wanted
- Prefer this over `/codex-review` unless the user specifically wants Codex as the reviewer

## Invocation

`/independent-review [finding or artifact path]` — validate the most recent analysis by
default, or scope to a single finding/file if given.

Example: `/independent-review` after answering "What's our 30-day retention?"

## Instructions

### Step 1 — Resolve what to validate

Identify the finding, analysis artifact, or latest result to validate. Prefer an explicit
artifact path or named finding when provided; otherwise use the most recent analytical
result in the conversation or workspace.

Capture the original result separately:
- question answered;
- original headline number(s) and conclusion(s);
- original SQL, query log references, notebook cells, or artifact paths;
- any caveats already stated.

If there is no clear target, ask the user which finding or artifact to review.

### Step 2 — Extract only the blind inputs

Build a validation input set that includes **only** what an independent reviewer needs to
answer the same question the same way:
- business question;
- dataset identifier and access instructions;
- metric definitions, numerator, denominator, grain, filters, and segmentation;
- scope, cohort rules, and time window;
- required repository instructions such as reading `.knowledge/active.yaml`, dataset
  manifests, schema docs, quirks, and logging executed queries with `scripts/log_query.py`.

Do **NOT** include original SQL, original result numbers, original charts, original
conclusions, or hints like "confirm the 38% result" in the blind brief.

### Step 3 — Create the run directory and provenance files

Create a timestamped run directory:

```bash
mkdir -p working/independent_review/<UTC-timestamp>-<question-slug>/
```

Write:
- `brief.md` — the blind validation brief, containing only the allowed inputs from Step 2;
- `original_result.md` — the original result, SQL, numbers, conclusion, and artifact paths.

Keep `original_result.md` **out** of the independent reviewer prompt.

### Step 4 — Run the independent derivation

Use the Agent tool to dispatch a fresh subagent that is **blind to the original analysis**:

```
Agent tool call:
  prompt: <contents of brief.md + output contract below>
  description: "Independent blind review"
```

The subagent receives **only** the blind brief and this output contract:

```markdown
Independently answer the analytics question in this brief against the active dataset.
Use the metric definitions, scope, and time window exactly as given. Write and run your own
queries; do not ask for or infer anyone else's SQL, numbers, or conclusion. Log executed
queries according to the repository instructions. Report only:

- headline: <single number or concise result per finding>
- sql: <query/queries actually run, or query log references>
- measured: <numerator, denominator, grain, window, filters>
- conclusion: <one or two sentences>
- caveats: <data or metric caveats, if any>
```

Save the subagent's output as `independent_result.md` in the run directory.

**User-assisted fallback:** If the Agent tool is unavailable or the subagent cannot
connect to the data source:
1. Save `brief.md` to the run directory.
2. Tell the user: "I've written the blind brief. Please run a fresh Claude Code session
   (or any model) with the contents of `brief.md`, then paste the output here or save it
   as `independent_result.md` in the run directory."
3. Stop. Do not produce a verdict until `independent_result.md` exists.

### Step 5 — Compare and assign verdicts

After `independent_result.md` exists, compare it with `original_result.md` skeptically.
Assign one verdict per finding:

- **AGREE** — numbers match within a sensible stated tolerance and conclusions align.
- **PARTIAL** — same direction but different magnitude, some sub-results agree, or caveats
  materially narrow the claim.
- **DISAGREE** — a material gap in number, direction, definition, SQL grain, filters, cohort,
  time window, or conclusion.

Do not average conflicting results. For any `PARTIAL` or `DISAGREE`, identify the most likely
source of divergence and recommend the next resolution step.

Write:
- `verdict.md` — a human-readable table with columns such as
  `Finding | Original | Independent | Verdict | Why`;
- `verdict.json` — deterministic audit payload shaped like:

```json
{
  "question": "<question>",
  "reviewer": "independent-review",
  "findings": [
    {
      "name": "<finding>",
      "verdict": "AGREE|PARTIAL|DISAGREE",
      "original": "<brief original result summary>",
      "independent": "<brief independent result summary>",
      "why": "<short rationale>"
    }
  ]
}
```

### Step 6 — Append the audit log

Append one JSONL row to `.knowledge/independent-review/log.jsonl`. Create the directory if
needed. Count verdicts from `verdict.json`, not from prose:

```bash
python3 - "<run_dir>" <<'PY'
import json, sys
from datetime import datetime, timezone
from pathlib import Path

run_dir = Path(sys.argv[1])
payload = json.loads((run_dir / "verdict.json").read_text())
findings = payload.get("findings", [])
counts = {"AGREE": 0, "PARTIAL": 0, "DISAGREE": 0, "UNKNOWN": 0}
for finding in findings:
    verdict = str(finding.get("verdict", "")).strip().upper()
    counts[verdict if verdict in counts else "UNKNOWN"] += 1
entry = {
    "ts": datetime.now(timezone.utc).isoformat(),
    "question": payload.get("question", "(unknown)"),
    "reviewer": payload.get("reviewer", "independent-review"),
    "n_findings": len(findings),
    "agree": counts["AGREE"],
    "partial": counts["PARTIAL"],
    "disagree": counts["DISAGREE"],
    "unknown": counts["UNKNOWN"],
    "dir": str(run_dir),
}
log_dir = Path(".knowledge/independent-review")
log_dir.mkdir(parents=True, exist_ok=True)
with (log_dir / "log.jsonl").open("a") as f:
    f.write(json.dumps(entry, sort_keys=True) + "\n")
print(json.dumps(entry, indent=2, sort_keys=True))
PY
```

### Step 7 — Report to the user

Report a concise verdict table and provenance paths:
- run directory;
- `brief.md`;
- `original_result.md`;
- `independent_result.md`;
- `verdict.md` and `verdict.json`;
- `.knowledge/independent-review/log.jsonl`.

Use honest framing:
- **All AGREE** — "An independent re-derivation reproduced this from its own queries. That's
  strong evidence the result is sound — not proof, but two independent derivations agreeing."
- **Any PARTIAL or DISAGREE** — "The independent review diverged here. That's the check
  earning its keep: one of these derivations may be wrong, or the metric is under-defined.
  Resolve the gap before acting on the number."

On any DISAGREE, offer to:
- re-run the relevant analysis step;
- define the metric precisely via `/metric-spec`;
- log the lesson via `/log-correction`.

## Relationship to other skills

| Skill | What it tests | Mechanism |
|-------|--------------|-----------|
| `/independent-review` (this) | Correctness by independent agreement | Fresh subagent, blind re-derivation |
| `/reliability` | Stability (same model, N runs) | Same model run N times |
| `/codex-review` (legacy) | Correctness via Codex specifically | Codex CLI plugin, blind brief |

Use `/independent-review` as the default for independent validation. Use `/codex-review`
only when the user specifically wants Codex (OpenAI) as the second model. Use `/reliability`
when you want to test whether the *same* model gives consistent results.

## Rules

1. **No independence, no verdict.** If you cannot dispatch a blind subagent or arrange a
   fresh session, stop at the brief-writing step. Never validate your own analysis in the
   same context and call it independent.
2. **The subagent must be blind.** Never include original SQL, result numbers, or conclusions
   in `brief.md`. If you can't keep them out, the run isn't independent — say so rather than
   presenting a false validation.
3. **Counting is deterministic.** Verdict tallies come from the Python logger reading
   `verdict.json`, never estimated in prose.
4. **Same definitions, independent derivation.** The subagent answers the *same* question
   with the *same* metric definition — only the SQL and numbers are its own.

## Edge Cases

- **No recent analysis to validate** → ask the user what to check; offer a path or finding.
- **Subagent can't reach the warehouse** → the brief should include the local DuckDB/CSV
  fallback (`manifest.local_data`) so it can still derive independently.
- **Subagent defines the metric differently** → flag it: the disagreement may be
  definitional, not a computation error. Surface both definitions and recommend `/metric-spec`.
- **Agent tool unavailable** → write `brief.md` and instruct the user to run it in a fresh
  session. This is the user-assisted fallback, not a failure.
