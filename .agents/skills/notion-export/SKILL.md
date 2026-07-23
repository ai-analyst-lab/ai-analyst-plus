---
name: notion-export
description: Export Codex analysis results to Notion with structured findings, charts, data stamps, provenance toggles or fallback headings, and optional Analysis Gallery database entry. Use when the user asks to export/share/send analysis to Notion or create a Notion page/database entry.
---

# Notion Export

## Purpose

Export analysis results to a Notion page with chart embeds, confidence/data stamps,
provenance, and recommendations. Supports standalone pages and Analysis Gallery database
entries when Notion tools are available.

This is the Codex-native counterpart to the legacy Claude notion-export skill.

## Preflight

1. Check whether Notion tools are exposed and authenticated in the current environment.
2. If unavailable, stop with setup guidance and offer `$export brief` or `$export docx` as a
   local alternative.
3. Find source material using the same source-selection rules as `$export`:
   - latest narrative;
   - latest analysis report;
   - pipeline summary;
   - storyboard fallback.
4. Gather charts, validation, close-the-loop, query log, provenance blocks, and receipt when
   available.

## Analysis Gallery detection

Search for an “Analysis Gallery” database when Notion search tools exist.

If found:

- create a new database page;
- set properties such as Title, Date, Dataset, Confidence, Status when supported by schema.

If not found:

- create a standalone page;
- tell the user how to create an Analysis Gallery database later.

Avoid duplicate entries for the same dataset/date/title unless the user confirms.

## Page structure

Use this structure:

```text
Title: {Analysis Title} — {Dataset} ({Date})
Icon: confidence-grade color when supported

Callout: Confidence {grade} ({score}/100) — interpretation

H2: Executive Summary
  3–5 sentence overview
  max 3 key findings

H2: Finding 1 — {title}
  Data stamp callout
  Insight/evidence paragraph
  Chart image if available
  Toggle: Show methodology & SQL
    Methodology
    SQL/query log reference
    Cross-verification result

H2: Finding 2 — {title}
  ...

H2: Recommendations
  Numbered action items

H2: Data Quality & Limitations
  Caveats and validation summary

Divider

H3: Provenance
  Toggle or H3 fallback per finding

H3: Analysis Receipt
  Link/path to receipt when available
```

## Toggle fallback

If Notion toggle blocks are unsupported or fail:

- use H3 headings instead;
- show provenance inline;
- note that toggle blocks were unavailable.

## Chart image hosting

Notion image blocks require accessible URLs.

Preferred:

1. durable Google Drive/public asset when Google tools/auth are available;
2. temporary public hosting only for immediate one-off exports, with expiration warning;
3. omit chart with clear note if hosting fails.

Verify image URLs before embedding when possible.

## Notion block types

Use supported blocks only:

- `heading_2` / `heading_3`;
- `paragraph`;
- `bulleted_list_item`;
- `numbered_list_item`;
- `callout`;
- `toggle` when supported;
- `code` with language `sql`;
- `image`;
- `divider`.

## Self-check

After creating the page, read it back when tools permit and verify:

1. title correct;
2. all findings present;
3. expected chart blocks present or missing-chart notes included;
4. data stamps present;
5. provenance sections exist;
6. no empty sections.

Attempt one fix iteration at most. Report any remaining issues.

## Report

Return:

```text
Analysis exported to Notion:
  URL: {page_url}
  Location: Analysis Gallery / Standalone page
  Findings: {N}
  Charts: {N} embedded
  Provenance: toggle blocks / H3 fallback
  Self-check: PASS / PASS with fixes / issues flagged
```

Then use `$session-handoff` or update `working/session_state.yaml` with Notion page id/url.

## Rules

- Never duplicate content without confirmation.
- Data stamps on every finding when available.
- Provenance must be present even if toggles fail.
- Never expose secrets or connection strings.
- Do not claim a live Notion export happened when tools/auth were unavailable.
- One fix iteration maximum after self-check.
