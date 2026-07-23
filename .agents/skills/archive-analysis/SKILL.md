---
name: archive-analysis
description: Save completed analyses to `.knowledge/analyses` for future recall. Use after validated multi-step analyses, completed pipelines, generated deliverables, or when users ask to save/archive findings.
---

# Archive Analysis

## Purpose
Capture durable metadata about completed analysis work so future sessions can find and reuse it.

## Modes
- Create archive entry for new completed work.
- Verify/read an existing archive entry when the user asks what was saved.

## Workflow
1. Determine whether this is create mode or verification mode.
2. Gather only facts from conversation context and actual files; do not invent findings, metrics, outputs, confidence, or business impact.
3. Read `.knowledge/active.yaml`, `working/session_state.yaml`, recent `outputs/` and `working/` files, validation summaries, and analysis summaries when present.
4. Read `.knowledge/analyses/_schema.yaml` if available.
5. Create an id like `analysis_YYYYMMDD_HHMMSS` and append an entry to `.knowledge/analyses/index.yaml`.
6. Include title, date, dataset, question, level, findings, metrics, agents/tools, output files, tags, confidence, and `partial: true` when evidence is incomplete.
7. Update the active dataset manifest analysis count/last_used when safe.
8. Confirm what was archived and how to browse it.
9. Optionally suggest capturing reusable SQL/table/join knowledge via archaeology helpers when confidence is high.

## Safety
- Archive only what is explicitly stated or present in files.
- Check file existence before listing outputs.
- Never archive credentials or private connection details.
