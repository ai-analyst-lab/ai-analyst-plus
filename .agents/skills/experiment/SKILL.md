---
name: experiment
description: Codex-native experiment lifecycle workflow for design, power analysis, monitoring, A/B test analysis, interpretation, and reporting. Use when the user wants to design an experiment, analyze an A/B test, check SRM/power/guardrails, decide ship/no-ship, or asks whether an experiment worked.
---

# Experiment

## Purpose

Support the full experiment lifecycle from design through analysis and decision. Use coded
statistical helpers from `helpers/experiment_stats/` instead of improvising formulas.

This is the Codex-native counterpart to the legacy Claude experiment workflow.

## Invocation pattern

Use natural language or:

```text
$experiment design
$experiment power <slug>
$experiment monitor <slug>
$experiment analyze <slug>
$experiment interpret <slug>
$experiment report <slug>
$experiment status <slug>
$experiment full <slug>
```

If mode or experiment slug is missing, infer from context when safe; otherwise ask one concise
clarifying question.

## State layout

Use this layout:

```text
experiments/{slug}/
├── experiment.yaml
├── working/
│   ├── analysis_results.json
│   ├── monitoring_update.md
│   └── ...
└── reports/
    └── experiment_report_YYYY-MM-DD.md
```

Use `templates/experiment.yaml` for new configs and `templates/experiment-report.md` for
reports when applicable.

## Helper functions

All statistical work should call coded helpers:

| Function | Use |
|---|---|
| `srm_check()` | sample ratio mismatch gate |
| `srm_diagnose()` | segmented SRM root cause |
| `proportion_test()` | binary/proportion metric treatment effect |
| `welch_test()` | continuous metric treatment effect |
| `ratio_metric_test()` | ratio metric treatment effect |
| `cohens_d()` | standardized effect size |
| `relative_lift()` | percentage lift |
| `adjust_pvalues()` | multiple comparison correction |
| `power_proportion()` | sample size for proportions |
| `power_mean()` | sample size for means |
| `detectable_effect()` | MDE from fixed sample |
| `duration_estimate()` | timeline planning |
| `cuped_adjust()` | CUPED variance reduction |
| `confidence_sequence()` | always-valid intervals for peeking-safe monitoring |
| `bayesian_proportion()` / `bayesian_mean()` | Bayesian sensitivity view |

Import from `helpers.experiment_stats` or the specific submodule as exposed by the package.

## Modes

### Mode: design

Purpose: create a pre-registered experiment config before results are known.

Steps:

1. Capture hypothesis, target metric, expected direction/magnitude, mechanism, target
   population, randomization unit, constraints, guardrails, timeline, and decision rules.
2. Assess feasibility:
   - can randomize → A/B test path;
   - cannot randomize but has comparison group → quasi-experimental path;
   - no comparison group → pre/post with explicit weak-causal caveats.
3. Define treatment, control, randomization unit, exposure rules, analysis unit, primary
   metric, secondary metrics, guardrails, segments, and stopping rules.
4. Write `experiments/{slug}/experiment.yaml` from `templates/experiment.yaml`.
5. Mark status `DESIGNING` or `POWERED` if power analysis is also completed.

Never design decision rules after looking at treatment results.

### Mode: power

Purpose: estimate required sample and duration.

Steps:

1. Read `experiments/{slug}/experiment.yaml`.
2. Identify primary metric type: `proportion`, `continuous`, or `ratio`.
3. For proportions, call `power_proportion(baseline_rate, mde_relative, alpha, power)`.
4. For continuous metrics, call `power_mean(baseline_mean, baseline_std, mde_relative,
   alpha, power)`.
5. Estimate duration with `duration_estimate(total_sample, daily_traffic, allocation)` when
   traffic is known.
6. Update `experiment.yaml` with sample size, duration, and viability.
7. If not viable, suggest narrowing scope, increasing allocation/duration, choosing a more
   sensitive metric, or using a quasi-experimental/causal workflow.

