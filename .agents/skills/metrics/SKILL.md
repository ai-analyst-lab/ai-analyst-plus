---
name: metrics
description: Browse, search, and display metric definitions from the active dataset metric dictionary. Use when users ask what metrics are available, how a metric is calculated, to list/search/show metric specs, or to verify a metric definition before analysis.
---

# Metrics

## Purpose
Browse and explain metric definitions from the active dataset's metric dictionary without querying data unless the user separately asks for analysis.

## Trigger examples
- "show me the metrics", "what metrics do we track?", "list KPIs"
- "how is conversion rate calculated?", "define revenue"
- "search metrics for retention", "what's in the metric dictionary?"

## Workflow
1. Read `.knowledge/active.yaml` to identify the active dataset.
2. Read `.knowledge/datasets/{active}/metrics/index.yaml` and any referenced metric YAML files.
3. Choose the mode from the user's request:
   - list all metrics: table with id, name, category, direction, owner/status;
   - show one metric: full formula, grain, unit, source tables, filters, dimensions, guardrails, typical range, validation status;
   - filter/search: case-insensitive search across ids, names, descriptions, categories, and formulas.
4. If no metric dictionary exists, say so and recommend `$metric-spec` to define metrics.
5. If a named metric is missing, suggest closest matches. If no match exists, inspect schema docs only when useful and suggest candidate metrics to formalize.
6. Flag stale or unvalidated metric specs when `last_validated` is older than 30 days or absent.

## Output contract
- Lead with active dataset and metric count.
- Use compact tables for lists.
- For formulas, include denominator, time window, filters, grain, and caveats when available.
- End with a concrete next step: define via `$metric-spec`, validate via `$data-quality-check`, or analyze the metric.

## Safety
- Do not invent metric definitions. Mark inferred suggestions clearly as suggestions.
- Do not query production data unless the user asks to compute/analyze a metric.
- Never print credentials from manifests or connection files.
