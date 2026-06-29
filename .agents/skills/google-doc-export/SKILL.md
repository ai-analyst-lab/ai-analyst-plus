---
name: google-doc-export
description: Create properly formatted Google Docs from Codex analysis outputs with local docx backup, chart embedding, heading hierarchy, data stamps, provenance appendix, and safe Google Drive upload when tools/auth are available. Use when creating/exporting analysis to Google Docs or formatting a shareable Doc.
---

# Google Doc Export

## Purpose

Create well-formatted Google Docs while avoiding common API failures: overlapping images,
broken heading hierarchy, index invalidation, excessive whitespace, missing local backup, and
lost provenance.

This is the Codex-native counterpart to the legacy Claude google-doc-export skill.

## Decision tree

1. **Analysis report/writeup with charts/tables** → use `.docx → Google Docs` workflow via
   repository helpers.
2. **Simple text-only doc** → direct Google Docs API/MCP calls are acceptable if tools exist.
3. **No Google tools/auth** → generate local `.docx` and provide manual upload instructions.

For analysis documents, prefer `.docx → Google Docs` 90% of the time.

## Recommended workflow — docx then upload

### Step 1 — build local docx

Use existing helpers before writing custom document code:

```python
from helpers.gdoc_narrative_parser import parse_pipeline_outputs
from helpers.gdoc_builder import build_readout

data = parse_pipeline_outputs(base_dir=".")
docx_path = build_readout(data, output_dir="outputs")
```

The local `.docx` is the archival backup. Do not delete it.

### Step 2 — upload with conversion when tools are available

If Google Docs/Drive tools are exposed and authenticated, upload with conversion to Google
Doc. Tool names vary by environment; use the available Google Docs/Drive upload capability
that accepts local file path and conversion, equivalent to:

```python
upload_file_to_drive(file_path=docx_path, convert_to_google_doc=True)
```

If upload/auth fails, keep the `.docx` and report the local path with manual upload guidance.

### Step 3 — write export state

After successful upload, write/update:

```text
outputs/gdoc_export.yaml
```

Include:

- document id;
- document URL;
- title;
- created timestamp;
- source narrative path;
- source content hash when available;
- local docx path;
- charts embedded count;
- version number;
- previous version history.

### Step 4 — handoff state

After creating a Google Doc, immediately use `$session-handoff` or write/update
`working/session_state.yaml` with the document id, URL, title, status, auth account, and
local backup path.

## Direct API workflow for simple docs

Only use direct API/MCP calls for simple text-only documents. Available tools may include:

- create document;
- append text;
- write formatted content blocks;
- insert image with both width and height;
- upload image to Drive;
- read document.

Do not assume older/unavailable functions exist. If a needed formatting operation is not
available, fall back to `.docx` generation.

## Document structure standards

For analysis readouts:

```text
H1: Document Title
H2: Executive Summary
H2: Finding 1 — Title
  Data stamp
  Chart
  The Insight:
  Why this matters for product:
H2: Finding 2 — Title
H2: Data Quality and Limitations
H2: Recommendations
H2: Provenance Appendix
H2: Appendix
```

Spacing rules:

- one H1;
- H2 for sections, H3/H4 for subsections;
- no skipped heading levels;
- no more than two consecutive empty paragraphs;
- no stub headings without body content;
- tables have spacing before and after;
- images get dedicated paragraphs.

## Image rules

- Prefer embedding images in the `.docx` before upload.
- If using direct API image insertion, upload image to Drive first.
- Never rely on expiring temporary image URLs for permanent docs.
- Always specify both width and height when direct-inserting images.
- Standard chart size: about 400pt × 300pt unless aspect ratio requires otherwise.

## Data stamps and provenance

Every finding should include a data stamp from `helpers/provenance_assembler.py` when
available:

```text
[50K rows | Jan-Mar 2026 | EVENTS | Confidence: B (82/100)]
```

For Tier 2+ analyses, add citation markers and a Provenance Appendix with one entry per
finding. Include methodology, SQL/query log reference, cross-verification result, and data
stamp. For Tier 3, link or reference the full analysis receipt.

## Verification

After upload, read back or otherwise verify when tools permit:

- title present;
- Summary/Analysis or expected section headings present;
- no placeholder chart text remains;
- document length is plausible;
- URL/id captured in state files.

If verification fails, attempt one fix or clearly report the issue.

## Rules

- Always create a local `.docx` backup for complex analysis docs.
- Always report both Google Doc URL and local backup path.
- Save resource IDs immediately via `$session-handoff`.
- Do not expose credentials or private connection details.
- Do not use unavailable MCP functions; check actual tools first.
- Do not build complex chart/table documents through fragile index-based API calls when the
  `.docx` conversion path is available.
