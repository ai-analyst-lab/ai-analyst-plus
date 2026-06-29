---
name: deck-rescue
description: Restructure a weak or overloaded deck into a focused stakeholder-ready narrative with a new slide outline, before/after comparison, and speaker notes. Use when a deck critique finds major issues or users ask to rescue, rewrite, refocus, shorten, or make a deck executive-ready.
---

# Deck Rescue

## Purpose

Turn a messy deck into a shorter, clearer story with action headlines, evidence discipline, explicit stakes, and a concrete ask.

## When to use

- a deck is low-scoring, too long, unclear, or missing a narrative;
- the user asks to rescue, rewrite, refocus, or executive-polish a deck;
- $deck-critique flags multiple slides below 6/12;
- a stakeholder deck needs a complete story rebuild rather than local slide edits.

## Workflow

### 1. Inventory source content

Read the original deck or outline. Extract claims, numbers, charts, asks, audience, and meeting purpose. Save a raw inventory to `working/content_inventory_{timestamp}.md` when doing a full rescue.

### 2. Diagnose the story problem

Identify missing or weak SO-WHAT, STAKES, EVIDENCE, and ASK. Determine the single narrative spine the rescued deck should tell.

### 3. Design the rescued structure

Default to 4-8 slides. Favor shorter and more focused than the original:

1. title / executive takeaway;
2. context;
3. tension/problem;
4. evidence or driver;
5. recommendation/options;
6. ask/decision;
7-8. optional risk, rollout, or appendix pointer.

Every title must be an action headline. Avoid generic labels such as Overview, Results, or Questions.

### 4. Generate the new deck

Create Marp markdown when possible, using repository themes/components and chart placeholders only when charts need to be created separately. Keep each slide to one idea, max one primary chart, and minimal bullets.

Save to `working/deck_rescue_{timestamp}.marp.md` unless the user specifies another output.

### 5. Before/after comparison and speaker notes

Write `working/before_after_{timestamp}.md` mapping original content to new slides and explaining cuts/merges. Add speaker notes to every rescued slide with talking track, transition, and anticipated question.

### 6. Validate

Run `$deck-critique` on the rescued outline when practical. Recommend `$slide-transform` for any slide still below target.

### Report

Return original vs rescued slide count, projected grade, story spine, files created, and next rendering/export steps.

## Key contracts preserved from Claude

- `working/deck_rescue`
- `before_after`
- `speaker notes`
- `action headline`
- `Deck Rescue`

## Codex adaptation notes

- Use natural language or `$deck-rescue` invocation; do not rely on legacy slash-command-only mechanics.
- Prefer existing repository helpers, MCP tools exposed to the current session, and safe local fallbacks over provider-specific assumptions.
- Never print or commit credentials, tokens, private document contents, or user-specific generated artifacts.
- If automation is unavailable, state the blocker and provide the closest safe manual or local-export path.
