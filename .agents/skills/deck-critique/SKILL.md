---
name: deck-critique
description: Score and critique an analytics deck or slide draft using the Data Story Checklist. Use when users ask to review, critique, score, improve, or assess a deck/slides, especially for SO-WHAT, STAKES, EVIDENCE, ASK, narrative flow, and presentation readiness.
---

# Deck Critique

## Purpose

Evaluate decks slide-by-slide and deck-level against stakeholder storytelling standards, then prioritize fixes and hand off weak slides to `$slide-transform` or `$deck-rescue`.

## When to use

- the user asks to critique, review, grade, or improve slides/decks;
- a Marp deck, Google Slides export, or slide outline needs quality review;
- deck rescue or slide transformation needs an initial scorecard;
- a stakeholder-ready presentation should be checked before sharing.

## Workflow

### 1. Load the deck

Accept Marp markdown, slide text, exported outline, images/screenshots, or a Google Slides/Docs representation when tools are available. For Marp, parse slide boundaries and speaker notes. If the deck cannot be read, ask for the deck file or pasted content.

### 2. Score each slide

Use a 12-point Data Story Checklist:

| Dimension | Max | Question |
|---|---:|---|
| SO-WHAT | 3 | Does the headline state the takeaway? |
| STAKES | 3 | Does the slide explain why the audience should care? |
| EVIDENCE | 3 | Is the evidence clear, sufficient, and not cluttered? |
| ASK | 3 | Is the decision/action/next step clear where needed? |

Score 0-3 per dimension and record evidence for each score.

### 3. Deck-level review

Assess narrative arc, executive summary, title flow, recommendation ordering, chart quality, pacing, audience fit, data stamps/provenance, and final ask. Flag banned patterns such as label headlines, chart dumps, mystery-meat metrics, too many bullets, and "Questions?" as the only final slide.

### 4. Prioritize fixes

Classify slides:

- 9-12: stakeholder-ready or minor polish;
- 6-8: needs targeted rewrite;
- 0-5: candidate for `$slide-transform` or `$deck-rescue`.

### 5. Output report

Write or return:

```text
Deck Critique Report
Overall grade
Slide score table
Top 5 fixes
Before/after headline suggestions
Recommended slide-transform targets
Deck-level narrative recommendations
```

If requested, save to `working/deck_critique_{timestamp}.md`.

## Key contracts preserved from Claude

- `Data Story Checklist`
- `SO-WHAT`
- `STAKES`
- `EVIDENCE`
- `ASK`
- `working/deck_critique`

## Codex adaptation notes

- Use natural language or `$deck-critique` invocation; do not rely on legacy slash-command-only mechanics.
- Prefer existing repository helpers, MCP tools exposed to the current session, and safe local fallbacks over provider-specific assumptions.
- Never print or commit credentials, tokens, private document contents, or user-specific generated artifacts.
- If automation is unavailable, state the blocker and provide the closest safe manual or local-export path.
