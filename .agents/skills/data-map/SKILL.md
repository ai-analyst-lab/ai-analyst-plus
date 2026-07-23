---
name: data-map
description: Build a first-contact map of a dataset: table inventory, primary keys, date coverage, completeness, join relationships, and a thread to pull. Use when users ask what is in a new dataset or need a dataset-wide overview.
---

# Data Map

## Purpose
Create a concise, query-backed map of a dataset so later analysis starts with table relationships, health, and known risks.

## Workflow
1. Resolve the active dataset and connection/manifest.
2. Inventory tables with row counts, candidate primary keys, and PK health.
3. Identify primary timestamp/date columns and table date ranges.
4. Compute column completeness/null-rate summaries, focusing on analytical keys, timestamps, metrics, and dimensions.
5. Infer foreign keys and produce a join-rate matrix for likely relationships.
6. Check cross-table date alignment and coverage mismatches.
7. Create a simple relationship diagram such as `users -> orders -> order_items`.
8. Surface quirks, blockers, and one promising thread to investigate.
9. Log executed queries using repository query logging conventions.

## Output contract
Include sections: Cross-Table Health, Relationship Map, Join-Rate Matrix, Date Alignment, Completeness Flags, Quirks, Thread to Pull, and Budget/Safeguards.

## Safety
- Respect query budgets; sample large tables when appropriate.
- Do not mutate data.
- Do not infer business meaning from names alone without caveats.
