---
name: metric-spec
description: Define, clarify, document, standardize, or register a business/product metric from Codex using a complete metric spec. Use when the user asks how to measure something, define a metric, create metric documentation, standardize different team definitions, explain a ratio/rate/count, build a metric dictionary, or when an analysis references a metric without denominator, time window, filters, or calculation method.
---

# Metric Spec

## Purpose

Use this skill to make any metric unambiguous enough that two analysts would write the same
SQL and interpret the result the same way. The output is a complete metric specification plus
registration in the repository knowledge system when an active dataset is available.

This is the Codex-native counterpart to the legacy Claude metric-spec skill. Preserve the
same analytical standard, but use Codex-native invocation language rather than Claude slash
commands.

## When to use

Use this skill when:

- defining a new metric;
- documenting an existing metric;
- clarifying how a metric should be calculated;
- resolving different team definitions for the same metric name;
- building or updating a metric dictionary;
- onboarding someone to metric definitions;
- an analysis references a rate, ratio, count, or business metric without clear denominator,
  time window, filters, or calculation method.

## Workflow

### Step 1 — Clarify the metric context

Identify or ask for:

- metric name;
- business decision the metric supports;
- plain-English behavior or outcome being measured;
- numerator and denominator, if applicable;
- unit of analysis/grain;
- time window and attribution window;
- exclusions and filters;
- segmentation dimensions;
- source tables/columns or available dataset context;
- thresholds and historical baseline, if known.

If any critical piece is unknown, state the assumption or ask a concise clarification. Do not
silently define ambiguous metrics like “conversion rate” without a denominator and event
window.

### Step 2 — Write the metric spec

Use this template.

```markdown
## Metric: [Name]

### Definition
**Plain English:** [One sentence a non-technical person can understand]
**Formula:** [Exact calculation]

### Components
| Component | Definition | Source |
|-----------|------------|--------|
| **Numerator** | [What's being counted/summed in the top] | [Table.column] |
| **Denominator** | [What's being counted in the bottom, or N/A for absolute metrics] | [Table.column] |
| **Unit of analysis** | [What one row/entity represents] | [e.g., per user, per session, per order] |

### Segmentation Dimensions
| Dimension | Values | Why |
|-----------|--------|-----|
| [e.g., Device type] | [mobile, desktop, tablet] | [Different UX -> different conversion] |
| [e.g., Acquisition channel] | [organic, paid, referral] | [Different intent -> different behavior] |

### Data Source
- **Primary table:** [schema.table_name]
- **Key columns:** [list]
- **Refresh cadence:** [real-time / hourly / daily / weekly]
- **Latency:** [how delayed the data is]
- **Reference query:** [canonical SQL implementation, if known]

### Thresholds
| Condition | Value | Action |
|-----------|-------|--------|
| **Healthy** | [e.g., >3.5%] | No action needed |
| **Watch** | [e.g., 2.5-3.5%] | Monitor, investigate if persistent |
| **Investigate** | [e.g., <2.5%] | Root-cause analysis |
| **Alert** | [e.g., <1.5%] | Escalate immediately |

### Known Limitations
- [Limitation 1]
- [Limitation 2]
- [Limitation 3]

### Related Metrics
- [Upstream: what drives this metric]
- [Downstream: what this metric drives]
- [Alternative: other ways to measure the same concept]

### Driver Decomposition (Optional)
**Decomposition type:** [Multiplicative / Additive]

| Driver | Formula | Relationship | Data Source |
|--------|---------|--------------|-------------|
| [driver 1] | [formula] | [x / +] | [table.column] |
| [driver 2] | [formula] | [x / +] | [table.column] |

**Diagnostic rule:** If [parent metric] changes, check these drivers in order:
1. [driver 1] — [why this is likely/high leverage]
2. [driver 2] — [what changes here would mean]

**Verification:** [parent metric] = [driver 1] x [driver 2] ... for multiplicative, or
[parent metric] = [driver 1] + [driver 2] ... for additive.
```

### Step 3 — Apply writing rules

1. Make the definition unambiguous enough for another analyst to write the same SQL.
2. Always specify the denominator for rates/ratios.
3. Always specify the time window and attribution window.
4. Always specify exclusions and filters, such as test accounts, internal users, bots,
   canceled orders, or duplicate events.
5. Base thresholds on historical data where possible; if thresholds are illustrative or
   unknown, label them as such.
6. Include known limitations rather than hiding caveats.
7. For ratios, explain how numerator and denominator can move independently.
8. For key business metrics, include driver decomposition when it helps diagnosis.

### Step 4 — Register to the knowledge system when possible

After writing the metric spec, register it to the repository knowledge system when an active
dataset is available. This makes the metric discoverable and reusable.

Registration steps:

1. Read `.knowledge/active.yaml` to get the active dataset name.
2. Verify `.knowledge/datasets/{active}/metrics/` exists; create it if missing.
3. Generate a metric ID: lowercase, hyphenated, no spaces.
   - Example: `Checkout Conversion Rate` -> `checkout-conversion-rate`.
