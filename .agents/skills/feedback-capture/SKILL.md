---
name: feedback-capture
description: Capture user corrections, reusable methodology learnings, and positive confirmations into `.knowledge/corrections` and `.knowledge/learnings`. Use when users correct an answer, teach a preference, or ask to remember feedback.
---

# Feedback Capture

## Purpose
Learn from user feedback without derailing the user's actual request.

## Workflow
1. Detect feedback type:
   - correction: wrong number, wrong column/table, missing filter, bad join, flawed logic;
   - learning: "next time", "always", "never", team convention, preference;
   - positive confirmation: user confirms a result or approach.
2. Prioritize correction over learning over positive when multiple signals appear.
3. For corrections, append an entry to `.knowledge/corrections/log.yaml` and update `.knowledge/corrections/index.yaml` with the next `CORR-###` id.
4. For learnings, append a concise dated bullet to `.knowledge/learnings/index.md` under the best category.
5. For positive confirmations, record only if a lightweight positive-feedback log exists or the confirmation validates a reusable method.
6. Acknowledge briefly, then continue the user's actual request.

## Safety
- Never block the user's task if logging fails; report only if the user explicitly asked to log.
- Do not create verbose meta reports for incidental feedback.
- Do not guess details not present in the user's feedback; leave fields null or ask if explicit logging requires them.
