---
name: show-off
description: Create and optionally post a Slack/community showcase of what the user built, using git status/diff to detect their work, a first-person narrative, and an ASCII architecture diagram. Use when users want to share, show off, celebrate, post their work, or after meaningful build/analysis milestones.
---

# Show Off

## Purpose

Autonomously identify the user's actual additions/modifications, turn them into a concise showcase narrative and diagram, and post only after confirmation.

## When to use

- the user asks to share, show off, post, or celebrate what they built;
- a significant analysis, pipeline, skill, helper, chart set, or artifact was completed;
- the user wants a community update for Slack or show-and-tell;
- they need a visual architecture summary of recent work.

## Workflow

### 1. Detect the user's work

Run git inspection rather than asking the user to summarize:

```bash
git status --short
git diff
git log --oneline --all --not --remotes
```

Read relevant new/modified files. Ignore secrets, caches, lockfiles, environment files, generated dependency folders, and irrelevant local artifacts. Distinguish template/repo baseline from user-created changes.

### 2. Write the narrative

Compose 2-3 first-person sentences explaining what was built, how it works, and why it is interesting. Be specific about actual files, helpers, data, charts, skills, or pipeline pieces.

### 3. Build the ASCII diagram

Create a polished monospace architecture diagram with:

- input/trigger at top;
- core engine in a prominent box;
- fan-out to major components/artifacts;
- output paths at bottom;
- aligned connectors and readable spacing.

### 4. Confirm before posting

Show the exact Slack/community message with narrative and diagram in triple backticks. Ask for confirmation or edits. Never post live without explicit confirmation.

### 5. Post or save

If Slack/community tools are available and user confirms, post to the intended show-and-tell channel. Otherwise save to `working/show_off_{timestamp}.md` and give copy/paste text.

### Report

Confirm posted/saved status and include path or channel.

## Key contracts preserved from Claude

- `git status --short`
- `ASCII diagram`
- `show-and-tell`
- `confirm before posting`
- `working/show_off`

## Codex adaptation notes

- Use natural language or `$show-off` invocation; do not rely on legacy slash-command-only mechanics.
- Prefer repository helpers, available MCP tools, and safe local fallbacks over provider-specific assumptions.
- Never print or commit credentials, tokens, secrets, private workspace content, or user-specific generated artifacts.
- If an external platform/tool is unavailable, state the blocker and offer the closest safe fallback.
