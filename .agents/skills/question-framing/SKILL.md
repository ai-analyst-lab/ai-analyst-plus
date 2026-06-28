---
name: question-framing
description: Clarify ambiguous analytics questions into answerable, scoped analysis plans. Use when a user asks a broad business question, needs assumptions made explicit, or wants a question framed before analysis.
---

# Question Framing

## Purpose
Turn vague or broad requests into concrete analytical questions with scope, metrics, grain, hypotheses, and decision relevance.

## Workflow
1. Restate the user's question in plain language.
2. Identify ambiguity across metric definition, denominator, time window, population, segments, comparison/baseline, and decision/action.
3. Classify complexity from quick lookup to multi-phase causal/root-cause work.
4. Ask only the minimum clarifying questions needed. If reasonable defaults are low risk, state assumptions and proceed.
5. Produce an analysis plan:
   - primary question;
   - metric(s) and definitions needed;
   - time period and grain;
   - population and exclusions;
   - comparison/baseline;
   - segments to inspect;
   - likely data sources/tables;
   - validation and guardrail checks;
   - expected artifact.
6. Route to `$data-quality-check`, `$metric-spec`, `$experiment`, `$run-pipeline`, or direct analysis as appropriate.

## Output contract
Use a compact `Framed Question` block followed by assumptions, open questions, and next step.

## Safety
- Do not over-clarify simple questions.
- Do not hide assumptions; make them visible before analysis.
