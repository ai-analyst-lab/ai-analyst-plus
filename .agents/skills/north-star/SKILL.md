---
name: north-star
description: Coach North Star Metric lifecycle work from Codex: explain NSM concepts, triage or audit candidate NSMs, design or refine NSM inputs, and route strategic anchor metric questions with citation and calibration safeguards. Use when users mention north star metric, NSM, anchor metric, strategic metric, main metric, metric audit, NSM design, or NSM drivers.
---

# North Star

## Purpose

Provide a Codex-native wrapper around the repository's North Star Metric playbook, helpers, wiki, and specialist agents while preserving citation discipline, calibration boundaries, and artifact contracts. Shared deterministic runtime helpers live under `helpers/north_star/`; the curated wiki corpus lives in the provider-neutral `shared/north-star/wiki/` folder, with `.claude/skills/north-star/wiki` retained as a legacy compatibility symlink.

## When to use

- the user mentions North Star Metric, NSM, strategic anchor metric, or main metric in a strategic context;
- a PM wants to audit, triage, explain, draft, defend, diagnose, or evolve an NSM;
- the user needs NSM input metrics or drivers;
- question-router identifies NSM lifecycle intent.

## Workflow

### Supported verbs and natural-language routing

Accept natural language or `$north-star <verb> ...` style requests. Dispatch to:

| Verb | Use when |
|---|---|
| `explain <concept>` | user wants a cited NSM concept explanation |
| `triage "<candidate>"` | quick screen of a candidate metric |
| `audit "<candidate>"` | full 7-checklist candidate evaluation |
| `draft` | design from scratch when required helper/templates exist; otherwise explain the current blocker and offer audit/triage |
| `inputs` | build a data-validated metric tree for an audited NSM |
| `drivers` | decompose NSM movement over a window when helper/data support exists |

If no verb is clear, show the current NSM if profile state exists; otherwise present the entry menu.

### Shared corpus and core principles

Read `.claude/skills/north-star/_lib/core_principles.md` or the corresponding shared standard before making framework claims. Treat `shared/north-star/wiki/` as the curated NSM corpus; do not duplicate wiki content into provider-specific skill folders. Honor cite-on-claim, never-fabricate, contested-zone, and boundary-speech rules.

### Use deterministic helpers where available

The shared helper package is `helpers/north_star/`.

From repo root, prefer helper CLIs/modules over hand-written logic:

```bash
python3 -m helpers.north_star refusal --stdin
python3 -m helpers.north_star classify-vertical "<description>" --industry <industry> --business-model <model>
python3 -m helpers.north_star calibration <vertical_id> <verb>
python3 -m helpers.north_star case-lookup --vertical-id <vertical_id> --limit 3
python3 -m helpers.north_star checklist
```

For candidate-bearing verbs, pass the candidate via stdin to the refusal pre-filter to avoid shell quoting hazards. If refused, compose a useful refusal/redirect rather than continuing.

### Profile and calibration preflight

Load active org/product profile through `helpers.north_star.profile` when available. If product context is missing and the verb requires judgment, ask one concise product-description question and pause. Classify vertical/game and check calibration before verdict verbs. If calibration is missing or experimental under trust mode, state the boundary and offer generic framework guidance with explicit uncertainty.

### Verb workflows

- **Audit**: run/refollow the 7-question checklist, produce PASS/WEAK/FAIL per criterion, load similar cases when calibrated, and write an artifact under `outputs/north-star/{org}/audit-*.md` when practical.
- **Triage**: compare against vanity/lagging/input/NSM role tests and produce a short disposition table.
- **Explain**: answer from cited wiki/playbook concepts; if citation is unavailable, say so.
- **Draft**: only run if draft helpers/templates exist. Otherwise explain what is unavailable and suggest auditing a candidate or using a constrained manual worksheet.
- **Inputs**: require an audited/current NSM and connected dataset when doing data-validated input trees; reject inputs that merely restate the NSM.
- **Drivers**: use `helpers.north_star.drivers` when available and document the decomposition window and caveats.

### Cross-skill composition

Use `$metric-spec` for precise metric definitions, `$metrics` to browse/register metrics, `$guardrails` for countervailing metrics, `$tracking-gaps` for measurability gaps, `$question-router` for routing, `$pace` for pacing, and `$session-handoff` when NSM state or external artifacts need preservation.

### Output contract

For NSM judgment outputs include:

- verdict and one-line rationale;
- cited criteria or concept references;
- weak/failing criteria and fix recipes;
- calibration boundary if applicable;
- artifact path when saved;
- recommended next verb/action.

## Key contracts preserved from Claude

- `North Star Metric`
- `NSM`
- `refusal`
- `calibration`
- `7-checklist`
- `outputs/north-star`
- `helpers/north_star/`
- `shared/north-star/wiki/`
- `.claude/skills/north-star/wiki/` legacy symlink

## Codex adaptation notes

- Use natural language or `$north-star` invocation; do not rely on legacy slash-command-only mechanics.
- Prefer repository helpers, standards, and existing skill composition over duplicating large provider-specific prompts.
- If a required external capability is unavailable, state the blocker and offer the closest safe manual fallback.
