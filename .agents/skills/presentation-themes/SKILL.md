---
name: presentation-themes
description: Apply Codex-native presentation and Marp theme standards for stakeholder decks, slide structure, narrative arc, HTML components, chart styling, and speaker notes. Use when creating or reviewing presentations, decks, Marp slides, structured stakeholder outputs, or choosing analytics/analytics-dark themes.
---

# Presentation Themes

## Purpose

Create stakeholder-ready decks with a coherent analytical story and consistent visual theme.
This is the Codex-native counterpart to the legacy Claude presentation-themes skill.

## When to use

Use whenever creating, revising, linting, or exporting a presentation or slide deck. Also use
when generating Marp slides from `$run-pipeline`, `$export slides`, experiment readouts, or
any structured stakeholder output.

## Default theme selection

For Codex analytics decks:

| Condition | Theme |
|---|---|
| User explicitly provides theme | Use it |
| Context is workshop, talk, live demo, or dark-room screen share | `analytics-dark` |
| Marp analytics deliverable or standard stakeholder readout | `analytics` |
| Non-Marp/general corporate output without analytics CSS | `corporate` fallback |

In this repository, prefer `analytics` for normal analysis decks. It maps to
`themes/analytics-light.css` and uses warm off-white backgrounds.

## Deck arc

Every analytical deck follows:

```text
Title → Executive Summary → Context → Insight Slides → Synthesis → Recommendations → Appendix
```

The narrative arc is:

```text
Situation → Analysis → Finding → Implication → Recommendation
```

The “headline test” must pass: reading only slide headlines should tell the complete story.

## Slide content rules

- Max 3 bullets per slide.
- One chart per insight slide.
- Headlines are takeaways, not labels.
- Bullets are fragments with key numbers, not dense paragraphs.
- 5–8 slides for short readouts; 10–15 for longer stakeholder presentations.
- Every insight slide answers “so what?”
- Main deck should not dwell on methodology; move details to appendix.
- Include a recommendation slide for decision-oriented analysis.

## Required Marp standards

When producing Marp:

1. Use frontmatter with all required keys:

```yaml
---
marp: true
theme: analytics
size: 16:9
paginate: true
html: true
footer: "[Organization] | [Author] | [Date]"
---
```

2. Use `templates/deck_skeleton.marp.md` and `templates/marp_components.md` as source
   patterns when building decks.
3. Use at least 3 distinct HTML component types, such as `.kpi-row`, `.kpi-card`,
   `.so-what`, `.finding`, `.rec-row`, `.chart-container`, `.callout`, `.badge`, or
   `.data-source`.
4. Validate with `helpers/marp_linter.py`.
5. Export with `helpers/marp_export.py` when requested/available.

## Analytics theme

Use for standard analysis deliverables.

- CSS: `themes/analytics-light.css`
- Background: `#F7F6F2`
- Surface/card: white
- Accent: amber `#D97706`
- Positive: emerald
- Negative: red
- Brand signature: amber left border

Useful components:

- `.metric-callout` — single big KPI.
- `.kpi-row` / `.kpi-card` — KPI group.
- `.finding` — insight card.
- `.chart-container` — chart image in bordered card.
- `.rec-row` — recommendation row with confidence.
- `.so-what` — implication callout.
- `.delta` — change indicator.
- `.badge` — categorical status tag.
- `.data-source` — source/provenance line.

Common slide classes:

- `title`
- `section-opener`
- `insight`
- `chart-full`
- `chart-left`
- `chart-right`
- `kpi`
- `takeaway`
- `recommendation`
- `appendix`

## Analytics-dark theme

Use for workshops/talks and screen-share-heavy contexts.

- CSS: `themes/analytics-dark.css`
- Background: warm dark `#1A1A17`
- Text: off-white
- Accent: amber-orange
- Positive/negative colors adjusted for dark contrast.

Common dark classes:

- `dark-title`
- `dark-impact`
- `section-opener`
- `two-col`
- `diagram`
- `insight`
- `chart-left`
- `chart-right`

When extending CSS, ensure dark-specific variants do not leak light-mode colors.

## Chart rules

- Call `swd_style()` before rendering charts.
- Use palette/theme helpers instead of hardcoded hex values when possible.
- Chart background should visually integrate with deck theme.
- Chart title must not equal slide headline.
- Standard chart image size is `(10, 6)` at 150 DPI unless a chart helper requires otherwise.
- Use `.chart-container` for chart images in Marp.

## Speaker notes

Include speaker notes for presentation decks. Notes should have:

- opening line;
- 2–3 talking points;
- transition to next slide;
- anticipated questions;
- engagement markers where useful: `[POLL]`, `[HANDS]`, `[PAUSE]`, `[ASK]`, `[CHAT]`.

## QR codes

On dark slides, wrap QR codes in a white container for scannability:

```html
<div style="background:#fff; border-radius:10px; padding:6px; display:inline-block;">
  <img src="qr-code.png" style="width:140px; height:140px; display:block;">
</div>
```

## Anti-patterns

- More than one chart per insight slide.
- Label headlines such as “Revenue by Quarter.”
- More than 3 bullets per slide.
- Methodology-heavy main deck.
- Missing “so what.”
- Recommendations hidden in appendix.
- Findings in discovery order rather than story order.
- Marp deck without required frontmatter or HTML components.
