# AI Analyst v3 — Cleanup & Open-Source Merge Plan

**Goal:** Clean this repo (currently "AI Analyst+") into a generalizable, plug-and-play,
open-sourceable state and merge it into the existing **AI Analyst** repo as **v3** —
retiring the separate "+" product.

**Owner:** Shane · **Status:** in progress · **Last updated:** 2026-06-17

**Done-when:** clone → `/connect-data` (or Snowflake connect) → fully working with zero
NovaMart traces; no course/build scaffolding; no redundant subsystems; history clean of
the bot era; no secrets.

**NovaMart model (decided):** NovaMart is *not* shipped. Its dataset brain + bulk data are
**already gitignored** and live only in Shane's local working copy. Users connect their own
warehouse (e.g. Snowflake) and the brain is (re)generated locally on connect. The repo
ships a generic **template** for the brain, never the NovaMart instance.

Surface area today: **69 skills · 44 agents · 47 helpers · 35 tests.**

---

## Part 1 — Immediate commits (split the current working tree)

> Not yet run — awaiting "go".

### Commit 1 — `chore: remove groww-bot, VR20 bot, PM dev-team, and class test skills`
- [ ] Staged deletions: `groww-bot/` (6), `agents/pm-*.md` (7), `.claude/skills/build-data-product/`, `docs/superpowers/specs/2026-05-16-vr20-strategy-design.md`
- [ ] `agents/registry.yaml` (−skeptical-reviewer, −PM block); `agents/INDEX.md` (−skeptical, −7 PM rows)
- [ ] `CLAUDE.md` (+Reliability row); `helpers/INDEX.md` (+reliability_stats row)
- [ ] `agents/comms-drafter.md` — hunk-stage only the 2-line skill-ref removal
- [ ] New keepers: `.claude/skills/reliability/`, `helpers/reliability_stats.py`

### Commit 2 — `wip: north-star + connection/data-helper infra`
- [ ] `agents/comms-drafter.md` (50-line WIP hunks), `agents/descriptive-analytics.md`, `helpers/connection_manager.py`, `helpers/data_helpers.py`

### Held out of both commits
- [ ] `.knowledge/reliability/` — 8 test-run dirs + `log.jsonl` (class-test output). **Action:** gitignore; don't commit.
- [ ] `themes/brands/economist/` — fails WCAG autograder. **Action:** hold until fixed.

---

## Phase A — Strip course / build scaffolding  ✅ DONE

### A1. Internal build docs — removed ✅
`BUILD_STATUS.yaml` · `WEEK4_COVERAGE_MAP.md` · `GDOC_EXPORT_MASTER_PLAN.md` · `HISTORY.md`
deleted (recoverable from history). `CHANGELOG.md` KEPT — it's a proper semver changelog,
not NovaMart-specific (its NovaMart line is a correct "removed bundled dataset" entry).

### A2. Community / class skills — removed ✅
- **KEPT:** `kickoff`, `show-off`, `setup`, `connect-data`, `architect`
- **CUT:** `show-off-linkedin`, `certificate` (+ `render-certificate.mjs` + `auto_certificate`
  config), `demo` (+ `agents/demo-breakout.md`), `first-run-welcome` (+ its cross-refs in
  knowledge-bootstrap / north-star skill + obsolete test fixture). Deregistered everywhere.

### A3. Earlier removals ✅
always-compare · color-commentary · drop-off-format · skeptical-reviewer · groww-bot · pm-* dev team · build-data-product

---

## Phase B — De-NovaMart / make plug-and-play

### B1. Already clean (gitignored, not tracked) ✅
- `.knowledge/datasets/*/` (NovaMart brain), `.knowledge/active.yaml`, `*.duckdb`, `data/practice/` — confirmed via `git ls-files`: zero NovaMart files tracked. A fresh clone already has no NovaMart brain.

### B2. Genericized this session ✅
- `.claude/skills/data-map/skill.md` — "NovaMart-style schemas" → "example e-commerce schema"; dropped the curriculum-specific Week-23 opener; theme examples generalized
- `helpers/north_star/input_tree.py` — comment de-NovaMart'd
- `tests/north_star/test_input_tree.py` — comments de-NovaMart'd (data unchanged; 7 tests pass)
- Guard already in place: `tests/test_data_helpers_v2.py::test_no_novamart_references` (keep)

### B3. Config & template — done ✅
- `data_sources.yaml` — emptied to a clean registry template (no NovaMart). No gitignore
  needed: no Python reads it, skills treat it as optional (scan `.knowledge/datasets/`
  when empty), and the dataset manifest is the source of truth — so the local NovaMart
  still resolves via its (gitignored) manifest.
