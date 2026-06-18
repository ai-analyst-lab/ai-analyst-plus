STATUS: REPORT ONLY — NO CHANGES MADE (original investigation).

## Execution status (2026-06-18, post-approval)
- **Win 1 — delete `tieout_helpers.py` shim:** ✅ DONE (`5f6a4b6`-amended). Re-pointed 5 refs;
  import-layer check + health check + 849 tests pass.
- **Win 2 — `semantic-validation` skill vs Validation agent:** ✅ DONE (light consolidation).
  Established single source of truth: the executable validators + `confidence_scoring.py`
  (run by the Validation agent) are canonical; the skill's parallel 0–80 rubric is now
  explicitly "illustrative — `confidence_scoring.py` wins." Fixed the inaccurate CLAUDE.md
  description. Did NOT gut the 476-line skill (it's a CRITICAL gate; full rewrite deferred).
- **Win 3 — `feedback-capture` corrections vs learnings double-write:** ❎ NO CHANGE NEEDED.
  On closer read the skill already routes each message to exactly ONE bucket via Step 1
  "prioritize: Correction > Learning > Positive." Corrections (specific SQL mistakes) and
  learnings (reusable methodology) are distinct signal types — the same legitimate split as
  corrections-vs-archaeology. Not a redundancy.

# AI Analyst v3 — Redundancy / De-duplication Report (Phase D)

**Scope:** Knowledge subsystems (`.knowledge/`), the deprecated `tieout_helpers.py`
shim, and the validation helper stack. Report-only per Shane: write the report, do
not execute any dedup, do not merge anything. Companion to
`docs/internal/v3-merge-plan.md` Phase D.

**Method:** Read the actual schema/index/template files, the helper docstrings and
public APIs, and traced the import/reference graph across `helpers/`, `agents/`, and
`.claude/skills/` via grep. Where I'm uncertain I say so.

**Headline:** Less redundant than the Phase-D worry suggested. The two systems that
*sound* duplicative — `corrections/` vs `query-archaeology/`, and the four validators
— are actually complementary by design. The genuine, low-risk dedup wins are: (1) the
deprecated `tieout_helpers.py` shim, and (2) the `semantic-validation` skill vs the
Validation agent describing the *same* 4-layer stack in two prose copies.

---

## 1. Knowledge subsystems under `.knowledge/`

The `.knowledge/README.md` is an accurate, self-documenting map. Seven subsystems are
*documented*; not all exist on disk yet (several are gitignored / created-on-use).

On-disk today (`find .knowledge`):
`README.md`, `active.yaml`, `analyses/` (`_schema.yaml`, `_patterns.yaml`),
`corrections/` (`log.template.yaml`), `datasets/` (`_metric_schema.yaml`, + gitignored
`novamart/`), `organizations/_example/`, `query-archaeology/` (`curated/index.yaml`,
3 JSON `schemas/`, `raw/.gitkeep`), `references/` (one guide), `reliability/` (8 run
dirs + `log.jsonl`).

Documented-but-absent (in README, not on disk): `learnings/`, `user/`, `global/`,
plus `corrections/log.yaml` + `index.yaml`, `analyses/index.yaml`. These are the
gitignored, populated-on-use halves of each subsystem — their templates ship, content
doesn't. This is intentional (README "Gitignore Policy" section), **not** redundancy.

### 1a. `corrections/` vs `query-archaeology/` — the headline suspicion

**What overlaps:** Both store SQL knowledge keyed by dataset/table.

**Evidence — they are opposite halves of a learning loop, not duplicates:**
- `corrections/log.template.yaml` schema: `severity`, `category (sql|metric|schema|logic|other)`,
  `description`, `fix`, `sql_before`, `sql_after`, `prevented_by`. This captures **what
  went wrong and its fix** — a guardrail against repeating mistakes.
- `query-archaeology/schemas/cookbook_entry.schema.json`: `sql`, `tags`, `use_count`,
  `last_used`, `source_analysis`. Plus `join_pattern.schema.json` (`cardinality`,
  `validated: bool`) and `table_cheatsheet.schema.json` (`grain`, `primary_key`,
  `gotchas`, `common_joins`). This captures **proven, reusable patterns** — institutional
  memory of what works.
- Writers differ: corrections ← `/log-correction` skill + `feedback-capture` skill;
  archaeology ← `helpers/archaeology_helpers.py` (`capture_cookbook_entry`,
  `capture_join_pattern`, `capture_table_cheatsheet`) called by the `archive-analysis` skill.
- Readers differ: corrections read pre-SQL per CLAUDE.md **Rule 15**; archaeology read
  pre-SQL per the `archaeology` skill. Both fire before writing SQL but answer different
  questions ("what mistake must I avoid?" vs "is there a proven pattern to reuse?").

**Recommendation:** KEEP SEPARATE. No merge. The naming is the only thing that invites
confusion. Optional (cosmetic): add a one-line cross-reference at the top of each
subsystem's template clarifying "mistakes" vs "proven patterns."
**Risk:** Merging would conflate avoid-this with reuse-this and break both Rule 15 and
the archaeology skill. Don't.
**Effort:** S (docs note only) / merge would be M and is not advised.

### 1b. `query-archaeology/curated/` vs `query_log.py` (the per-query audit log)

Worth disambiguating because both touch "queries," but they are clearly distinct:
- `helpers/query_log.py` → `working/query_log_*.jsonl`, JSONL, **every** query (Rule 17),
  ephemeral/run-scoped, fields like `query_id`, `pipeline_step`, `claim_ids`, `status`.
  Read by the Validation agent for coverage.
- `query-archaeology/` → curated YAML, a hand/auto-picked **subset** of proven patterns,
  persistent org memory.

**Recommendation:** KEEP SEPARATE. Different storage, granularity, lifecycle, readers.
**Risk/Effort:** none / N/A.

### 1c. `corrections/` vs `learnings/` — a real (minor) overlap in the writer path

**What overlaps:** The `feedback-capture` skill writes to BOTH `.knowledge/corrections/`
AND `.knowledge/learnings/` (skill.md line 76–104 → corrections; line 115–121 →
`learnings/index.md`). `log-correction` writes only to `corrections/`. So a single user
correction can land in two places, and the boundary between "a correction" and "a
learning" is fuzzy (corrections = a specific wrong→right SQL fix; learnings = broader
methodology insight in 6 categories).

