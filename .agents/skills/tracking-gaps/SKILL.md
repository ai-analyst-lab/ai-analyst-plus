---
name: tracking-gaps
description: Identify missing events, properties, dimensions, or data sources needed to answer an analysis question, then propose workarounds and instrumentation requests. Use when data availability blocks or weakens analysis.
---

# Tracking Gaps

## Purpose
Make data gaps explicit, quantify their analytical impact, and translate them into practical instrumentation requests.

## Workflow
1. Start with data requirements: metrics, events, properties, dimensions, grain, time range, and source systems needed to answer the question.
2. Inventory available data from schema docs, manifests, metric specs, and actual tables when safe.
3. Compare required vs available fields and classify each gap:
   - blocker: answer not possible;
   - limitation: answer possible with caveats;
   - proxy: workaround available;
   - instrumentation: future tracking required.
4. For each gap, describe impact, workaround, confidence loss, and recommended next step.
5. Write instrumentation requests with event/property name, definition, trigger, required fields, owner, priority, and validation check.
6. Recommend the best feasible analysis approach with caveats.

## Output contract
Produce a Tracking Gap Report with Summary, Analysis Feasibility, Gap Details, Prioritized Instrumentation Requests, and Recommended Analysis Approach.

## Safety
- Do not pretend a proxy is equivalent to missing source data.
- Do not block useful partial analysis when limitations can be stated honestly.
