---
name: chart-to-drive
description: Upload local chart/image assets to Google Drive and return URLs usable in Google Docs or Slides. Use when charts need to be inserted into Google Workspace documents, when image URLs are required, or when Google doc/slide insertion fails because local images are inaccessible.
---

# Chart To Drive

## Purpose

Bridge local chart artifacts and Google Workspace insertion APIs by uploading charts to Drive with appropriate accessibility and provenance tracking.

## When to use

- a Google Doc or Slides export needs local PNG/SVG/JPEG charts;
- an insertion API requires a public or Drive-hosted URL rather than a local path;
- the user asks to upload charts/images to Drive;
- image insertion fails due to inaccessible URLs or permissions.

## Workflow

### 1. Run auth preflight

Use `$auth-preflight` before any Drive upload. If Google auth is unavailable, offer a local docx/Marp/PDF fallback that embeds local images directly.

### 2. Collect image files

Identify chart assets, usually under `outputs/charts/`, `outputs/`, or a user-specified path. Support PNG, JPEG, and SVG only when the downstream API supports the format. Verify files exist and are non-empty.

### 3. Upload and set accessibility

Use available Google Drive or Workspace upload tools. Prefer direct Drive upload from local file when supported. If a tool requires an HTTPS source, use a safe temporary upload only with user-visible caveats and avoid sensitive charts.

Set permissions to the narrowest level that allows document insertion. For stakeholder docs, prefer organization-accessible links over fully public links when tooling supports it.

### 4. Produce URL map

Write a manifest such as:

```text
working/chart_drive_manifest_{timestamp}.yaml
```

with local path, Drive file ID, URL, permission mode, upload timestamp, and intended document/deck.

### 5. Validate URLs

Before handing URLs to Docs/Slides, verify the URL is accessible to the insertion tool. If validation fails, fix permissions or fallback to local export.

### Report

Return a concise table: local file, Drive URL/ID, permission mode, status, and next insertion step.

## Key contracts preserved from Claude

- `Drive`
- `outputs/charts`
- `working/chart_drive_manifest`
- `URL map`
- `permissions`

## Codex adaptation notes

- Use natural language or `$chart-to-drive` invocation; do not rely on legacy slash-command-only mechanics.
- Prefer existing repository helpers, MCP tools exposed to the current session, and safe local fallbacks over provider-specific assumptions.
- Never print or commit credentials, tokens, private document contents, or user-specific generated artifacts.
- If automation is unavailable, state the blocker and provide the closest safe manual or local-export path.
