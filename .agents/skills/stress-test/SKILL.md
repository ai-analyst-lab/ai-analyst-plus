---
name: stress-test
description: Stress-test an analysis plan, hypothesis, or proposed finding for weaknesses before execution or stakeholder presentation. Use when users ask to challenge a plan, review assumptions, or find analytical failure modes.
---

# Stress Test

## Purpose
Find failure modes in an analysis before they create misleading results or stakeholder rework.

## Workflow
Evaluate seven dimensions:
1. Hypothesis clarity: is the claim testable and falsifiable?
2. Baseline validity: is the comparison period/group appropriate?
3. Survivorship bias: are excluded/dropped entities changing the answer?
4. Segment coverage: could aggregate results hide subgroup reversals?
5. Confound identification: what else changed at the same time?
6. Kill criteria: what result would disprove the hypothesis or stop the work?
7. Output alignment: does the deliverable match the decision and audience?

For each dimension, assign PASS/WARN/FAIL, evidence, and recommended fix. Prioritize fixes that change the decision or interpretation.

## Output contract
Produce a Stress Test Scorecard with overall grade, top risks, required fixes before analysis, optional improvements, and go/no-go recommendation.

## Safety
- Be adversarial about assumptions but constructive about fixes.
- Do not overstate certainty; stress tests identify risk, not truth.