### Mode: monitor

Purpose: check a running experiment for validity and guardrail issues.

Steps:

1. Read `experiment.yaml` and current assignment/outcome data.
2. Run mandatory SRM first using production-sensitive threshold where appropriate:

```python
from helpers.experiment_stats import srm_check
result = srm_check([control_n, treatment_n], [0.5, 0.5], threshold=0.0005)
```

3. If SRM verdict is `BLOCK`, stop, label status RED, and recommend assignment/debug
   investigation.
4. Track sample accumulation vs. powered sample size.
5. Check guardrails with the appropriate helper.
6. Write `experiments/{slug}/working/monitoring_update.md`.

### Mode: analyze

Purpose: run the final or interim treatment-effect analysis.

Steps:

1. Read pre-registered `experiment.yaml`.
2. Run `$data-quality-check` on assignment/outcome data before statistics.
3. Run mandatory SRM gate first. Use positional lists for `srm_check`; do not pass dicts.
4. If SRM verdict is `BLOCK`, halt and write invalid analysis status; do not interpret
   treatment effects.
5. Select test based on primary metric type:

```python
from helpers.experiment_stats import proportion_test, welch_test, ratio_metric_test
```

- `proportion`: `proportion_test(c_success, c_n, t_success, t_n)`;
- `continuous`: `welch_test(control_values, treatment_values)`;
- `ratio`: `ratio_metric_test(num_c, den_c, num_t, den_t)`.

6. Compute effect size/lift.
7. Correct for multiple comparisons across secondary/guardrail metrics with
   `adjust_pvalues(..., method="holm")` unless a different pre-registered correction exists.
8. Check guardrails against pre-registered thresholds.
9. Run segment analysis and watch for Simpson's paradox or interaction effects.
10. Write structured results to `experiments/{slug}/working/analysis_results.json`.

### Mode: interpret

Purpose: classify outcome and recommend action.

Read `analysis_results.json` and `experiment.yaml`, then use this tree:

- SRM/data quality invalid → **INVALID**; do not ship based on results.
- Positive primary metric + clean guardrails → **SHIP**.
- Positive primary metric + degraded guardrails → **INVESTIGATE** or segment/guardrail tradeoff.
- Powered null → **ABORT**; no evidence of benefit at the designed MDE.
- Underpowered null → **LEARN**; extend, redesign, or choose a more sensitive metric.
- Negative primary metric → **ABORT**.

Anchor recommendations to pre-registered decision rules and confidence intervals, not just
p-values.

### Mode: report

Purpose: generate stakeholder-ready markdown.

Steps:

1. Read `analysis_results.json` and `experiment.yaml`.
2. Fill `templates/experiment-report.md` when useful.
3. Tailor to audience: executive, technical, or cross-functional.
4. Write `experiments/{slug}/reports/experiment_report_YYYY-MM-DD.md`.

### Mode: status

Read `experiment.yaml` and display current status, hypothesis, primary metric, sample/power,
timeline, latest SRM/analysis verdict, blockers, and next action.

### Mode: full

Run design → power → analyze → interpret → report in order, stopping at mandatory blockers
such as SRM `BLOCK`, data quality blockers, or missing required inputs.

## Required analysis standards

- Run SRM before treatment effects.
- Treat SRM `BLOCK` as invalid; do not continue to a ship/no-ship conclusion.
- Separate statistical significance from practical significance.
- Report confidence intervals/effect sizes, not only p-values.
- Account for multiple comparisons.
- Check guardrails and segments.
- Document data quality caveats.
- Do not move goalposts after seeing results.
- Do not claim causality for observational/post-hoc analyses without appropriate caveats.

## Query logging and provenance

When SQL is executed, log it with `scripts/log_query.py` as required by repository rules.
Save key inputs, configs, results, and reports under `experiments/{slug}/` so the decision is
reproducible.
