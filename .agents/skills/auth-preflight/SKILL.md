---
name: auth-preflight
description: Check Google Workspace MCP/API authentication before Google Docs, Slides, or Drive work. Use before Google exports, Drive uploads, online decks/docs, or when users mention Google Docs, Google Slides, Drive, upload/share to Google, or Google API auth failures.
---

# Auth Preflight

## Purpose

Fail fast on Google Workspace authentication and tool availability before generating content that depends on Docs, Slides, or Drive.

## When to use

- a task will call Google Docs, Slides, Drive, or Google Workspace tools;
- the user asks to create/export/upload/share a Google Doc or Google Slides deck;
- a workflow needs Drive-hosted image URLs;
- the user sees auth, permission, or image-access errors from Google tools.

## Workflow

### 1. Detect configured Google tooling

Inspect available MCP/resource/tool configuration in this Codex environment. Check `.mcp.json` only if it exists and never print credentials. Identify whether Docs, Slides, Drive, or full Workspace tools are available.

If no Google tooling is configured, stop Google-dependent work and provide concise setup guidance or offer a local export fallback such as docx, Marp, PDF, or local HTML.

### 2. Check credential presence without exposing secrets

Look for expected credential/token files only by existence, size, and freshness. Do not cat, print, or commit token contents. Common locations vary by MCP implementation, so report what was checked at a high level rather than assuming one provider.

### 3. Test with a lightweight create operation

When tools are available, prefer a create-style test over reading an arbitrary existing doc, because read permissions can fail on a specific document even when auth is valid. Create a short-lived test document/presentation when safe, capture the resulting ID, and clean it up if the tool supports deletion.

### 4. Interpret outcomes

| Outcome | Meaning | Action |
|---|---|---|
| create succeeds | auth OK | proceed with Google workflow |
| tool unavailable | MCP not loaded/configured | ask user to configure/restart or use local fallback |
| auth/401 | token missing/expired | guide re-auth and ask user to retry |
| forbidden/403 on create | API disabled/quota/scope issue | report exact likely issue and stop |
| permission error on read only | document-specific access issue | ask for sharing/access or use create/upload flow |

### 5. Report auth status

Return a short preflight result:

```text
Auth: OK|FAILED|PARTIAL
Google capability: Docs|Slides|Drive|Workspace|none
Test: create/read/config-only
Next: proceed|reauth|use fallback
```

Never continue into Google-dependent generation after a failed preflight unless the user explicitly chooses a local fallback.

## Key contracts preserved from Claude

- `Google Workspace`
- `Docs`
- `Slides`
- `Drive`
- `Auth: OK`
- `local fallback`

## Codex adaptation notes

- Use natural language or `$auth-preflight` invocation; do not rely on legacy slash-command-only mechanics.
- Prefer existing repository helpers, MCP tools exposed to the current session, and safe local fallbacks over provider-specific assumptions.
- Never print or commit credentials, tokens, private document contents, or user-specific generated artifacts.
- If automation is unavailable, state the blocker and provide the closest safe manual or local-export path.
