---
name: patterns
description: Browse, search, and use recurring analytical patterns discovered across archived analyses. Use when users ask what patterns have been seen, whether a finding is recurring, or need historical context for a new finding.
---

# Patterns

## Purpose
Surface recurring analytical patterns from `.knowledge/analyses/_patterns.yaml` and optional cross-dataset observations.

## Workflow
1. Read `.knowledge/active.yaml` to identify the current dataset.
2. Read `.knowledge/analyses/_patterns.yaml`; if absent, explain that patterns appear after multiple archived analyses.
3. If the user asks globally, also inspect `.knowledge/global/cross_dataset_observations.yaml` when present.
4. Support modes:
   - list dataset patterns sorted by occurrences/confidence;
   - show a pattern by id;
   - search descriptions, metrics, dimensions, evidence, and tags;
   - compare a current finding to known patterns.
5. Flag stale patterns when last seen more than 60 days ago.
6. Suggest revalidation before relying on a pattern in a decision.

## Output contract
- Include pattern id, description, type, occurrences, confidence, last seen, and evidence analysis ids.
- Keep empty-state responses short and actionable.

## Safety
- Do not create patterns from a single observation.
- Do not imply a pattern is causal unless archived evidence establishes causality.
