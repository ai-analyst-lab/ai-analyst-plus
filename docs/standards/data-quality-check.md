# Data Quality Check Standard

This provider-neutral standard defines the checks and reporting contract for validating data
before analysis. Claude and Codex skill wrappers should reference this file rather than
forking the substantive rubric.

## Purpose

Validate data completeness, consistency, coverage, freshness, and statistical sanity before
analysis. Report issues with severity so users know what blocks analysis versus what should
be carried as a caveat.

## Required context

- Active dataset pointer from `.knowledge/active.yaml`.
- Dataset manifest from `.knowledge/datasets/{active}/manifest.yaml` when present.
- Cached schema from `.knowledge/datasets/{active}/schema.md`.
- Dataset quirks from `.knowledge/datasets/{active}/quirks.md` when present.
- Repository connection/query helpers for live probes.
- Query logging when SQL is executed as part of a broader analysis workflow.

Do not guess the dataset, expose credentials, or silently use unrelated example data.

## Minimum table-scoped probe

When a request names a specific table and expects more than cached schema, run or request
permission to run:

1. row count;
2. null rate per column, flagging anything above 5%;
3. date range on the primary timestamp/date column when one exists;
4. duplicate check on documented primary key or likely ID column;
5. table-specific notes from `quirks.md`.

If the table is extremely large or warehouse cost is a concern, ask before the full probe.
Still try to run the cheapest row count and primary-key duplicate checks when safe.

## Check sequence

Run checks in this order. Stop and report immediately when a blocker invalidates the planned
analysis.

### 1. Completeness

Check null rates, null primary keys, critical column coverage, missing date ranges, and
unexpected zeros in revenue/count/quantity/denominator columns.

Severity:

- **BLOCKER**: primary key nulls, more than 50% nulls in a critical analysis column, entire
  required date ranges missing.
- **WARNING**: 5–50% nulls in an analysis column, scattered missing dates, unexpected zeros
  in key numeric columns.
- **INFO**: less than 5% nulls in non-critical columns or expected weekend/business-day gaps.

### 2. Consistency

Check duplicate primary keys, referential integrity, mixed date formats, category casing or
whitespace inconsistency, and orphan records.

Severity:

- **BLOCKER**: duplicate primary keys or broken referential integrity affecting more than
  10% of relevant rows.
- **WARNING**: mixed date formats, orphan records under 10%, inconsistent category casing in
  analysis dimensions.
- **INFO**: minor casing or whitespace issues that can be normalized with caveats.

### 3. Coverage

Check expected temporal coverage, required cohorts/segments, expected category domains, and
whether key segments are entirely missing. Prefer existing helper functions such as
`check_temporal_coverage()` and `check_value_domain()` when operating on DataFrames.

Severity:

- **BLOCKER**: key segments entirely missing or temporal coverage below 80% for the analysis
  window.
- **WARNING**: segments with materially fewer rows than expected, coverage 80–95%, unexpected
  category values.
- **INFO**: minor imbalances or coverage above 95%.

### 4. Statistical sanity

Check impossible values, outliers, skew, and effectively empty columns. Prefer existing
helper functions such as `check_null_concentration()` and `check_outliers()`.

Severity:

- **BLOCKER**: impossible values in critical metrics, more than 95% nulls, or values that
  make the planned metric invalid.
- **WARNING**: extreme outliers, more than 50% nulls, or high skew that affects mean-based
  metrics.
- **INFO**: moderate outliers or mild skew.

### 5. Time-series anomaly scan

For date-indexed metric columns, aggregate to daily or weekly grain first. Do not run anomaly
checks directly on raw event rows. Report anomalies as observations, not causal conclusions.

Severity:

- **WARNING**: material spike/drop that may affect the analysis window.
- **INFO**: no notable anomalies or minor expected seasonality.

### 6. Freshness

For each table with a date/timestamp column, check most recent date and infer cadence when
possible.

Severity:

- **WARNING**: data is stale relative to inferred cadence or business expectation.
- **INFO**: data is fresh or explicitly static/historical.

## Report contract

Use this structure for substantial checks:

```markdown
# Data Quality Report: [Dataset Name]
## Date: [YYYY-MM-DD]
## Scope: [dataset/table/question]

### Summary
| Severity | Count | Details |
|----------|------:|---------|
| BLOCKER | X | Must fix before analysis |
| WARNING | X | Carry as caveat / investigate |
| INFO | X | Awareness only |

### BLOCKERS
[List each blocker with table/column, rows affected, impact, suggested fix]

### WARNINGS
[List each warning with likely impact and recommended handling]

### INFO
[List awareness items]

### Data Profile
| Table | Rows | Columns | Date Range | Key Columns |
|-------|-----:|--------:|------------|-------------|

### Recommendation
[PROCEED | PROCEED WITH CAUTION | BLOCKED] — [why]
```

Recommendation meanings:

- **PROCEED**: no blockers and only minor warnings.
- **PROCEED WITH CAUTION**: no blockers but warnings materially affect interpretation.
- **BLOCKED**: blockers found; fix or explicitly scope around them before analysis.

## Anti-patterns

- Skipping quality checks because the data “looks fine.”
- Treating all nulls as equal.
- Silently fixing or excluding data without documentation.
- Analyzing through known blockers without explicit scoping.
- Assuming dates, time zones, primary keys, or categorical domains are clean.
- Presenting anomalies as causal explanations without follow-up analysis.
