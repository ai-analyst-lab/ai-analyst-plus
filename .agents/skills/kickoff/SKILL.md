---
name: kickoff
description: Compose and optionally post a short introduction to the AI Analyst Lab community. Use when users want to introduce themselves, say hello, join the Slack/community, make a first post, or kick off participation after setup.
---

# Kickoff

## Purpose

Help the user write a warm community introduction and post it only after confirmation, with safe fallback when Slack tools are unavailable.

## When to use

- the user wants to introduce themselves or post to the community;
- the user mentions Slack introductions, first post, getting involved, or saying hi;
- setup just completed and they want the next community step;
- the user asks for help drafting a short intro.

## Workflow

### 1. Check Slack capability

Determine whether Slack tooling is available. If not, draft the message and provide setup guidance or ask the user to paste it manually. Do not request or print tokens in chat; route secrets to ignored local config if the user explicitly configures Slack.

### 2. Gather intro details

Ask at most one or two questions at a time:

1. name;
2. role/company or context;
3. what they are excited to learn/build.

If enough context exists in `.knowledge/user/profile.md` or conversation history, draft from that and let the user edit.

### 3. Compose message

Write 2-4 sentences that sound natural, first-person, and specific. Include greeting, role/context, learning/building excitement, and one celebratory emoji.

### 4. Confirm before posting

Show the exact message and ask for confirmation or edits. Never post automatically in a live user session.

### 5. Post or save

If confirmed and Slack tools are available, post to the intended introductions channel. Otherwise save the draft to `working/kickoff_intro_{timestamp}.md` or provide copy/paste text.

### Report

Confirm whether it was posted or saved, and suggest the next community or analysis step.

## Key contracts preserved from Claude

- `Slack`
- `introductions`
- `confirm before posting`
- `working/kickoff_intro`

## Codex adaptation notes

- Use natural language or `$kickoff` invocation; do not rely on legacy slash-command-only mechanics.
- Prefer existing repository helpers, MCP tools exposed to the current session, and safe local fallbacks over provider-specific assumptions.
- Never print or commit credentials, tokens, private document contents, or user-specific generated artifacts.
- If automation is unavailable, state the blocker and provide the closest safe manual or local-export path.
