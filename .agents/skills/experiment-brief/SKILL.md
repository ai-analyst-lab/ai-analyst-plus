---
name: experiment-brief
description: Create an experiment brief before designing or launching an A/B test. Use when users have a hypothesis and need north-star metric, guardrails, success criteria, baseline validation, and feasibility framing.
---

# Experiment Brief

## Purpose
Turn an experiment idea into a decision-ready brief before power analysis, launch, or analysis.

## Workflow
1. Validate any user-provided baseline rates or sample sizes against available data when possible; otherwise label as assumed.
2. Verify that proposed metrics and guardrails are trackable in the active dataset or metric dictionary.
3. Extract the hypothesis in `If we change X for population Y, then metric Z will move because mechanism M` form.
4. Define one north-star/primary metric with numerator, denominator, window, population, exclusions, and direction.
5. Define guardrail metrics using `$guardrails` principles.
6. Define success criteria: minimum detectable effect, practical significance threshold, statistical threshold, and decision rule.
7. Estimate feasibility and duration using `$experiment`/power helpers where possible.
8. Hand off to `$experiment design` or analysis workflow.

## Output contract
Sections: Hypothesis, North Star Metric, Guardrail Metrics, Success Criteria, Feasibility Estimate, Next Step, and Handoff.

## Safety
- Do not accept unverified baselines as facts.
- Do not launch or interpret experiments without SRM and guardrails.
