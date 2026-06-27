---
name: independent-review
description: Run a provider-neutral blind second-pass validation of an analysis or finding. Use when the user asks for an independent review, second opinion, validate this analysis, cross-check this finding, independently verify this, or blind re-derive; also use before acting on a high-stakes analytical result when honest independent validation is requested.
---

# Independent Review

## Purpose

Use this skill to get an honest second-pass validation of an analytical result. The
reviewer must re-derive the answer from the same question, dataset, metric definitions,
scope, and time window while staying blind to the original SQL, numbers, and conclusions.
The goal is independent agreement or useful disagreement, not a critique of the original
work.

This is provider-neutral. It can use a fresh Codex custom agent, subagent, or separate
session when available, but it must not depend on Claude plugin mechanics or the legacy
`/codex-review` workflow.

## Core rule: do not fake independence

A review is only independent if the second derivation does not see the original SQL,
headline numbers, or conclusions. If you cannot run or arrange a fresh model/session (or
equivalent isolated reviewer) with only the blind brief, say so and stop with clear next
steps. Do not re-check the work in the same context and call it independent.

## Workflow

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

Build a validation input set that includes only what an independent reviewer needs to
answer the same question the same way:
- business question;
- dataset identifier and access instructions;
- metric definitions, numerator, denominator, grain, filters, and segmentation;
- scope, cohort rules, and time window;
- required repository instructions such as reading `.knowledge/active.yaml`, dataset
  manifests, schema docs, quirks, and logging executed queries with `scripts/log_query.py`.

Do **not** include original SQL, original result numbers, original charts, original
conclusions, or hints like "confirm the 38% result" in the blind brief.

### Step 3 — Create the run directory and provenance files

Create a timestamped run directory:

```bash
working/independent_review/<UTC-timestamp>-<question-slug>/
```

Write:
- `brief.md` — the blind validation brief, containing only the allowed inputs from Step 2;
- `original_result.md` — the original result, SQL, numbers, conclusion, and artifact paths.

Keep `original_result.md` out of the independent reviewer prompt.

### Step 4 — Run the independent derivation

Use the best genuinely independent mechanism available in the current environment:

1. **Preferred:** dispatch a fresh Codex custom agent/subagent or equivalent fresh model
   worker with `brief.md` only.
2. **Acceptable:** start a separate Codex session that has not seen the original analysis and
   pass it `brief.md` only.
3. **User-assisted fallback:** if no automatic fresh worker is available, instruct the user to
   run a fresh Codex session with the contents of `brief.md`, then paste or save the output to
   `independent_result.md`.

Use this output contract for the independent reviewer:

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

Save the independent output as `independent_result.md` in the run directory.

If you cannot obtain a blind independent output, write `blocked.md` explaining what is
missing and do not produce a verdict.

### Step 5 — Compare and assign verdicts

After `independent_result.md` exists, compare it with `original_result.md` skeptically.
Assign one verdict per finding:

- `AGREE` — numbers match within a sensible stated tolerance and conclusions align.
- `PARTIAL` — same direction but different magnitude, some sub-results agree, or caveats
  materially narrow the claim.
- `DISAGREE` — a material gap in number, direction, definition, SQL grain, filters, cohort,
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
needed. Count verdicts from `verdict.json`, not from prose. A small inline Python logger is
sufficient when no dedicated helper exists:

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
- all `AGREE`: independent re-derivation is strong evidence the result is sound, not proof;
- any `PARTIAL` or `DISAGREE`: the review found an issue worth resolving before acting.

## Notes for Claude users

The legacy Claude Code slash-command workflow remains at
`.claude/skills/codex-review/SKILL.md` and is invoked as `/codex-review`. Codex users should
use `$independent-review` or select `independent-review` from `/skills`.
