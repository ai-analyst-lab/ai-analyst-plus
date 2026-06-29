---
name: teach
description: Generate teaching visuals for analytics and statistics concepts. Use when users ask to teach a concept, show intuition, make explanatory charts, or create slide-ready learning visuals.
---

# Teach

## Purpose
Render canonical teaching charts for analytics/statistics concepts so explanations are visual, reproducible, and slide-ready.

## Available topics
| Topic | Script | Output |
|---|---|---|
| `signal-vs-noise` | `shared/teach/topics/signal_vs_noise.py` via `.agents/skills/teach/topics/signal_vs_noise.py` wrapper | Bell-curve charts showing how variance changes interpretability of a mean difference. |

## Workflow
1. If no topic is provided, list available topics.
2. Normalize topic names across hyphen, underscore, and spaces.
3. Run the matching shared topic script with `.venv/bin/python` or `python3`; compatibility wrappers under `.agents/skills/teach/topics/` may delegate to `shared/teach/topics/`.
4. Scripts should write charts to `outputs/charts/teach/<topic>/`.
5. Inspect/read generated images when possible and summarize the takeaway in 1-2 sentences.
6. If the topic is unknown, list available topics and do not invent a new chart unless the user asks to create a new topic.

## Adding topics
- Add reusable topic implementations under `shared/teach/topics/`; add thin `.agents/skills/teach/topics/` wrappers only for backwards compatibility.
- Use `helpers.chart_helpers.swd_style()` and `action_title()`.
- Save outputs under `outputs/charts/teach/<topic>/`.

## Safety
- Do not fabricate empirical claims; teaching visuals are illustrative unless explicitly backed by data.
