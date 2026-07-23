---
name: codex-review
description: Legacy compatibility wrapper for requests to validate an analysis with Codex. In Codex-native sessions, use this to explain that same-provider self-review is not independent and route to `$independent-review` or `$claude-review` for true blind validation, while preserving audit-log and AGREE/DISAGREE/PARTIAL reconciliation concepts when an external reviewer is available.
---

# Codex Review

## Purpose

Preserve the legacy Codex-review intent without creating circular Codex-checks-Codex validation. In Codex, the safe path is provider-neutral independent review or a Claude second opinion.

## When to use

- the user says codex review, validate with codex, second opinion from codex, or asks whether Codex agrees;
- a legacy artifact or workflow references codex-review;
- the user wants multi-model validation of an analysis result;
- you need to explain why same-provider self-review is not independent in a Codex session.

## Workflow

### 1. Classify the request

Determine whether the user wants:

- a true independent validation of a Codex-produced result;
- a legacy Claude-era Codex validation artifact interpreted or migrated;
- a same-provider recheck for stability rather than independence.

### 2. Apply the independence gate

If the current analysis was produced by Codex, do **not** present another Codex pass as independent validation. State clearly that same-provider self-review is circular for correctness validation.

Route instead:

- `$independent-review` for provider-neutral blind second-pass validation;
- `$claude-review` when the user specifically wants Claude to validate Codex output;
- `$reliability` when the goal is repeated-run stability, not cross-provider correctness.

### 3. Preserve the blind-brief pattern

For any real independent review, create a blind brief that contains the question, metric definitions, active dataset, schema/quirks, and required output contract — but not the original SQL, numbers, or conclusions. Keep original results in a separate comparison-only file.

Suggested run layout:

```text
working/independent_review/<timestamp>-<question>/
├── brief.md
├── original_result.md
├── independent_result.md
├── verdict.md
└── verdict.json
```

### 4. Reconcile results

Use the legacy verdict vocabulary:

- `AGREE` when numbers and conclusions match within tolerance;
- `DISAGREE` when material numbers or interpretation diverge;
- `PARTIAL` when direction or some sub-findings match but details differ.

On disagreement, diagnose definition, filter, cohort, join grain, source, and window differences. Do not average conflicting numbers.

### 5. Report honestly

Lead with whether the validation was truly independent. If not, say what safe route is available. If a real external review ran, show the comparison table and artifact paths.

## Key contracts preserved from Claude

- `AGREE`
- `DISAGREE`
- `PARTIAL`
- `blind brief`
- `independent-review`

## Codex adaptation notes

- Use natural language or `$codex-review` invocation; do not rely on legacy slash-command-only mechanics.
- Prefer repository helpers, available MCP tools, and safe local fallbacks over provider-specific assumptions.
- Never print or commit credentials, tokens, secrets, private workspace content, or user-specific generated artifacts.
- If an external platform/tool is unavailable, state the blocker and offer the closest safe fallback.
