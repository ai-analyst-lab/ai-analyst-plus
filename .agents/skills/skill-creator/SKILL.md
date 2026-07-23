---
name: skill-creator
description: Create, edit, evaluate, package, and improve Codex skills. Use when users want to create a new skill, modify an existing skill, write SKILL.md, add eval prompts, benchmark skill behavior, improve trigger descriptions, or package/review skill resources.
---

# Skill Creator

## Purpose

Guide Codex-native skill creation and iterative improvement while preserving progressive disclosure, safe resource organization, test prompts, and optional benchmark workflows. Provider-neutral tooling contracts live in `shared/skill-creator/`; legacy runnable scripts currently remain bundled under `.claude/skills/skill-creator/scripts/` until extracted.

## When to use

- the user wants to create a skill from scratch;
- the user wants to update, optimize, or evaluate an existing skill;
- a workflow should be captured as reusable instructions;
- skill descriptions, evals, bundled resources, or packaging need improvement.

## Workflow

### 1. Capture intent

Clarify what the skill should enable, when it should trigger, required inputs, expected outputs, dependencies, and whether objective evals are useful. Extract details from the current conversation before asking repeat questions.

### 2. Design the skill structure

Use progressive disclosure:

```text
skill-name/
├── SKILL.md
├── scripts/      # optional deterministic helpers
├── references/   # optional detailed docs loaded as needed
├── assets/       # optional templates/assets
└── evals/        # optional eval prompts
```

Keep `SKILL.md` focused and route large details to references/scripts.

### 3. Write or edit SKILL.md

Include valid YAML frontmatter with `name` and a trigger-rich `description`. Body should cover purpose, when to use, workflow, output format, resources, validation, and anti-patterns. Avoid malicious, credential-exposing, or surprising behavior.

### 4. Add eval prompts when useful

For objective workflows, create `evals/evals.json` with realistic prompts, expected output descriptions, input files, and later assertions. For subjective writing/design skills, prefer qualitative review and examples.

### Shared tooling sources

Read `shared/skill-creator/README.md` for the provider-neutral skill/eval tooling contract. When a requested operation needs legacy scripts that have not yet been extracted, treat `.claude/skills/skill-creator/scripts/` and `.claude/skills/skill-creator/eval-viewer/` as source material to port or run deliberately, rather than copying hidden behavior into Codex.

### 5. Run or simulate evaluation loop

When tooling allows, compare with-skill vs baseline/old-skill outputs, grade assertions, aggregate benchmark results, and collect user feedback. In Codex-only environments without the legacy viewer/subagent tools, save a reproducible local eval plan and run available tests/scripts.

### 6. Iterate and improve description

Use eval/user feedback to revise workflow, resource routing, and the description. Optimize descriptions for correct triggering without over-broad false positives.

### 7. Validate and package

Check frontmatter, paths, references, scripts, and eval schema. If packaging is requested, include only intended resources and no secrets/generated outputs.

## Key contracts preserved from Claude

- `SKILL.md`
- `progressive disclosure`
- `evals/evals.json`
- `benchmark`
- `description`
- `shared/skill-creator/README.md`
- `.claude/skills/skill-creator/scripts/`

## Codex adaptation notes

- Use natural language or `$skill-creator` invocation; do not rely on legacy slash-command-only mechanics.
- Prefer repository helpers, available MCP tools, and safe local fallbacks over provider-specific assumptions.
- Never print or commit credentials, tokens, secrets, private workspace content, or user-specific generated artifacts.
- If an external platform/tool is unavailable, state the blocker and offer the closest safe fallback.
