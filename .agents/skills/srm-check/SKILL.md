---
name: srm-check
description: Detect Sample Ratio Mismatch in experiment or A/B test data before treatment-effect analysis. Use whenever experiment data, treatment/control groups, variants, buckets, randomization, or A/B tests are mentioned or detected.
---

# SRM Check

## Purpose
Block or warn on broken experiment randomization before analyzing outcomes.

## Workflow
1. Detect experiment assignment columns such as `variant`, `group`, `treatment`, `control`, `arm`, `experiment_group`, `bucket`, or small-cardinality assignment fields.
2. Determine expected allocation from experiment metadata, user input, or equal allocation by default.
3. Count units by assignment group at the correct randomization unit, usually user id.
4. Run `helpers.experiment_stats.srm_check()` when available, or a chi-squared goodness-of-fit test.
5. Interpret:
   - p > 0.05: `PASS`;
   - 0.01 < p <= 0.05: `WARNING`;
   - p <= 0.01: `BLOCK`.
6. For multi-day experiments, check SRM over time and by key segments when sample size allows.
7. If `BLOCK`, halt treatment-effect interpretation and recommend investigating assignment, logging, exposure, filtering, and pipeline issues.

## Output contract
Show expected vs observed counts, deviations, chi-square statistic, p-value, verdict, and recommended next step.

## Safety
- Do not skip SRM for experiment analyses.
- Do not report experiment impact as trustworthy when SRM blocks randomization integrity.
