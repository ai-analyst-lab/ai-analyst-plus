---
name: architect
description: Create a multi-persona project or feature plan with scope, personas, independent plans, critique, synthesis, waves, task specs, dependencies, and build tracker. Use when users ask to architect, plan, design an implementation, build a roadmap, break down a complex initiative, or think through a project from multiple expert perspectives.
---

# Architect

## Purpose

Run a structured multi-perspective planning workflow that turns a project brief into a master plan, wave structure, task list, dependency map, and build tracker. The provider-neutral methodology lives in `shared/PLANNING_METHODOLOGY.md`.

## When to use

- the user wants to architect a system, feature, course, content pipeline, refactor, or launch plan;
- the work has enough complexity to benefit from 3-5 expert perspectives;
- the user asks for waves, phases, task specs, dependencies, or a build roadmap;
- the user wants a plan created from a brief or existing file.

## Workflow

### 0. Load the shared methodology

Read `shared/PLANNING_METHODOLOGY.md` before planning. Treat it as the source of truth for persona selection, debate/revision phases, master-plan sections, `BUILD_STATUS.yaml` schema, dependency rules, and execution tracker semantics.

### 1. Parse the brief

Read the user's project brief or referenced file. If the deliverable is vague, ask one clarifying question before planning. Identify constraints, desired output, target users, timeline, and implementation environment.

### 2. Choose output paths

Default to:

```text
working/plans/{project-slug}/
MASTER_PLAN.md or {PROJECT}_MASTER_PLAN.md
BUILD_STATUS.yaml
```

Use an existing project-specific `working/plans/` directory when obvious. Ask only when multiple destinations are equally plausible.

### 3. Select personas

Pick 3 personas for small/quick plans, 5 for medium plans, and 7 only for large multi-domain efforts. Customize personas to the brief, for example product strategist, implementation architect, testing lead, UX/editorial reviewer, operations owner, or risk/safety reviewer.

Brief the user on the persona set unless they requested auto-proceed.

### 4. Produce independent plans

For each persona, create a plan covering scope, structure, waves, dependencies, risks, open questions, and pushback. If true parallel subagents are unavailable, run sequentially and note that limitation.

Save persona plans under:

```text
working/plans/{project-slug}/round1/{persona-slug}.md
```

### 5. Debate and revise

Unless the user requested a quick/no-debate plan, synthesize agreements, conflicts, gaps, and decisions into `debate-summary.md`. Then produce revised persona plans under `round2/` that explicitly address the debate outcomes.

### 6. Synthesize the master plan

Write a master plan with:

1. executive summary;
2. assumptions and scope boundaries;
3. wave structure;
4. detailed task specs with IDs, owners/roles, dependencies, files, and acceptance criteria;
5. dependency graph or ordering notes;
6. risk register;
7. open questions;
8. immediate next actions.

### 7. Build tracker

Create `BUILD_STATUS.yaml` with waves/tasks, statuses, dependencies, and acceptance checks. Validate that required artifacts exist before reporting completion.

### Report

Return paths, wave/task counts, major risks, and the recommended first execution step.

## Key contracts preserved from Claude

- `multi-persona`
- `MASTER_PLAN.md`
- `BUILD_STATUS.yaml`
- `working/plans`
- `debate-summary.md`
- `shared/PLANNING_METHODOLOGY.md`

## Codex adaptation notes

- Use natural language or `$architect` invocation; do not rely on legacy slash-command-only mechanics.
- Prefer existing repository helpers, MCP tools exposed to the current session, and safe local fallbacks over provider-specific assumptions.
- Never print or commit credentials, tokens, private document contents, or user-specific generated artifacts.
- If automation is unavailable, state the blocker and provide the closest safe manual or local-export path.
