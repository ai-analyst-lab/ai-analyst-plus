---
name: causal
description: Run causal-inference planning and observational treatment-effect analysis when experiments are not possible. Use when users ask whether a feature/change caused an outcome, need retroactive impact measurement, or say they cannot randomize.
---

# Causal

## Purpose
Estimate causal effects from observational data with explicit method selection, assumption checks, sensitivity analysis, and non-negotiable caveats.

## Workflow
1. Clarify the treatment, outcome, unit, timing, comparison group, and decision.
2. Select the weakest defensible method using this decision tree:
   - can randomize? prefer `$experiment` design;
   - comparison group plus pre/post data? Difference-in-differences;
   - observed confounders and overlap? propensity matching or regression adjustment;
   - only before/after? pre-post with low confidence;
   - no credible counterfactual? descriptive analysis only.
3. Use helpers from `helpers.experiment_stats.causal` when available: pre/post, DiD, matching, balance, regression adjustment, and sensitivity helpers.
4. Run assumption checks for the chosen method: parallel trends, overlap/common support, balance, positivity, no anticipation, stable composition, and model specification as applicable.
5. Run sensitivity analysis where possible and translate robustness into plain language.
6. Save working artifacts under `analyses/{slug}/working/` or `working/causal/` and final reports under `reports/`.
7. Produce a report with estimate, interval, assumption verdicts, sensitivity, confidence ladder, caveats, and recommendation.

## Mandatory caveats
- Pre-post: assumes nothing else changed during the period.
- DiD: assumes the control group would have followed the same trend.
- PSM: controls observed confounders only.
- Regression: assumes relevant confounders and model specification are adequate.

## Safety
- Do not claim causality without a credible counterfactual and assumptions.
- If assumptions fail, stop or downgrade to descriptive language.