- Template story already covered: `connection_templates/*.yaml.example` (4 warehouses) +
  `_metric_schema.yaml` + connect-data generating the brain. A separate `_template/` brain
  would be redundant (counter to dedup goal) — skipped.

### B4. `/north-star drivers` — DECIDED: de-hardcode, real-world default ✅ (partial)
Principle (Shane): everything defaults to real-world behavior, nothing hardcoded.
Done this session:
- `drivers.py` report label is now a `name` param (no "NovaMart" literal in md/html/title)
- `__main__.py` defaults `--name` to the **active dataset's display name** via `detect_active_source()`
- removed the "Demo defaults (NovaMart)" section + hardcoded slide numbers from `verbs/drivers.md`
- smoke-tested (renders "Acme Corp"); 73 north-star tests pass

Remaining (flagged, not yet done):
- [ ] `DEFAULT_DATA = data/practice` is still a hardcoded path. For true real-world,
  default the data dir to the **active dataset's** `data_dir` (fallback to `--data`).
- [ ] `compute()` still assumes an `orders.csv` e-commerce schema (BDEF on orders/buyers).
  Full schema-generalization is a feature task, separate from this cleanup.

### B5. Demo-data factory — DECIDED: remove ✅
- `data-generation/` removed (`git rm -r`) — recover from history later for a standalone
  **`analyst-sample-data`** repo
- `experiments/checkout_redesign/` removed; `experiments/` added to `.gitignore` (user runs, never committed)
- README + `explore/skill.md` references updated off the generator
- [ ] OPEN: remaining sample data — `data/examples/` and `data/experiments/_answers/` (12 keys).
  Pull these into the same future sample-data repo, or keep `data/examples/` as bundled demos?

### B6. Theme — done ✅
`themes/brands/economist/` darkened teal/gold/captions + distinct alert → all WCAG gates
green (`check_theme economist`); copy-paste "Acme Corp" README rewritten.

---

## Phase C — Open-source hardening & secret scan — done ✅
Full report: `docs/internal/hardening-report.md`. **Secret-scan verdict: GO** — no real
secrets in the working tree or across all 64 commits of history; groww-bot era is clean
(creds by reference only); `.env` never tracked / absent from history. Configs hold
placeholders only.
Follow-ups (for the merge/rename phase, not blockers):
- [ ] Rename stale "AI Analyst Plus" in README (title + clone URL); `pyproject` already on `ai-analyst`
- [ ] Install `gitleaks` as a CI pre-publish gate (not installed; manual scan used this round)

---

## Phase D — De-duplicate knowledge & validation — REPORT DELIVERED ✅ (do not execute)
Full report: `docs/internal/dedupe-report.md`. **Awaiting Shane's approval before any change.**

Headline: repo is *less* redundant than feared. Verified NON-overlaps (keep separate):
`corrections/` vs `query-archaeology/` (mistakes-to-avoid vs patterns-to-reuse),
`business_rules.py` (engine) vs `business_validation.py` (loader), `metric_validator.py`
(validates definitions, not dataframes).

Genuine low-risk dedup wins (PENDING APPROVAL — not executed):
1. Delete `helpers/tieout_helpers.py` shim — re-point 3 doc/util refs first. Effort S.
2. Consolidate `semantic-validation` skill vs Validation agent (duplicate prose → drift). Effort S–M.
3. `feedback-capture` double-writes to `corrections/` + `learnings/` — tighten routing. Effort S.

---

## Phase E — Merge into existing AI Analyst repo  ⛔ BLOCKED

- [ ] **NEED FROM SHANE:** path / GitHub URL of the existing AI Analyst repo
- [ ] File-by-file "carry over / already exists / conflicts" diff against target
- [ ] Merge as content (fresh history in target = clean OSS history); "+" repo retired

---

## Open decisions
1. Remaining sample data (B5) — pull `data/examples/` + `data/experiments/_answers/` into the
   future sample-data repo, or keep `data/examples/` bundled?
2. `drivers.py` deeper generalization (B4) — wire data dir to active dataset now, or defer
   the schema-generalization as a separate feature task?
3. Target repo location (E)

Resolved: NovaMart model (gitignore + regenerate-on-connect + template); commit split;
class/community skills (A2); phase order (C hardening → D dedupe-report → E merge);
`/drivers` de-hardcoded (B4); demo-data factory removed (B5).
