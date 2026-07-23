---
name: stakeholder-communication
description: Adapt analytical findings to a target audience such as executives, product, engineering, data, or mixed stakeholders. Use when drafting narratives, summaries, reports, decks, or stakeholder updates.
---

# Stakeholder Communication

## Purpose
Tailor the same analytical truth to different audiences without changing the facts.

## Workflow
1. Identify the audience from explicit user wording or context. If unclear and the artifact matters, ask; otherwise default to Product Team.
2. Load relevant communication preferences from `.knowledge/learnings/index.md` when available.
3. Choose the framing:
   - Executive: business impact, risk, decision, resource ask.
   - Product: user/customer implication, priority, next steps.
   - Engineering: root cause, affected systems, fix scope, logs/queries.
   - Data: methodology, validation, caveats, reproducibility.
   - Multi-audience: executive summary plus labeled detail sections.
4. Calibrate detail level and chart count to the audience.
5. Attribute quantitative claims with source detail appropriate for the audience.
6. If drafting a template rather than reporting actual analysis, use placeholders and never fabricate numbers.

## Output contract
Start deliverables with:
```markdown
Audience: <audience>
Adapted for: <role/person if known>
Detail level: <1-4>
```
Then lead with the audience's primary concern.

## Safety
- Tailoring changes emphasis, not evidence.
- Keep caveats that materially affect the recommendation for every audience.
