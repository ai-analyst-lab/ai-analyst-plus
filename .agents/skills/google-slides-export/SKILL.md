---
name: google-slides-export
description: Create properly formatted Google Slides decks from Codex analysis outputs while avoiding API errors, text overflow, bad object IDs, oversized batches, and missing provenance. Use when exporting to Google Slides, building shareable presentations, or calling Google Slides tools.
---

# Google Slides Export

## Purpose

Create clean Google Slides presentations with safe API request patterns and consistent design.
This is the Codex-native counterpart to the legacy Claude google-slides-export skill.

## When to use

Use when the user asks for Google Slides, a shareable online presentation, or a Slides export
from analysis/deck artifacts. Also use before making Google Slides API/MCP calls.

## Preflight checklist

Before creating or mutating slides:

- Google Slides/Drive tools are available and authenticated.
- Source deck/narrative/charts exist.
- Object IDs you create are at least 5 characters.
- Use `createSlide`, not invalid request names.
- Never set outline weight to zero; omit the outline block when no border is desired.
- Split request batches to 50 or fewer requests and apply sequentially.
- Delete only confirmed existing object IDs.
- Use generous text boxes with autofit for variable content.
- Save presentation ID/URL immediately with `$session-handoff`.

If Google tools are unavailable, fall back to local Marp/PDF/HTML export through `$export`.

## Design system

Default slide dimensions:

```text
Width:  9144000 EMU
Height: 5143500 EMU
```

Default palette:

- dark navy for headers/section dividers;
- amber/orange accent;
- off-white background;
- white cards;
- dark body text;
- green/red for positive/negative metrics.

Layout zones:

- header bar: full width, about 686000 EMU high;
- content starts around y=800000;
- left/right margins about 457200 EMU;
- keep content above y=4800000.

## Formatting rules

- Use autofit on text boxes with variable content.
- Minimum 3000000 EMU width for sentence text boxes.
- Max 5 content elements per slide, excluding header/title.
- Max 3 bullets per text box.
- No spaces/tabs for alignment; use positioned elements.
- Cards are rectangles first, then text layered on top.
- Include data stamp text boxes on finding slides when provenance is available.

## Slide recipes

Use the closest recipe rather than improvising layouts:

1. **Title slide** — dark background, main title, subtitle/context.
2. **Section divider** — dark background, centered section name.
3. **Header + bullets** — header bar, insight headline, body bullets.
4. **KPI cards** — header plus 2–4 metric cards.
5. **Two-column** — header plus left/right text boxes.
6. **Chart slide** — header, insight headline, body text, chart image.

## Image workflow

Charts must be accessible by Google Slides as HTTPS URLs. Prefer durable Google Drive-hosted
images when tools/auth allow. Temporary public URLs are acceptable only for immediate one-off
exports and must be disclosed as expiring.

For every image:

- verify URL is accessible;
- preserve aspect ratio;
- insert into a dedicated image element;
- save any Drive file ID/URL in `working/session_state.yaml`.

## Data stamps and speaker notes

For finding slides, include an abbreviated data stamp:

```text
50K | Jan-Mar 2026 | EVENTS | B (82)
```

Speaker notes should include full provenance:

```text
Data: [145K rows | Jan-Mar 2026 | ORDERS | Confidence: B (82/100)]
Methodology: segmented comparison
SQL: query log reference or SQL
Verification: cross-verification summary
```

## Self-check

After creation, read or inspect the deck when tools permit and verify:

- title and slide count are correct;
- no text overflow warnings if detectable;
- expected charts are present;
- data stamps/provenance notes are present for finding slides;
- no obvious overlapping elements;
- presentation ID and URL are saved.

Attempt one fix iteration at most, then report remaining issues.

## Rules

- Do not make oversized request batches.
- Do not invent/delete unknown object IDs.
- Do not use expiring chart URLs without warning.
- Do not create slides without saving the presentation URL/ID.
- Do not expose secrets in slide content or speaker notes.
- If live Slides tools are unavailable, produce local deck artifacts instead.
