---
name: distribution-profiler
description: Profile numeric metric distributions and recommend summary statistics, transformations, tests, and A/B methods. Use when users ask what distribution a metric follows, whether data is normal, what statistical test to use, or before analyses that assume normality.
---

# Distribution Profiler

## Purpose

Prevent invalid statistical conclusions by checking numeric distribution shape, summary-statistic fit, and test assumptions before analysis or experimentation.

## When to use

- the user asks to profile a column, metric, or distribution;
- the user asks if data is normal or what test to use;
- an A/B test or regression depends on numeric metric assumptions;
- a skewed, zero-inflated, bounded, count, or heavy-tailed metric is likely.

## Workflow

### 1. Identify metric and unit of analysis

Clarify the column/query/derived metric and the unit: per user, per session, per order, per day, etc. Aggregate to the unit used by the decision before profiling.

### 2. Extract data safely

Use the active dataset and repository connection helpers. For large tables, sample responsibly and report sample criteria. Exclude nulls only with an explicit count and caveat.

### 3. Compute diagnostics

Calculate:

- n, null count, zeros, unique count;
- min/max and bounds;
- mean, median, mean/median ratio;
- standard deviation, IQR, MAD, CV;
- skewness and excess kurtosis;
- integer/count flag;
- variance-to-mean ratio for counts;
- normality/log-normality tests when appropriate;
- top 1% share and outlier influence;
- bimodality signal when relevant.

### 4. Identify likely distribution family

Classify as one or more of: normal-ish, log-normal, gamma/exponential, Poisson, negative binomial, binomial/beta/bounded rate, zero-inflated, mixture/bimodal, heavy-tailed, or nonstandard. Report confidence and alternatives when tests disagree.

### 5. Recommend analysis methods

For the identified shape, recommend:

- valid central tendency and spread;
- what not to report;
- two-group test;
- regression/GLM family;
- bootstrap or nonparametric alternative;
- A/B sample-size implications;
- transformation only when appropriate.

### 6. Chart the distribution

When useful, generate a histogram/density/ECDF/QQ-style diagnostic chart using `$visualization-patterns` and save to `outputs/charts/` or `working/`.

### Output

Produce a Distribution Profile report with diagnostics table, distribution verdict, valid summaries, recommended tests, A/B guidance, transformations, caveats, and chart path.

## Key contracts preserved from Claude

- `Distribution Profile`
- `mean/median`
- `skewness`
- `A/B`
- `outputs/charts`

## Codex adaptation notes

- Use natural language or `$distribution-profiler` invocation; do not rely on legacy slash-command-only mechanics.
- Prefer existing repository helpers, MCP tools exposed to the current session, and safe local fallbacks over provider-specific assumptions.
- Never print or commit credentials, tokens, private document contents, or user-specific generated artifacts.
- If automation is unavailable, state the blocker and provide the closest safe manual or local-export path.
