---
name: semantic-validation
description: Run the 4-layer semantic validation stack and confidence scoring for analytical findings. Use after analysis, before stakeholder presentation, when validating calculations or data quality, when users ask if findings are trustworthy, or whenever L3+ analysis needs a confidence gate.
---

# Semantic Validation

## Purpose

Validate analytical outputs with structural, logical, business-rule, and Simpson's-paradox checks, then produce a confidence grade and stakeholder-safe caveats.

## When to use

- analysis findings need validation before presentation;
- the user asks whether numbers, calculations, or findings can be trusted;
- a validation agent/checkpoint runs in a pipeline;
- confidence badges or blocker/warning reports are needed.

## Workflow

### Source of truth

Prefer executable helpers and agent standards over prompt memory:

- `helpers/structural_validator.py` when available;
- `helpers/logical_validator.py` when available;
- `helpers/business_rules.py` when available;
- `helpers/simpsons_paradox.py` when available;
- `helpers/confidence_scoring.py` for the authoritative confidence grade;
- validation steps in `agents/validation.md` when running inside the pipeline.

If helpers are unavailable or cannot run in the current context, perform a transparent static/manual validation and cap confidence appropriately.

### Layer 1 — Structural validation

Check schema, expected columns, primary-key uniqueness/nulls, critical-field null rates, row-count adequacy, and referential integrity for multi-table work. Halt or mark `BLOCKER` for empty/insufficient data, missing required columns, or severe null/key failures.

### Layer 2 — Logical validation

Check aggregation consistency, segment exhaustiveness, temporal consistency, trend continuity, denominator alignment, and metric-definition compatibility. Definitional flaws are blockers: explain why the comparison is invalid and provide a corrected definition or query if possible.

### Layer 3 — Business rules validation

Check plausible ranges, numerator <= denominator, nonzero denominators, valid rates, nonnegative quantities where required, YoY/plausibility thresholds, and domain expectations. If a counterintuitive result appears, investigate classification consistency, temporal coverage, mix shift, and definition errors before treating it as a finding.

### Layer 4 — Simpson's paradox / segment-first check

For aggregate findings, segment by plausible confounds such as geography, cohort, platform, source, lifecycle stage, or day/week. Report whether the aggregate direction holds within segments, reverses, or is at risk because segment data is unavailable.

### SQL/provenance requirements

Include executable SQL or query descriptions for validation checks when data is queryable:

1. duplicate/null/row-count checks;
2. parts-to-whole and ratio recomputation;
3. warning/blocker investigation;
4. segment-first paradox checks;
5. recommended fixes or corrected definitions.

Log queries according to repository query-logging requirements.

### Confidence grade

Use `helpers.confidence_scoring.score_confidence()` when available. If scoring manually, report A-F with blocker override: any blocker makes the finding unpresentable until resolved. Include sample-size, cross-verification, and reproducibility evidence when available.

### Output format

Produce a Semantic Validation Report with:

- confidence score/grade and recommendation;
- table of layer checks with PASS/WARNING/BLOCKER;
- blocker/warning investigation SQL;
- confidence score breakdown;
- what can/cannot be safely said;
- required caveats;
- final verdict: present, present with caveats, or do not present.

## Key contracts preserved from Claude

- `Structural Validation`
- `Logical Validation`
- `Business Rules`
- `Simpson`
- `Confidence Score`
- `BLOCKER`

## Codex adaptation notes

- Use natural language or `$semantic-validation` invocation; do not rely on legacy slash-command-only mechanics.
- Prefer repository helpers, standards, and existing skill composition over duplicating large provider-specific prompts.
- If a required external capability is unavailable, state the blocker and offer the closest safe manual fallback.
