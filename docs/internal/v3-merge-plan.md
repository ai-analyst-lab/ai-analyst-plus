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

## Phase A — Strip course / build scaffolding

### A1. Internal build docs (delete or move to `docs/internal/`)
- [ ] `BUILD_STATUS.yaml` (41 KB) · `WEEK4_COVERAGE_MAP.md` (46 KB) · `GDOC_EXPORT_MASTER_PLAN.md` (29 KB) · `HISTORY.md` · `CHANGELOG.md` (NovaMart-specific → replace with clean product changelog)

### A2. Community / class skills — DECIDED
- **KEEP:** `kickoff`, `show-off`
- [ ] **CUT:** `show-off-linkedin`, `certificate`, `demo` (+ `agents/demo-breakout.md`), `first-run-welcome`
- [ ] Deregister each from `CLAUDE.md`, `agents/INDEX.md`, `agents/registry.yaml`
- Keepers confirmed: `setup`, `connect-data`, `architect`

### A3. Already removed ✅
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

### B3. Remaining — config & template
- [ ] `data_sources.yaml` — currently registers `novamart`. **Plan:** gitignore it + ship `data_sources.example.yaml` (mirror the `active.yaml` pattern). Do NOT wipe in place — Shane's local demo reads it.
- [ ] **Build a generic dataset-brain template** `.knowledge/datasets/_template/` (placeholder `schema.md`, `quirks.md`, `manifest.yaml`, `metrics/index.yaml`) so `/connect-data` scaffolds from it. `_metric_schema.yaml` already exists as the metric template.

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

### B6. Theme
- [ ] Fix `themes/brands/economist/` WCAG failures + rewrite copy-paste README, or drop it

---

## Phase C — Open-source hardening & secret scan  *(moved up per Shane)*

- ✅ `.env` gitignored & untracked; no secret files tracked; `.gitleaks.toml` + pre-commit present
- [ ] Run `gitleaks` over **full history** (bot era) — guarantee no secrets anywhere in history
- [ ] Audit `data_sources.yaml`, `snowflake-mcp-config.yaml`, `connection_templates/` — placeholders only, no real creds
- [ ] README / LICENSE pass; `pyproject.toml` metadata; CI green on a clean clone

---

## Phase D — De-duplicate knowledge & validation  *(REPORT ONLY — do not execute)*

> Per Shane: **write a report on dedupe, do not change anything, do not merge without me.**

- [ ] Report: overlapping knowledge subsystems — `corrections/` vs `query-archaeology/` (purpose overlap), plus `analyses/`, `references/`, `organizations/`, `reliability/`, `datasets/`
- [ ] Report: deprecated shim `helpers/tieout_helpers.py` (→ `cross_verification.py`)
- [ ] Report: validation stack overlap (4 validators + confidence_scoring + business_rules + semantic-validation)
- [ ] Deliver as `docs/internal/dedupe-report.md`; Shane reviews before any change

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
