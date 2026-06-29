---
name: log-correction
description: Manually record analyst mistakes and fixes in `.knowledge/corrections` so future analyses avoid repeated errors. Use when users say to log/save/record a correction, mistake, error, or lesson.
---

# Log Correction

## Purpose
Create a durable correction record with enough detail to prevent recurrence.

## Workflow
1. Gather required details:
   - what was wrong;
   - correct approach/fix;
   - dataset and tables if relevant;
   - severity: critical, high, medium, low;
   - category: sql, metric, schema, logic, other;
   - SQL before/after if applicable.
2. If severity or fix is unclear, ask rather than guessing.
3. Read `.knowledge/corrections/index.yaml` and compute the next `CORR-###` id.
4. Append the correction to `.knowledge/corrections/log.yaml` following the repository template.
5. Update totals, severity counts, category counts, `last_correction_id`, and `last_updated` in the index.
6. Confirm the id, severity, category, description, and fix.

## Safety
- Do not record secrets or raw credentials from queries/configs.
- Use only allowed categories; map custom labels to the closest allowed category and mention the mapping.
- Prefer `prevented_by` values tied to validation layers: structural, logical, business-rules, Simpson's check, or source tie-out.