4. Check `.knowledge/datasets/{active}/metrics/index.yaml` to see whether this is an update
   or a new metric.
5. Write `.knowledge/datasets/{active}/metrics/{id}.yaml` with:
   - `name`
   - `definition.plain_english`
   - `definition.formula`
   - `definition.unit` such as percent, count, currency, or ratio
   - `definition.direction` such as `higher_is_better`, `lower_is_better`, or `neutral`
   - `source.tables`
   - `source.sql` when a reference query is available
   - `dimensions`
   - `thresholds`
   - `limitations`
6. Update `.knowledge/datasets/{active}/metrics/index.yaml` with an entry:

```yaml
- id: checkout-conversion-rate
  name: Checkout Conversion Rate
  category: conversion
  created: YYYY-MM-DD
  updated: YYYY-MM-DD
```

If no active dataset exists, still write the metric spec and explain that registration is
blocked until a dataset is active. Do not invent dataset paths.

## Canonical SQL patterns

Use these as starting patterns. Replace `{schema}` and placeholders with the active dataset
schema and metric-specific values.

### Conversion Rate (Event-Based)

```sql
SELECT
    COUNT(DISTINCT CASE WHEN b.user_id IS NOT NULL THEN a.user_id END) * 1.0
    / NULLIF(COUNT(DISTINCT a.user_id), 0) AS conversion_rate
FROM {schema}.events a
LEFT JOIN {schema}.events b
    ON a.user_id = b.user_id
    AND b.event_type = '{{TARGET_EVENT}}'
    AND b.timestamp >= a.timestamp
    AND b.timestamp <= a.timestamp + INTERVAL '{{WINDOW}}'
WHERE a.event_type = '{{SOURCE_EVENT}}'
    AND a.timestamp BETWEEN '{{START_DATE}}' AND '{{END_DATE}}';
```

### Revenue (Order-Based)

```sql
SELECT
    COUNT(DISTINCT order_id) AS total_orders,
    SUM(total_amount) AS total_revenue,
    AVG(total_amount) AS avg_order_value,
    COUNT(DISTINCT user_id) AS purchasing_users
FROM {schema}.orders
WHERE status = 'completed'
    AND order_date BETWEEN '{{START_DATE}}' AND '{{END_DATE}}';
```

### Active Users (DAU / WAU / MAU)

```sql
SELECT
    DATE_TRUNC('{{GRANULARITY}}', timestamp) AS period,
    COUNT(DISTINCT user_id) AS active_users
FROM {schema}.events
WHERE event_type IN ({{QUALIFYING_EVENTS}})
    AND timestamp BETWEEN '{{START_DATE}}' AND '{{END_DATE}}'
GROUP BY 1
ORDER BY 1;
```

### Retention Rate (Cohort-Based)

```sql
WITH cohorts AS (
    SELECT
        user_id,
        DATE_TRUNC('{{GRANULARITY}}', signup_date) AS cohort
    FROM {schema}.users
),
activity AS (
    SELECT DISTINCT
        user_id,
        DATE_TRUNC('{{GRANULARITY}}', timestamp) AS active_period
    FROM {schema}.events
)
SELECT
    c.cohort,
    DATE_DIFF('{{GRANULARITY}}', c.cohort, a.active_period) AS period_number,
    COUNT(DISTINCT a.user_id) * 1.0
    / NULLIF(COUNT(DISTINCT c.user_id), 0) AS retention_rate
FROM cohorts c
LEFT JOIN activity a ON c.user_id = a.user_id
GROUP BY 1, 2
ORDER BY 1, 2;
```

### NPS (Net Promoter Score)

```sql
SELECT
    COUNT(CASE WHEN score >= 9 THEN 1 END) * 100.0 / NULLIF(COUNT(*), 0)
    - COUNT(CASE WHEN score <= 6 THEN 1 END) * 100.0 / NULLIF(COUNT(*), 0) AS nps,
    COUNT(CASE WHEN score >= 9 THEN 1 END) AS promoters,
    COUNT(CASE WHEN score BETWEEN 7 AND 8 THEN 1 END) AS passives,
    COUNT(CASE WHEN score <= 6 THEN 1 END) AS detractors,
    COUNT(*) AS total_responses
FROM {schema}.nps_responses
WHERE submitted_at BETWEEN '{{START_DATE}}' AND '{{END_DATE}}';
```

## Anti-patterns

- Defining a metric without a denominator, time window, or exclusions.
- Reusing one metric name for different team definitions without creating separate specs.
- Setting thresholds from gut feel without labeling them as provisional.
- Skipping known limitations.
- Treating an improving ratio as automatically good without checking numerator and
  denominator movement.
- Registering a metric to the wrong active dataset.

## Output expectations

When responding to the user, provide:

1. the metric spec;
2. any assumptions or clarifying questions;
3. registration status and file paths if registered;
4. recommended next validation step, such as computing the metric once and checking it
   against historical ranges.
