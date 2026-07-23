---
name: data-quality-check
description: Validate data completeness, consistency, coverage, freshness, and statistical sanity before analysis from Codex. Use at the start of data analysis, before querying or drawing conclusions, after connecting or switching datasets, when results look suspicious, when users ask if data is clean, or when they ask about a specific table and need more than schema.
---

# Data Quality Check

## Purpose

Validate data completeness, consistency, coverage, freshness, and statistical sanity before
analysis. Report issues with severity so the user knows what blocks analysis versus what
should be carried as a caveat.

This is the Codex-native counterpart to the legacy Claude data-quality-check skill.

## When to use

Use this skill proactively:

- at the start of any new analysis that will query or interpret data;
- when connecting, switching, or profiling datasets;
- when results look surprising or suspicious;
- when the user asks whether data is clean, complete, fresh, validated, or reliable;
- when the user asks about a specific named table and needs more than cached schema.

For purely structural schema lookup, `$data-inspect` is enough. For table-scoped questions
such as “tell me about orders,” pair schema inspection with at least a minimum DQ probe.

## Required context

1. Read `.knowledge/active.yaml` to identify the active dataset.
2. Read `.knowledge/datasets/{active}/manifest.yaml` when present.
3. Read `.knowledge/datasets/{active}/schema.md`.
4. Read `.knowledge/datasets/{active}/quirks.md` when present.
5. Use `helpers.connection_manager.ConnectionManager` for data access when probing real
   tables.
6. Log executed SQL with `scripts/log_query.py` when the broader analysis workflow requires
   query logging.

Never guess the dataset. Never expose credentials from manifests or errors.

## Shared standard

Use the provider-neutral data quality rubric in:

```text
docs/standards/data-quality-check.md
```

That standard is the source of truth for:

- minimum table-scoped probes;
- check sequence;
- severity thresholds;
- report format;
- recommendation meanings;
- anti-patterns.

When using this skill, read that standard before running a substantive quality check and
apply it with the Codex-specific context and helper guidance above.

## Anti-patterns

- Do not skip quality checks because the data “looks fine.”
- Do not treat all nulls as equal; distinguish critical from non-critical fields.
- Do not silently fix data. Document every cleaning or exclusion choice.
- Do not analyze through known blockers unless the user explicitly narrows scope around them.
- Do not assume dates, time zones, primary keys, or categorical domains are clean.
- Do not present anomalies as causal explanations without follow-up analysis.
