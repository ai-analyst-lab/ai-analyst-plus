---
name: question-router
description: Classify analytical questions into L1-L5 complexity and route them to direct query, chart, guided analysis, deep investigation, presentation pipeline, or North Star handling. Use at the start of data, metric, trend, segment, funnel, revenue, conversion, retention, experiment, or business-performance requests.
---

# Question Router

## Purpose

Route analytical work to the lightest sufficient path, avoiding over-engineering simple lookups while still protecting complex investigations with planning, validation, and appropriate pacing.

## When to use

- a user asks an analytical or metric question;
- before starting `$run-pipeline` or a multi-step investigation;
- when a follow-up changes depth, output format, or pace;
- when North Star Metric intent may need routing to `$north-star`.

## Workflow

### Fast-path obvious L1 questions

If the user asks for a single count, total, average, or fact with no breakdown, hypothesis, comparison, or investigation signal, answer directly after normal dataset/data-quality preflight. Include source citation and 2-3 relevant next actions. Do not show classification overhead.

### Preflight enrichment

Run these silently unless they find something actionable:

1. check feedback/corrections that may affect the analysis;
2. resolve known entity or metric aliases when an index exists;
3. detect whether the user named a dataset different from the active dataset and pause for confirmation before querying;
4. let `$archaeology` context flow downstream when known SQL patterns exist.

### Parse and score

Extract subject, action, scope, output expectation, time range, and named dataset/metric. Score complexity signals:

| Level | Label | Typical signals | Path |
|---|---|---|---|
| L1 | Factual lookup | single number/fact | direct query + citation |
| L2 | Simple comparison | compare, by dimension, breakdown | query + quick chart; use `$visualization-patterns` |
| L3 | Guided analysis | analyze, what is happening, specific question | frame, explore, analyze, validate, present findings |
| L4 | Deep investigation | why, root cause, opportunity sizing, experiment design | deeper pipeline with validation and sizing |
| L5 | Full presentation | deck, board-ready, full pipeline, slides | `$run-pipeline` with story/deck/export |

Ties break toward the lower level unless risk or stakeholder stakes justify more depth.

### North Star intent override

If the request is about a North Star Metric, NSM, strategic anchor metric, audit/design/defense/diagnosis/evolution of a team's main metric, route to `$north-star` rather than the generic L1-L5 path. Use `$metric-spec` for metric calculation details and `$north-star` for strategic anchor judgment.

### Pace selection for L3+

Choose pace separately from level:

- **guided**: announce each phase, run it, pause for confirmation;
- **narrated**: announce phases and continue end-to-end;
- **autopilot**: run silently and show the final output.

Read `working/session_state.yaml` for persisted `pace_mode`. Explicit user choice beats heuristics. Default to `narrated` when unclear. Never default to guided or autopilot.

### Response policy

- **L1/L2**: execute immediately; no classification report; include citations/provenance and contextual next actions.
- **L3-L5**: brief the user with level, pace, plan, estimated time, and relevant preflight findings. Ask for confirmation unless the user clearly said to just run it.
- **Dataset mismatch**: stop and ask which dataset to use.
- **Ambiguity**: default to L2 for simple ambiguity, or ask one concise clarifying question when the route affects cost or risk.

### Phase banners

For guided/narrated L3+ work, use phase banners:

```text
▶ Phase n/N: Name
  Why: one-line reason
  Input: concise summary
```

Close with a one-line result. In guided mode, append proceed/explain/skip/pace/abort options.

## Key contracts preserved from Claude

- `L1`
- `L2`
- `L3`
- `L4`
- `L5`
- `Pace`
- `North Star`
- `working/session_state.yaml`

## Codex adaptation notes

- Use natural language or `$question-router` invocation; do not rely on legacy slash-command-only mechanics.
- Prefer repository helpers, standards, and existing skill composition over duplicating large provider-specific prompts.
- If a required external capability is unavailable, state the blocker and offer the closest safe manual fallback.