**Evidence:** `.claude/skills/feedback-capture/skill.md` lines 76, 86–104 (corrections
path) and 115–121 (learnings path). `learnings/` is gitignored and not on disk yet, so
this overlap is currently latent, not active.

**Recommendation:** KEEP BOTH but TIGHTEN the routing rule in `feedback-capture` so a
given signal goes to exactly one store (specific SQL fix → corrections; general
methodology → learnings), with a cross-link rather than a duplicate entry. This is a
prompt-wording fix, not a code change.
**Risk:** Low — both are gitignored append stores; no importer breaks. Worst case today
is a duplicated note once `learnings/` starts being populated.
**Effort:** S.

### 1d. `analyses/`, `references/`, `organizations/`, `reliability/`, `datasets/`

No overlap found among these — each has a distinct purpose, writer, and reader:
- `analyses/` — completed-run archive (`_schema.yaml`) + recurring patterns
  (`_patterns.yaml`, populated by `patterns` skill after 3+ runs). Written by
  `archive-analysis`, read by `history`/`patterns` skills.
- `references/` — static reference docs (one statistical-distributions guide). Pure
  reference material; no writer.
- `organizations/` — per-org business context (glossary/KPIs/teams), `_example/` template
  committed. Written by `/setup`, read via `helpers/business_context.py`. (Note this is
  the data layer that `business_validation.py` and `metric_validator.py` consume — see §3.)
- `reliability/` — output of the `reliability` skill (`helpers/reliability_stats.py`); 8
  run dirs + `log.jsonl`. Distinct eval subsystem. **Per v3-merge-plan §"Held out"**, these
  8 dirs + log are class-test output flagged to be gitignored / not committed — that's a
  cleanup item, not a dedup item.
- `datasets/` — per-dataset brain (schema/quirks/metrics). The NovaMart instance is
  gitignored; only `_metric_schema.yaml` ships. No overlap.

**Recommendation:** KEEP ALL. **Effort:** N/A.

---

## 2. Deprecated shim — `helpers/tieout_helpers.py`

**What it is:** A backward-compat shim (467 lines). Re-exports `check_null_concentration`,
`check_outliers`, `safe_check_outliers` from `data_quality_extras.py`, and
`format_verification_table` / `overall_status` from `cross_verification.py`. Keeps two
source-agnostic utilities live without deprecation (`read_source_direct`,
`profile_dataframe`); everything else (`compare_profiles`, `format_tieout_table`,
`overall_status`, `validate_profile_pair`, `safe_compare`) emits `DeprecationWarning`.
The dual-path (pandas-vs-DuckDB) tie-out paradigm was replaced by same-source
cross-verification.

**All remaining references (grep `tieout_helpers`, excluding `.git/`):**
| File | Line | Nature |
|------|------|--------|
| `helpers/tieout_helpers.py` | self | the shim |
| `helpers/data_quality_extras.py` | 1, 4 | docstring note "rescued from tieout_helpers" (comment only) |
| `helpers/error_helpers.py` | 216 | comment "(from tieout_helpers)" (comment only) |
| `helpers/health_check.py` | 196 | lists `"helpers.tieout_helpers"` as an importable module to health-check |
| `scripts/check_imports.py` | 9, 34 | imports it + assigns expected-import-count `3` |
| `.claude/skills/data-quality-check/skill.md` | 138 | instructs `from helpers.tieout_helpers import check_null_concentration, check_outliers` |
| `CLAUDE.md` | 98 | "Deprecated" note pointing users to the new modules |
| `helpers/INDEX.md` | 9 | marks it DEPRECATED |
| `docs/internal/v3-merge-plan.md` | 116 | the Phase-D to-do that produced this report |

