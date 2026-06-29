---
name: slide-transform
description: Transform one weak slide into 2-3 improved variants with before/after scoring. Use when users ask to fix, improve, redesign, rewrite, or optimize a specific slide, when deck critique finds low-scoring slides, or when they want multiple presentation approaches.
---

# Slide Transform

## Purpose

Improve slide-level storytelling by diagnosing the original against SO-WHAT/STAKES/EVIDENCE/ASK and generating distinct variants: headline fix, declutter, and story reframe.

## When to use

- the user asks to fix, improve, redesign, transform, or rewrite a slide;
- `$deck-critique` identifies slides below target score;
- a deck rescue needs slide-level variants;
- the user wants multiple ways to present the same finding.

## Workflow

### 1. Validate input

Require the real slide content: text, Marp markdown, image description, slide object, or deck excerpt. If missing, ask for it rather than inventing an example. Clarify audience/decision context when needed.

### 2. Diagnose original slide

Score SO-WHAT, STAKES, EVIDENCE, and ASK from 0-3 each, or reuse `$deck-critique` scores. Identify the primary problem and buried insight.

### 3. Variant A — Headline Fix

Keep most body content but rewrite the title as a specific action headline. Reorder content to support the headline and add context subtitle/data stamp when available.

### 4. Variant B — Declutter

Cut to the 2-3 strongest evidence points, remove redundant bullets, simplify layout, and note what was cut and why.

### 5. Variant C — Story Reframe

Restructure around audience stakes and ask. Split into two slides only when needed for clarity; otherwise keep one strong slide.

### 6. Save transformation report

Write the complete report to:

```text
working/slide_transform_{timestamp}.md
```

Include original slide, variants, scoring table, recommended variant, and chart placeholders only when charts need to be created separately.

### 7. Marp and chart rules

Variants should be valid Marp when deck context uses Marp. Reference existing chart paths only after verifying they exist. If a chart would help but does not exist, add a comment describing the needed chart; do not reference fake image files.

## Key contracts preserved from Claude

- `SO-WHAT`
- `STAKES`
- `EVIDENCE`
- `ASK`
- `working/slide_transform`

## Codex adaptation notes

- Use natural language or `$slide-transform` invocation; do not rely on legacy slash-command-only mechanics.
- Prefer repository helpers, available MCP tools, and safe local fallbacks over provider-specific assumptions.
- Never print or commit credentials, tokens, secrets, private workspace content, or user-specific generated artifacts.
- If an external platform/tool is unavailable, state the blocker and offer the closest safe fallback.
