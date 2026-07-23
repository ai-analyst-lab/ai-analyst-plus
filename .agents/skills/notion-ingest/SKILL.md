---
name: notion-ingest
description: Ingest Notion workspace/page/database content into organization knowledge: glossary terms, metrics, products, objectives, teams, and raw query archaeology markdown. Use when users want to import, crawl, sync, or bootstrap business context from Notion docs.
---

# Notion Ingest

## Purpose

Convert Notion documentation into structured `.knowledge/organizations/` context and raw archaeology records with safe auth, scoped crawling, rate limiting, and reviewable classifications.

## When to use

- the user asks to import, crawl, connect, or sync Notion docs;
- the user wants business context, metrics, roadmap, OKRs, or glossary extracted from Notion;
- Notion is the source for organizational knowledge;
- a Notion page/database/workspace URL should populate `.knowledge/`.

## Workflow

### 1. Check Notion access

Use available Notion MCP/API tools or integration config. Never ask for tokens in chat. If Notion access is unavailable, route to `$setup-notion` or provide a simulation/dry-run plan.

### 2. Confirm crawl scope

Ask for or confirm one scope:

1. full accessible workspace;
2. specific database;
3. specific page tree;
4. keyword search.

Do not assume full workspace access when the user only supplied a page or database.

### 3. Crawl breadth-first

Traverse pages/databases with pagination and rate limiting. Track visited IDs to avoid loops. On 429, honor retry/backoff. On non-retryable 4xx, log and skip rather than halting the whole crawl.

### 4. Convert pages to markdown

Convert common block types to markdown: headings, paragraphs, lists, code, quotes, callouts, tables, toggles, child pages, and child databases. Preserve page ID, URL, title, crawl timestamp, and classification in frontmatter.

Save raw pages under:

```text
.knowledge/query-archaeology/raw/notion_{page_id_short}.md
```

### 5. Classify and extract knowledge

Map page content to structured org knowledge:

| Content | Target |
|---|---|
| glossary/definitions | `business/glossary/terms.yaml` |
| KPIs/metrics/formulas | `business/metrics/index.yaml` |
| products/features/roadmap | `business/products/index.yaml` |
| OKRs/objectives/KRs | `business/objectives/index.yaml` |
| teams/roles/org chart | `business/teams/index.yaml` |
| SQL/data patterns | query archaeology raw/curated candidates |

Mark uncertain classifications for review; do not overclaim accuracy.

### 6. Summarize and hand off

Report pages crawled/skipped, extracted counts by category, raw path, and review next steps with `$business`, `$metrics`, or `$archaeology`.

## Key contracts preserved from Claude

- `Notion`
- `BFS`
- `.knowledge/query-archaeology/raw`
- `business/metrics/index.yaml`
- `rate limiting`

## Codex adaptation notes

- Use natural language or `$notion-ingest` invocation; do not rely on legacy slash-command-only mechanics.
- Prefer repository helpers, available MCP tools, and safe local fallbacks over provider-specific assumptions.
- Never print or commit credentials, tokens, secrets, private workspace content, or user-specific generated artifacts.
- If an external platform/tool is unavailable, state the blocker and offer the closest safe fallback.