**No production helper or agent imports its deprecated functions.** The only *live code*
touchpoints are `health_check.py` (mentions the module name) and `check_imports.py` (smoke
import). The only *instruction* that still steers users into it is the data-quality-check
skill at line 138 — and it imports the two functions that actually live in
`data_quality_extras.py` now.

**Recommendation:** SAFE TO DELETE, but do it as a small, ordered change (not a bare `rm`):
1. Edit `.claude/skills/data-quality-check/skill.md:138` → import from
   `helpers.data_quality_extras` instead of `helpers.tieout_helpers`.
2. Remove `tieout_helpers` from `scripts/check_imports.py` (lines 9, 34) and
   `helpers/health_check.py:196`.
3. Update the comment in `error_helpers.py:216` (cosmetic) and the `helpers/INDEX.md`
   row + `CLAUDE.md:98` note.
4. Then delete `helpers/tieout_helpers.py`. Verify `read_source_direct` /
   `profile_dataframe` (its two non-deprecated utilities) have no importers first —
   grep showed none outside the shim, but re-confirm before deleting since they are the
   only functions not already re-homed.
**Risk:** Low, but non-zero: the two "still useful" utilities (`read_source_direct`,
`profile_dataframe`) are NOT re-exported from anywhere else, so deleting the shim drops
them entirely. Confirm zero importers (grep clean today) or re-home them into
`data_quality_extras.py` first. The skill-doc edit is the one user-facing change.
**Effort:** S.

---

## 3. Validation stack

Nine helpers form a deliberate 4-layer pyramid + synthesis. Per-file purpose and the
reference graph (verified by reading docstrings + public APIs + grep):

| Helper | Lines | Purpose | Used by |
|--------|-------|---------|---------|
| `structural_validator.py` | 898 | Layer 1: schema, PK, completeness, dates, referential integrity, domains | Validation agent, semantic-validation skill, 18+ tests |
| `logical_validator.py` | 879 | Layer 2: aggregation, trend, segment exhaustiveness, temporal, ratios | same |
| `business_rules.py` | 872 | Layer 3: plausibility — ranges, metric relationships, rates, YoY, cardinality (uses **default/in-code** rules) | Validation agent, semantic-validation, 7+ tests |
| `simpsons_paradox.py` | 849 | Layer 3: aggregate-vs-segment reversal detection | Validation agent, scoring |
| `confidence_scoring.py` | 1066 | Layer 4: synthesizes 9 factors from the layers into 0–100 + A–F grade (orchestrates outputs; does not import the validators) | Validation agent, storytelling, 6+ tests |
| `cross_verification.py` | 647 | Re-derivation checks (boundary / parts-to-whole / ratio / algebraic) + provenance | Cross-Verification agent, several export agents |
| `business_validation.py` | 192 | **Bridge**: loads metric rules + guardrail pairs from `.knowledge/` YAML and feeds them to the validators | 1 dedicated test |
| `metric_validator.py` | 193 | Validates metric YAML **definitions** (well-formedness) + checks a computed value against its definition | 1 test + `north_star/nsm_checklist.py` |
| `data_quality_extras.py` | 164 | null-concentration + outlier utilities (rescued from tieout) | data-quality-check skill |

### 3a. `business_rules.py` vs `business_validation.py` — NOT duplicates (verified)
The names invite the suspicion; the code refutes it.
- `business_rules.py` = the **rule engine**: hardcoded/default plausibility checks
  (`get_default_rules`, `validate_ranges`, `validate_rates`, `validate_yoy_change`…).
- `business_validation.py` = the **data loader/bridge** (192 lines): `load_metric_rules`,
  `load_guardrail_pairs`, `validate_against_knowledge` — reads org-specific rules out of
  `.knowledge/` YAML and applies them. It is the thin glue between the knowledge layer
  (§1d organizations/datasets) and the rule engine.
**Recommendation:** KEEP SEPARATE. Engine vs knowledge-bridge is a clean split.
**Risk of merging:** would couple the rule logic to filesystem/YAML I/O and hurt
testability. Don't merge. **Effort:** N/A.

### 3b. `metric_validator.py` vs the rest — NOT a duplicate (verified)
It validates metric *definition files* (YAML well-formedness) + a single computed value
against its spec. The Layer-1–3 validators validate *analysis result dataframes*.
Different inputs, different job. Its only non-test consumer is `north_star/nsm_checklist.py`.
**Recommendation:** KEEP SEPARATE. **Effort:** N/A.

