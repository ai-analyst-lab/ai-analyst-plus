# Skill-Merge Proposal (deep analysis)

**Status:** proposal — nothing executed. For each cluster: how each skill works *alone*,
where they collide, why they're stronger *merged*, the concrete merged shape, and risk.

Guiding principle: these aren't dead code — each skill does a real job. The problem is
**trigger collision** (the model guesses which fires on the same phrase) and **duplicated
prose** (the same procedure described in two places → silent drift). Merges should remove
those two hazards without losing any capability.

---

## Cluster 1 — Analysis design (`analysis-design`, `analysis-design-spec`, `stress-test`)

**How each works alone**
- `analysis-design-spec` — a *lightweight* gate (2–5 min): fill 7 fields (Question, Decision,
  Data Needed, Dimensions, Time Range, Output Format, Success Criteria) before any query. It's
  Step 2 of the default workflow in CLAUDE.md. Always-on framing.
- `analysis-design` — a *heavyweight* pipeline: hunch → hypothesis sharpening → confound scan →
  investigation plan → V1 → feedback synthesis → V2 redesign. Orchestrates 3 agents. Standalone `/analysis-design`.
- `stress-test` — a *critic*: pressure-tests a finished plan for wrong baselines, survivorship
  bias, confounds, missing kill criteria. Works on a plan from any source.

**The collision:** `analysis-design-spec` and `analysis-design` both claim "design an analysis /
start of every analytical request." On those words the model can't tell which to fire — one is a
2-minute gate, the other a multi-agent pipeline.

**Why stronger merged:** they're a *ladder of depth on the same axis* (frame → design → critique),
not three separate jobs. One entry point that scales depth removes the guess and gives users one
mental model.

**Merged shape:** fold `analysis-design-spec` into `analysis-design` as its **light/default mode**
(the 7-field spec); `analysis-design` escalates to the full pipeline only when the question warrants
it. Keep `stress-test` as a *separate* skill (it has standalone value as a reviewer) but wire it in
as the design's explicit critique step. **Net: 3 → 2 skills.**

**Risk/Effort:** Medium / M. `analysis-design-spec` is referenced as Step 2 in CLAUDE.md's workflow
— must update that reference and preserve the always-on framing behavior.

---

## Cluster 2 — Dataset understanding (`data-inspect`, `data-map`, `explore`, `data-profiling`, `distribution-profiler`, `datasets`)

**How each works alone**
- `data-inspect` (`/data`) — fast **schema** view of the active dataset (tables/columns/row counts).
- `data-map` — comprehensive **cross-table health** answer (PK uniqueness, date alignment, FK
  join-rate matrix, relationship diagram, opening thread). The "tell me about this data" payoff.
- `explore` (`/explore`) — **interactive** poke-around (browse, sample, distributions) with no commitment.
- `data-profiling` — deep **new-dataset** profiling (distributions, temporal, completeness, anomalies).
- `distribution-profiler` — **one column's** distribution (shape, valid stats, recommended test). Distinct.
- `datasets` (`/datasets`) — list of **connected datasets** (source inventory, not contents). Distinct.

**The collision:** `data-inspect`, `data-map`, and `explore` all trigger on "what's in this dataset?"
— same phrase, three skills, three depths. CLAUDE.md already needs **Rules 18 & 19** to hand-arbitrate
(table-scoped → data-quality-check; dataset-wide → data-map). That arbitration is the smell.

**Why stronger merged:** the first four are *depths of one question* ("understand this data"):
schema → health map → interactive → deep profile. Collapsing them behind one entry that scales depth
removes the routing ambiguity Rules 18/19 are patching.

**Merged shape:** one **"understand the active dataset"** skill with depth levels — schema (light) →
cross-table health map (full) → interactive follow-up → deep profile — absorbing `data-inspect`,
`data-map`, `explore`, and `data-profiling`. **Keep `datasets`** (source inventory — different
question) and **`distribution-profiler`** (column-level — different grain) standalone.
**Net: 6 → 3 skills.**

**Risk/Effort:** Higher / M–L. CLAUDE.md Rules 18/19 and several cross-references depend on the
`data-map` distinction; the depth-routing must be re-encoded carefully or first-contact UX regresses.
This is the highest-value *and* highest-care merge.

---

## Cluster 3 — Export (`export` + `google-doc-export`, `google-slides-export`, `notion-export`, `chart-to-drive`)

**How each works alone**
- `export` (`/export`) — the **dispatcher / entry point**; handles email/slack/brief/docx/csv
  directly and routes for gdoc/slides/notion.
- `google-doc-export`, `google-slides-export`, `notion-export` — **format-specific procedures** (MCP
  API specifics, formatting rules) that auto-apply when building that format.
- `chart-to-drive` — a **shared utility** (PNG → Drive URL) used by the Google export skills.

**The collision:** `export` *re-describes* the full gdoc/notion procedure that the standalone format
skills already own → the same steps live in two places and will drift.

**Why stronger together:** this is **de-dupe, not merge**. `export` should *route* to the format
skills, not restate them — single source of truth per format (same pattern as the validation win).

**Merged shape:** slim `export` to a thin dispatcher that **delegates** ("for a Google Doc, the
`google-doc-export` skill owns the procedure"); the format skills stay as the source of truth;
`chart-to-drive` stays as the shared utility. **Net: no skills removed; the duplicated prose removed.**

**Risk/Effort:** Low / S. No behavior change — just stop restating procedures in two places.

> **REASSESSED ON EXECUTION (2026-06-18):** the hunter over-flagged this. `export`'s notion path is
> *already* a thin delegator ("Follows the Notion Export skill" → "Invoke the notion-export agent"),
> and its gdoc path is a *distinct method* (build local `.docx` via `gdoc_builder` → upload with
> `convert_to_google_doc=True`), NOT a restatement of `google-doc-export`'s native-MCP construction.
> No real prose duplication to remove. Only change made: a formatting source-of-truth cross-reference
> on the gdoc path so both Doc-builders share `google-doc-export`'s look. **#1 effectively closed.**

---

## Recommendation & sequence

| # | Merge | Net | Risk | Value | Do? |
|---|-------|-----|------|-------|-----|
| 1 | Export: slim dispatcher to delegate | no removals | **Low/S** | drift killed | **Yes — start here** |
| 2 | Analysis design: spec → light mode of design | 3→2 | Med/M | removes collision | **Yes** |
| 3 | Dataset understanding: collapse 4 by depth | 6→3 | Med–High/L | biggest simplification | **Yes, but last & carefully** (touches CLAUDE.md Rules 18/19) |

Suggested order: **3? no — 1 → 2 → 3** (lowest-risk first; the data-inspection merge last because it
needs the Rules 18/19 rework). `datasets` and `distribution-profiler` stay standalone throughout.
