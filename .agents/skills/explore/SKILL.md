---
name: explore
description: Quick interactive data exploration within an active dataset. Use when users want to poke around tables/columns, preview distributions, understand data contents, or explore before formal analysis.
---

# Explore

## Purpose
Let users inspect and learn a dataset quickly without running the full pipeline.

## Disambiguation
- Use `$data-map` for first-contact dataset-wide health/entity mapping.
- Use `$data-inspect` for schema-only table/column listings.
- Use `$explore` for interactive poke-around and lightweight questions.

## Workflow
1. Load active dataset context from `.knowledge/active.yaml`, schema docs, and quirks. If absent, look for local example/practice/fixture data; if none exists, ask the user to connect or point to data.
2. Choose mode:
   - dataset overview: identity, source, coverage, table list, relationship sketch, then stop and ask what to explore;
   - table exploration: columns, types, nulls, samples, top values, numeric stats, dates, quality flags, analytical potential;
   - column deep-dive: distribution, null pattern, outliers, business meaning, related dimensions;
   - follow-up analytical question: show Question Router, Framed Query, Data Quality Check, then Answer.
3. Keep exploration fast: no more than a few queries per step.
4. Generate charts with `swd_style()` and chart helpers when visualizing.
5. Save notes to `working/explore_notes_{YYYYMMDD}.md` only after the user asks a real exploration question and actual observations exist.

## Safety
- Read-only operations only.
- Cite actual table/column names and data source.
- Do not invent observations when data is unavailable.