### 3c. `semantic-validation` skill vs the Validation agent — REAL prose duplication
**What overlaps:** `.claude/skills/semantic-validation/skill.md` says it "orchestrates
the full 4-layer validation stack plus confidence scoring," then re-describes Layer 1
(schema/PK), Layer 2 (aggregation/trend/segment/temporal), Layer 3 (ranges/rates/YoY),
Simpson's, and the A–F confidence grade — in its own prose, with point allocations
(0–15 per layer). The Validation agent (`agents/validation.md`) describes the **same**
4-layer stack and confidence badge as its core workflow, and the skill's own text says
it "applies automatically as part of the Validation agent workflow." So the same stack
is specified in two long prose documents that can drift out of sync.

**Evidence:** semantic-validation/skill.md (Purpose + Layer 1–4 sections, scoring
0–15/layer) vs agents/validation.md (4-layer workflow + confidence badge; depends_on
cross-verification). Both ultimately call the same five helpers.

**Recommendation:** CONSOLIDATE the prose (not the helpers — the helpers are fine). Make
one the single source of truth for the 4-layer procedure and have the other reference it.
Cleanest: keep the **Validation agent** as the canonical procedure and slim
`semantic-validation/skill.md` down to a trigger + a pointer ("run the Validation agent's
Step 5a–5e stack"), or vice-versa. Today they duplicate ~the same 60+ lines of layer
descriptions.
**Risk:** Low — both are prompt docs, no code imports them. The risk being *removed* here
is silent drift (one doc updated, the other stale → inconsistent grading instructions).
**Effort:** S–M (careful prose merge; make sure no unique check described in only one of
them is lost — I did not exhaustively diff every check line-by-line, so verify before cutting).

### 3d. Note on `cross_verification.py` ↔ `tieout_helpers.py`
Already covered in §2: cross-verification is the live replacement; tieout is the dead shim
pointing at it. No action beyond §2.

---

## 4. Other redundancy noticed

- **`reliability/` knowledge dirs (8 runs + log.jsonl):** not a dedup issue but flagged
  in v3-merge-plan as class-test output to gitignore. Mention here for completeness.
- **README documents subsystems that don't exist on disk** (`learnings/`, `user/`,
  `global/`): correct by design (gitignored content), but a fresh-clone reader sees a map
  richer than the tree. Optional: add "(created on first use)" markers. Cosmetic, S.
- No duplicate helpers doing the same job were found beyond the validator/tieout items
  above. `business_context.py` (org loader) and `business_validation.py` (rule loader)
  read the same `.knowledge/organizations/` tree but for different payloads (business
  glossary vs metric/guardrail rules) — not redundant.

---

## Prioritized recommendations (highest-confidence, lowest-risk first)

| # | Candidate | Action | Confidence | Risk | Effort |
|---|-----------|--------|-----------|------|--------|
| 1 | `helpers/tieout_helpers.py` deprecated shim | Re-point the 1 skill-doc import + 2 infra refs, confirm `read_source_direct`/`profile_dataframe` unused (or re-home), then delete | High | Low | S |
| 2 | `semantic-validation` skill vs Validation agent prose | Consolidate to one source of truth for the 4-layer procedure; other points to it | High | Low | S–M |
| 3 | `feedback-capture` writing to both `corrections/` + `learnings/` | Tighten routing so each signal lands in exactly one store + cross-link | Medium | Low | S |
| 4 | README documents `learnings/`/`user/`/`global/` not on disk | Add "(created on first use)" markers | Medium | Low | S (cosmetic) |
| 5 | `corrections/` vs `query-archaeology/` | KEEP SEPARATE; optional one-line cross-ref note only | High (verdict) | n/a | S (note) |
| 6 | `business_rules.py` vs `business_validation.py` | KEEP SEPARATE (engine vs knowledge-bridge) | High (verdict) | n/a | — |
| 7 | `metric_validator.py` vs Layer-1–3 validators | KEEP SEPARATE (validates definitions, not result frames) | High (verdict) | n/a | — |
| 8 | `analyses/`/`references/`/`organizations/`/`reliability/`/`datasets/` | KEEP ALL (distinct purposes) | High (verdict) | n/a | — |

**Honest uncertainties:** (a) For item 1 I confirmed grep-clean importers for the two
"still useful" tieout utilities but did not run the test suite — verify before deleting.
(b) For item 2 I did not line-by-line diff every individual check in the skill vs the
agent, so confirm no unique check exists in only one before cutting. (c) `learnings/`,
`user/`, `global/`, and the populated `corrections/log.yaml` are gitignored and absent on
disk, so §1c's overlap is assessed from the skill prose, not from live data.
