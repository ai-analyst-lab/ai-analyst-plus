---
name: visualization-patterns
description: Apply Storytelling-with-Data chart standards whenever Codex creates charts, graphs, dashboards, or visual evidence. Use for plotting, visualizing, chart-making, decks, funnels, trends, distributions, comparisons, and any analysis deliverable with visuals.
---

# Visualization Patterns

## Purpose

Ensure every visualization is clear, professional, accessible, theme-consistent, and insight-led rather than default or decorative.

## When to use

- any chart, graph, plot, dashboard, or visualization is requested or produced;
- L2+ analysis needs visual evidence;
- deck/storytelling work includes charts;
- a chart needs review for design quality.

## Workflow

### Use repository chart helpers first

Before writing chart code, import and apply helpers from `helpers/chart_helpers.py` whenever possible:

```python
from helpers.chart_helpers import swd_style, highlight_bar, highlight_line, action_title, save_chart
colors = swd_style()
```

Use palette/theme helpers instead of hardcoded hex values. For charts in this repo, call `swd_style()` before rendering. Save final deliverables under `outputs/`; save exploratory charts under `working/`.

### Storytelling with Data rules

- Gray everything first; color only the focus.
- Use at most 2 focus colors plus gray.
- Titles state the takeaway, not just the topic.
- Prefer direct labels over legends.
- Prefer text for single numbers.
- Prefer horizontal bars over pie charts.
- Avoid rainbow palettes, 3D, dual y-axes, chartjunk, heavy borders, and default matplotlib styling.

### Chart type selection

| Relationship | Preferred chart |
|---|---|
| category comparison | bar / horizontal bar |
| trend over continuous time | line |
| few discrete periods | bar |
| relationship between continuous variables | scatter |
| single distribution | histogram |
| distribution by group | box/violin |
| conversion steps | funnel |
| two categorical dimensions + measure | heatmap |
| additive contribution | waterfall |

Pie/donut charts are discouraged and require a strong reason with <=5 segments.

### Declutter checklist

Before finalizing, verify:

- chart title is an action title;
- top/right spines and chart border are removed;
- gridlines are light and purposeful;
- legends are replaced by direct labels where practical;
- labels do not collide;
- precision matches the decision;
- bars start at zero;
- colors meet palette/theme and accessibility expectations;
- data source/provenance appears in subtitle, caption, or surrounding text.

### Multi-chart sequencing

For multi-chart analyses, use Context → Tension → Resolution. Each chart must carry one narrative beat and make the next chart or recommendation easier to understand.

### Review output

When reviewing an existing chart, return:

1. what works;
2. issues by severity;
3. concrete fixes;
4. suggested action title;
5. whether it is stakeholder-ready.

## Key contracts preserved from Claude

- `swd_style`
- `highlight_bar`
- `action_title`
- `gray everything`
- `outputs/`
- `working/`

## Codex adaptation notes

- Use natural language or `$visualization-patterns` invocation; do not rely on legacy slash-command-only mechanics.
- Prefer repository helpers, standards, and existing skill composition over duplicating large provider-specific prompts.
- If a required external capability is unavailable, state the blocker and offer the closest safe manual fallback.
