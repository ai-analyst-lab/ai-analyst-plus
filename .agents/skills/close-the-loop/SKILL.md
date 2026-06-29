---
name: close-the-loop
description: Ensure analyses with recommendations end with an actionable follow-up plan: decision owner, success metric, baseline, target, check date, and fallback. Use only after a specific recommendation exists.
---

# Close the Loop

## Purpose
Convert recommendations into accountable follow-up plans.

## Trigger rule
Use only after a recommendation or action item has been made. Do not use for pure exploration before a recommendation exists.

## Workflow
1. Identify the recommendation and decision to be made.
2. Define owner/decision maker, deadline, and required approval if known.
3. Define success measurement: metric, baseline, target, time window, segment, and guardrails.
4. Define follow-up date and evidence needed to decide whether the recommendation worked.
5. Define actions for success, failure, and inconclusive outcomes.
6. Capture assumptions, confidence level, and what would change the recommendation.
7. If the user wants persistence, save the plan under `working/followups/` or append to the relevant archive entry.

## Output contract
Produce a `Follow-up Plan` with decision, owner, metric, baseline, target, check date, success/failure paths, assumptions, and confidence.

## Safety
- Do not invent owners or deadlines; mark unknowns and ask when needed.
- Include guardrails so the follow-up does not optimize one metric at the expense of another.
