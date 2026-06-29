---
name: data-profiling
description: Profile data tables for schema, completeness, distributions, cardinality, outliers, freshness, and join keys. Use when users ask to profile/explore a table before analysis or validate data shape.
---

# Data Profiling

## Purpose
Produce a structured profile of one or more tables before deeper analysis.

## Workflow
1. Confirm active dataset from `.knowledge/active.yaml` and selected table(s).
2. Read schema metadata and quirks before querying.
3. Use existing helpers such as `helpers.schema_profiler` or connector-specific profiling utilities when available.
4. Profile:
   - row count and date range;
   - column types and null rates;
   - distinct counts and top values;
   - numeric distributions and outliers;
   - key uniqueness and candidate joins;
   - freshness and gaps;
   - obvious business-rule violations.
5. Save artifacts under `working/data_profiles/` when generating files.
6. Recommend follow-up `$data-quality-check` or analysis based on profile risks.

## Output contract
Summarize table health, notable risks, candidate keys, useful dimensions, and safe next analyses.

## Safety
- Respect query budgets and sample large tables when appropriate.
- Do not print sensitive raw values; aggregate or redact identifiers.
