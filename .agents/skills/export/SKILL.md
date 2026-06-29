---
name: export
description: Export analysis results from Codex into stakeholder-ready formats such as slides, email, Slack update, decision brief, CSV data package, local docx, Google Doc, Notion page, or receipt. Use when the user asks to export/share/send/create a doc/deck/brief/update or wants outputs for stakeholders.
---

# Export

## Purpose

Convert completed or partial analysis outputs into ready-to-share deliverables for different
audiences. This is the Codex-native counterpart to the legacy Claude export workflow.

## Invocation pattern

```text
$export slides
$export email
$export slack
$export brief
$export data
$export docx
$export gdoc
$export notion
$export receipt
$export all
```

`all` generates local text/data formats only: email, Slack, brief, and data. External
resources and audit-heavy artifacts (`gdoc`, `notion`, `receipt`) require explicit request.

## Step 1 — find source material

Choose exactly one primary source, in order:

1. most recent `outputs/narrative_*.md`;
2. most recent `outputs/analysis_*.md` or `outputs/analysis_report_*.md`;
3. `working/pipeline_summary.md`;
4. most recent `working/storyboard_*.md`.

When multiple files exist, prefer latest filename date; otherwise use modification time.
Read the chosen source completely before exporting.

Collect supporting materials when available:

- `outputs/charts/*.png` and `.svg`;
- `outputs/validation_*.md`;
- `outputs/close_the_loop_*.md`;
- `working/query_log_*.jsonl`;
- `working/provenance_*.yaml`;
- `outputs/analysis_receipt_*.md`;
- relevant SQL files under `working/`.

If no source exists, say no analysis results were found and suggest `$run-pipeline` or a
specific analysis first.

## Step 2 — generate requested format

### Format: slides

- If a deck already exists, ask whether to use/export as-is or regenerate.
- If no deck exists, build from latest narrative + charts using deck standards from the
  pipeline/deck creator workflow.
- Output Marp deck under `outputs/`.
- Run `helpers/marp_linter.py` when producing a Marp deck.
- Export PDF/HTML with `helpers/marp_export.py` when Marp CLI is available.

### Format: email

Write `outputs/email_summary_YYYY-MM-DD.md`.

Structure:

- subject line;
- 3-paragraph body: context, key finding, recommendation;
- 1–2 key numbers;
- clear ask or decision.

Use only findings and numbers from the source. Do not invent derived impact.

### Format: slack

Write `outputs/slack_update_YYYY-MM-DD.md`.

Structure:

- one bold headline;
- 3–5 bullets;
- under 300 words;
- key metric/direction/action;
- abbreviated data stamp for each key finding when available.

Use emoji sparingly and do not create multiple variants unless asked.

### Format: brief

Write `outputs/decision_brief_YYYY-MM-DD.md`.

Structure:

- title;
- 3-sentence executive summary;
- numbered key findings;
- recommendation;
- next steps;
- appendix with data sources and methodology.

Target about one page. Use only source material.

### Format: data

Export analysis data tables from `working/` to `outputs/data/` as CSV where source DataFrames
or CSVs are available. Create `outputs/data/README.md` documenting:

- file name;
- source artifact;
- row count;
- columns;
- use case;
- data quality notes.

Do not create new analysis variants; export only data used in the analysis.

### Format: docx

Build a local Word document with repository helpers:

```python
from helpers.gdoc_narrative_parser import parse_pipeline_outputs
from helpers.gdoc_builder import build_readout

data = parse_pipeline_outputs(base_dir=".")
docx_path = build_readout(data, output_dir="outputs")
```

Report the local `.docx` path. This is also the fallback for Google export failures.

### Format: gdoc

Create a Google Doc by first generating `.docx`, then uploading/converting when Google tools
are available.

1. Check Google Docs/Drive MCP/tool availability if exposed in the environment.
2. If auth/tools are unavailable, generate local `docx` and provide manual upload guidance.
3. If source confidence grade is D/F, warn and ask before creating an external doc.
4. Upload with conversion to Google Doc when supported.
5. Write/update `outputs/gdoc_export.yaml` with document id/url, local backup path, source
   hash, version, and version history.
6. Read back or otherwise verify title/sections when tooling permits.

Do not silently fail external upload; always leave a local `.docx` backup.

### Format: notion

Create a Notion page only when Notion tools are configured. Use source narrative, charts,
active dataset, provenance blocks, and receipt when available. Output URL to:

```text
outputs/notion_url_{dataset}_{date}.txt
```

If Notion tooling is unavailable, stop with a clear setup requirement and offer local brief
or docx instead.

### Format: receipt

Generate a reproducibility receipt. Prerequisites:

- query log: `working/query_log_*.jsonl`;
- validation report: `outputs/validation_*.md`;
- cross-verification/provenance when available.

Use `agents/receipt-generator.md` as the source standard. Output:

```text
outputs/analysis_receipt_{dataset}_{date}.md
```

If prerequisites are missing, say what is missing and suggest `$run-pipeline` or validation
before receipt generation.

### Format: all

Run sequentially:

1. email;
2. slack;
3. brief;
4. data.

Skip external resources and receipt. Suggest explicit `$export gdoc`, `$export notion`, or
`$export receipt` afterward if useful.

## Step 3 — report exports

List every created file and any skipped/fallback outputs. Include:

- source file used;
- output paths;
- external URLs if created;
- version when applicable;
- warnings about missing charts, validation, low confidence, or partial analysis.

## Rules

- Never fabricate findings, numbers, recommendations, or impact estimates.
- Always cite source analysis date/dataset when known.
- Adapt detail level to format.
- Include confidence/data stamps when available.
- Never include `gdoc`, `notion`, or `receipt` in `$export all`.
- Generate a local fallback before attempting external upload.
- If source is unchanged and an external export state exists, offer to open/reuse or force a
  new version.

## Edge cases

- Partial analysis: export what exists and clearly note gaps.
- Multiple analyses: pick latest by date or ask user if ambiguous.
- Missing charts: text exports still work; mention charts are unavailable.
- Unknown format: list supported formats and ask for one.
- Offline/no network: produce local files only.
