---
name: theme-picker
description: Help choose a visual theme for charts or decks when the user asks for a visualization and has not specified a theme. Use for interactive chart/theme selection, not inside unattended pipeline runs.
---

# Theme Picker

## Purpose
Choose a chart/deck theme while preserving the repository's chart helper standards.

## Workflow
1. Skip theme selection when the user already named a theme, `working/session_state.yaml` has `default_theme`, or the chart is inside an unattended pipeline/deck run.
2. List available themes with `helpers.theme_loader.list_themes()` when possible.
3. For each brand theme, read display name and description from `themes/brands/{name}/theme.yaml`.
4. Ask the user to choose a theme for interactive work.
5. Render charts through standard helpers only: call `swd_style()` and use palette/theme helpers rather than hardcoded colors.
6. Offer once to remember the choice by writing `default_theme` to `working/session_state.yaml`.
7. For new or edited themes, run `python scripts/check_theme.py <name>` if that script exists, plus palette/WCAG checks where applicable.

## Safety
- Do not interrupt pipeline runs with theme menus.
- Keep themes accessible: validate contrast and avoid unreadable dark-background combinations unless chart helpers support them.
