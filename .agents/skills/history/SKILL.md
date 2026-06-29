---
name: history
description: Browse and search archived analyses from `.knowledge/analyses`. Use when users ask what they analyzed before, want prior findings, need analysis history, or want to build on previous work.
---

# History

## Purpose
Help users find and reuse archived analysis work from `.knowledge/analyses/`.

## Workflow
1. Read `.knowledge/analyses/index.yaml`; if missing, treat it as an empty archive.
2. Read `.knowledge/active.yaml` to determine the active dataset.
3. Unless the user explicitly asks for all datasets or names a dataset, filter results to the active dataset.
4. Support these modes:
   - recent/list: newest 10 analyses, with date, title, level, dataset, confidence, finding count;
   - detail: show one analysis by exact or partial id;
   - search: search title, question, findings, metrics, and tags;
   - all: show cross-dataset history.
5. For output files referenced by an entry, check whether they still exist and label missing files.
6. Offer follow-up actions such as rerun with fresh data, resume a partial pipeline, open an output, or compare related analyses.

## Output contract
- State the dataset filter used.
- Use tables for browsing and structured bullets for detail views.
- Do not fabricate missing archive fields; show `unknown` or omit them.

## Safety
- Treat archive data as historical context, not proof that current data still behaves the same.
- Revalidate old findings before using them for new decisions.
