---
name: compare-datasets
description: Compare metrics, findings, definitions, and patterns across two or more connected datasets. Use when users ask how behavior differs across datasets, product lines, regions, or data sources.
---

# Compare Datasets

## Purpose
Identify commonalities, differences, and definition drift across datasets.

## Workflow
1. Identify datasets to compare. If not specified, list available datasets and ask the user to choose.
2. Read each dataset manifest, schema docs, metric dictionary, quirks, and recent history/patterns where available.
3. Verify comparable metrics: same numerator, denominator, filters, grain, and time window. If definitions differ, report definition drift before comparing values.
4. Run data-quality/freshness checks for each dataset or state when relying on existing metadata.
5. Compare in layers:
   - schema/data coverage;
   - metric definitions;
   - metric values and trends;
   - segment patterns;
   - known quirks and caveats;
   - archived findings/patterns.
6. Separate universal patterns from dataset-specific anomalies.

## Output contract
Include a comparison table, definition-drift notes, confidence/caveats by dataset, and recommended next checks.

## Safety
- Do not compare metrics numerically until definitions and time windows are aligned.
- Never assume datasets have the same grain or business meaning because column names match.
