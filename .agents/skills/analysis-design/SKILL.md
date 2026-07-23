---
name: analysis-design
description: Design a multi-stage investigation before execution, including hypothesis sharpening, confound scan, prioritized plan, and optional V1-to-V2 redesign from stakeholder feedback. Use for complex investigations, hunches, or analysis planning.
---

# Analysis Design

## Purpose
Build a robust investigation plan for complex questions before spending query or stakeholder time.

## Workflow
1. Detect whether the user needs a fresh investigation plan or a V2 redesign from prior findings plus stakeholder feedback.
2. Preview the architecture: stages, checkpoints, expected artifacts, and urgency/scope compression if relevant.
3. Stage 1 — Hypothesis Sharpener: turn the hunch into a testable question, decision, hypothesis, comparison, segments, and criteria.
4. Checkpoint with the user before proceeding when the plan is materially uncertain.
5. Stage 2 — Confound Scanner: enumerate concurrent changes, selection bias, data-quality risks, alternative explanations, and threats to validity.
6. Stage 3 — Investigation Plan: prioritize checks by information value, define confound controls, required data, kill criteria, and outputs.
7. Optional Stage 3b — V1 execution plan or handoff to `$run-pipeline`/direct analysis.
8. Stage 4 — Feedback Synthesizer when the user provides V1 and stakeholder feedback: map feedback to follow-up questions and a V2 plan.

## Output contract
Produce an Analysis Design Brief with Question, Decision, Hypothesis, Comparison, Segments, Confounds, Criteria, prioritized steps, control strategy, and next action.

## Safety
- Do not estimate causality without causal design or caveats.
- Do not auto-run a large analysis when the user only asked for a plan.
