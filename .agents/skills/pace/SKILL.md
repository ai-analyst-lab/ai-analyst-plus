---
name: pace
description: Set how visibly Codex surfaces multi-step analytical work: guided, narrated, or autopilot. Use when users ask to slow down, narrate, pause between steps, run silently, or change workflow verbosity.
---

# Pace

## Purpose
Persist the user's preferred interaction style for L3+ analyses and pipeline workflows.

## Modes
- `guided`: announce each phase and pause for confirmation before continuing.
- `narrated`: announce phases and continue without waiting unless blocked.
- `autopilot`: minimize narration and return final outputs plus essential caveats.

## Workflow
1. Identify the requested mode from the user's wording.
2. If no mode is specified, show the three modes and ask which one they want.
3. Read `working/session_state.yaml` if it exists.
4. Update or create `pace: <mode>` while preserving unrelated keys.
5. Confirm the new mode and describe its effect in one sentence.

## Safety
- Pace changes presentation, not analytical rigor. Do not skip validation, data-quality checks, provenance, or safety gates in autopilot.
- Respect explicit user requests that override the saved mode for the current task.
