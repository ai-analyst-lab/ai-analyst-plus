# Hardening Report — Open-Source Readiness + Secret-Leak Audit

**Repo:** `/Users/shanebutler/projects/ai-analyst-plus`
**Phase:** C (cleanup) · **Scope:** read-only audit · **Date:** 2026-06-17
**Branch audited:** `feat/north-star-merge` · history scanned across **all** refs (64 commits)

---

## (a) Secret-Scan Verdict

### VERDICT: **GO** (with one local-machine caveat, not a git leak)

No real secrets are committed in the working tree **or** in git history, including the
removed `groww-bot/` options-trading bot. The bot was deleted in `6b9d6a5` ("chore: remove
groww-bot, PM dev-team, and class test agents") and added in `9679e6d`. Its 6 historical
files (`vr20_bot.py`, `vr20_journal.py`, `multi_runner.py`, 3 config JSONs) were inspected
directly from history — **all credential access is by reference, not by value.**

**Evidence (redacted):**

| Check | Result |
|-------|--------|
| `gitleaks` history scan | **Tool unavailable** — manual scan performed instead (see section d) |
| `git log -p --all` for `AKIA…`, `BEGIN…PRIVATE KEY`, `xox[bp]-`, `ghp_`, `github_pat_`, `sk-ant-`, `sk-…` | **0 hardcoded hits** |
| `GROWW_ACCESS_TOKEN` / `TELEGRAM_TOKEN` in history | Found only as `_base_env.get('TELEGRAM_TOKEN', '')` and `user.get('access_token','')` — **env-var / runtime reads, never literals** (`groww-bot/multi_runner.py:32,50`) |
| Bot credential files (`users.json`, `.env`, `vr20_sa_credentials.json`) | **Never committed.** Referenced by path `BASE = /home/ubuntu/groww-bot` (`multi_runner.py:15-17`, `vr20_journal.py:27`). `git log --all --diff-filter=A` for `groww-bot/` shows only the 6 code/config files. |
| `vr20_config_{nifty,banknifty,finnifty}.json` | Trading parameters only (R:R gates, OR buckets) — **no secrets** |
| Google Sheets logger (`vr20_journal.py`) | Loads `Credentials.from_service_account_file(...)` from an un-committed JSON; **no spreadsheet IDs or keys embedded** |
| `password=` / `client_secret=` in history | Only template placeholders: `password: "{password}"  # Consider using env vars` |
| `.env` tracked? | **No** — `git ls-files .env` empty; ignored via `.gitignore:8` |
| `.env` ever in history (any path)? | **No** — `git log --all -- .env */.env` empty |
| Tracked files matching `env\|cred\|secret\|token` | Only 2 false positives: `north-star/wiki/SCHEMAS/ConfidenceEnvelope.yaml`, `…/key-value-exchanges.md` (concept docs, no secrets) |

**Local-machine caveat (NOT a git leak, but flag before any `git add -A`):**
The working-tree `.env` (untracked, gitignored) contains a **real Snowflake credential set** —
`SNOWFLAKE_ACCOUNT`, `SNOWFLAKE_USER`, `SNOWFLAKE_PASSWORD`, etc. Values were **not printed**.
It is correctly excluded from git, so it will not ship. Risk is only if someone force-adds it
or the publish process copies untracked files. Recommend confirming the publish tarball is built
from `git archive`, not a directory copy.

---

## (b) Config Audit

| File | Tracked? | Real creds vs placeholder | Verdict |
|------|----------|---------------------------|---------|
| `data_sources.yaml` | **Yes** | NovaMart DuckDB path only; no host/account/token | Clean (but see OSS note re: NovaMart) |
| `snowflake-mcp-config.yaml` | **Yes** | Service toggles + SQL permission flags only; comment says "Auth is handled via `.env`" | Clean |
| `.mcp.json` | Not present | — (gitignored per `.gitignore`) | N/A |
| `connection_templates/snowflake.yaml.example` | Yes | `account: "{account_identifier}"`, `password: "{password}"` | Clean — placeholders |
| `connection_templates/postgres.yaml.example` | Yes | `{placeholder}` syntax | Clean |
| `connection_templates/bigquery.yaml.example` | Yes | `{placeholder}` syntax | Clean |
| `connection_templates/duckdb.yaml.example` | Yes | `{placeholder}` syntax | Clean |
| `.claude/settings.local.json.example` | Yes | Example only | Clean |
| `.knowledge/active.yaml` | Yes | `active_dataset: novamart` (pointer only) | Clean — but points at a dataset whose data is gitignored (see OSS) |
| `.env` | **No** (gitignored) | **Real Snowflake password/account** | Not shipped; local risk only |

`.gitignore` correctly covers: `.env`, `.env.*`, `credentials.json`, `client_secret*.json`,
`service_account*.json`, `*.credential`, `*.token`, `.mcp.json`, `snowflake-mcp-config.yaml`
(user copy), `connection_templates/` live copies, and `data/practice/*.csv`.

---

## (c) OSS Readiness Checklist

| Item | Status | Fix |
|------|--------|-----|
| **LICENSE** | OK — MIT, `Copyright (c) 2026 Shane Butler` | None |
| **pyproject.toml** | OK — `name = "ai-analyst"`, `version = "1.0.0"`, `license = {text="MIT"}`, `requires-python >=3.10`, author Shane Butler. Already renamed off "plus". | None for packaging |
| **README.md** | **Stale naming.** Title `# AI Analyst Plus` (line 1), body line 14, clone URL `ai-analyst-lab/ai-analyst-plus.git` (line 30-31), tree label line 229. No NovaMart / bootcamp / class / data-gen references remain (clean). | Rename "AI Analyst Plus" → "AI Analyst"; update clone URL to the v3 repo. (Repo is mid-rename — flagged, not fixed.) |
| **NovaMart default dataset** | **Broken on clean clone.** `data_sources.yaml` + `.knowledge/active.yaml` point at `novamart` / `data/practice/novamart_practice.duckdb`, but `data/practice/*.csv` (incl. 577 MB `events.csv`) is **gitignored and untracked**. A fresh clone has no active dataset data. Per `docs/internal/v3-merge-plan.md` (Phase B) NovaMart is intentionally not shipped. | Ship a generic template brain or unset the active pointer so first-run onboarding handles it. Align with v3-merge-plan Phase B. |
| **CI — `.github/workflows/ci.yml`** | OK — matrix py3.10/3.11/3.12, `pip install -e ".[dev]"` fallback, `pytest tests/ -v`. | None |
| **Tests on clean clone** | OK — 40 test files, self-contained. Integration/Snowflake tests are marker-gated (`pytestmark = pytest.mark.integration`). The lone `novamart` reference in `tests/test_data_helpers_v2.py:100` is an **anti-regression guard** (`assert "novamart" not in md`), not a data dependency. No network/data fixtures required for the default run. | None |
| **Stale "plus"/"+" naming** | Present in README (above) and dir name `ai-analyst-plus`. pyproject already on `ai-analyst`. | Part of the in-progress rename — flagged only. |

---

## (d) Tools Used / Limitations

- **`gitleaks`: NOT INSTALLED** (`which gitleaks` → not found). Could not run the requested
  `gitleaks detect --redact -v` or `--log-opts=--all`. A repo `.gitleaks.toml` exists and was
  read (allowlists `*.example`, placeholder strings; one rule for `connection_templates/*.yaml`
  credential patterns). **Recommendation:** install gitleaks and run it in CI as a pre-publish
  gate to make this verdict reproducible.
- **Manual scan performed instead:** `git log -p --all` piped through `grep -E` for high-signal
  patterns (AWS keys, PEM private keys, Slack `xox*`, GitHub `ghp_`/`github_pat_`, OpenAI/Anthropic
  `sk-*`, `GROWW_ACCESS_TOKEN`, `TELEGRAM_TOKEN`, `password=`, `client_secret=`), with env-var
  reads / placeholders filtered out. Historical bot files inspected individually via `git show`.
- **Coverage:** all 64 commits across all local refs. Remote-only branches
  (`origin/claude/investigate-ticket-spike-VewGX`) were not fetched/scanned — assumed subset of
  scanned history; fetch + re-scan before publish if uncertain.
- **No writes** beyond this report. No `git` write commands run.
- Secret **values never printed** anywhere in this report.
