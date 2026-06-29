---
name: guardrails
description: Pair success metrics with guardrail metrics and check trade-offs before presenting improvements as wins. Use when defining metrics, reporting metric lifts, analyzing positive changes, or celebrating performance gains.
---

# Guardrails

## Purpose
Prevent false wins by checking whether improvements in a success metric degrade another important business metric.

## Workflow
1. Identify the success metric and claimed improvement.
2. Identify at least one guardrail metric that captures a different dimension of value: quality, retention, satisfaction, support load, margin, safety, or long-term health.
3. Use existing metric specs and available data to compute guardrails over the same period and segment as the success metric.
4. If guardrail data is unavailable, look for proxy guardrails and document missing instrumentation.
5. Classify the result:
   - `CLEAR`: guardrail stable or improved;
   - `TRADE-OFF`: mild degradation that needs net-impact framing;
   - `DEGRADED`: meaningful degradation; do not present the success metric as a simple win.
6. Quantify net impact where possible, especially for revenue/margin trade-offs.

## Common guardrails
- Conversion rate → average order value, return rate, margin.
- Signup rate → activation, retention, qualified-user rate.
- Revenue per user → churn, support tickets, satisfaction.
- Speed/time-to-complete → error rate, quality, reopen rate.
- Engagement → retention, revenue, unsubscribe/churn.

## Output contract
Include a `Guardrail Check` table with success metric, change, guardrail, change, verdict, and caveat/recommendation.

## Safety
- Never celebrate a lift without a guardrail check or an explicit missing-guardrail caveat.
- Do not invent guardrail data; mark unavailable guardrails clearly.
