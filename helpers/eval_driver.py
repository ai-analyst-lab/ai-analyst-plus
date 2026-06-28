"""Live eval driver plumbing (D4).

The /eval SKILL is the agentic part: it runs the analyst once per gold question (fresh context,
gold blind) and captures each answer + SQL + latency. This module is the deterministic part that
does not need the model: the Snowflake preflight (D3, fail loud — no DuckDB fallback), the run
provenance (git sha, which metrics are currently defined), and the grading call into the eval
harness in the sibling ai-analytics-evals repo.

Blind-by-construction: the analyst sub-agents are handed questions only (see aievals.data.gold.
load_questions). The gold answers are read ONLY here, in grade(), after the analyst's answers are
already locked — so the runs never saw the key.
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

# The eval harness + blind gold live in the sibling repo (public, gold in-repo for teaching, D1).
EVALS_REPO = Path(os.environ.get("AIEVALS_REPO", Path.home() / "projects" / "ai-analytics-evals"))
GOLD_PATH = EVALS_REPO / "aievals" / "data" / "novamart_gold.yaml"
CANDIDATES_PATH = EVALS_REPO / "aievals" / "data" / "novamart_gold_candidates.yaml"
REPO_ROOT = Path(__file__).resolve().parents[1]


def git_sha(repo: str | Path | None = None) -> str | None:
    """Short HEAD sha of a repo, for the run record. None if not a git repo."""
    repo = Path(repo) if repo else REPO_ROOT
    try:
        return subprocess.check_output(
            ["git", "-C", str(repo), "rev-parse", "--short", "HEAD"], text=True
        ).strip()
    except Exception:
        return None


def _active_dataset(project_root: str | Path = REPO_ROOT) -> str:
    """The active dataset id, for resolving the context dir. Defaults to novamart."""
    import yaml

    p = Path(project_root) / ".knowledge" / "active.yaml"
    if p.exists():
        data = yaml.safe_load(p.read_text()) or {}
        return data.get("dataset") or data.get("active") or "novamart"
    return "novamart"


def context_state(metrics_path: str | Path | None = None,
                  project_root: str | Path = REPO_ROOT) -> dict:
    """The run's context fingerprint: which metrics are DEFINED in the analyst's dictionary.

    This is what makes the climb legible — the list grows run over run as students add definitions
    (C0-C2), and the eval score climbs with it. Resolves the same context dir the analyst reads from
    (local under source: local, the communal cache under source: git). Best-effort: never crashes a
    run over a missing dictionary."""
    import yaml

    try:
        if metrics_path is None:
            from helpers.context_sync import resolve_context_dir

            ctx_dir, _src = resolve_context_dir(_active_dataset(project_root), project_root)
            metrics_path = Path(ctx_dir) / "metrics" / "index.yaml"
        metrics_path = Path(metrics_path)
        if not metrics_path.exists():
            return {"defined_metrics": [], "n": 0}
        data = yaml.safe_load(metrics_path.read_text()) or {}
        names = [m.get("metric") or m.get("name")
                 for m in (data.get("metrics") or []) if isinstance(m, dict)]
        names = sorted(n for n in names if n)
        return {"defined_metrics": names, "n": len(names)}
    except Exception as e:  # pragma: no cover - defensive
        return {"defined_metrics": [], "n": 0, "error": str(e)}


def get_snowflake_conn():
    """Open the analyst's Snowflake connection and return the raw DBAPI connection.

    D3: Snowflake only, fail loud. If the manager connects to anything other than Snowflake
    (e.g. a local DuckDB fallback), raise instead of silently grading against the wrong engine."""
    from helpers.connection_manager import ConnectionManager

    cm = ConnectionManager()
    cm.connect()
    if cm.connection_type != "snowflake":
        raise RuntimeError(
            f"eval: active connection is '{cm.connection_type}', not Snowflake. D3 requires Snowflake "
            "with no DuckDB fallback — connect the active dataset to Snowflake first (/setup-snowflake "
            "or /connect-data; the dataset manifest's type must be 'snowflake')."
        )
    return cm._connection


def preflight(conn=None):
    """D3 fail-loud gate: a live Snowflake connection that answers a trivial probe. Raises a clear
    RuntimeError rather than degrading to local data. Returns the usable connection."""
    conn = conn or get_snowflake_conn()
    try:
        cur = conn.cursor()
        cur.execute("select 1")
        cur.fetchone()
    except Exception as e:
        raise RuntimeError(
            f"eval preflight: Snowflake probe failed ({e}). Fix the connection; there is no local "
            "fallback (D3)."
        ) from e
    return conn


def grade(per_case_results, split, out_dir, conn, gold_path=GOLD_PATH,
          model=None, extra_meta=None):
    """Grade the locked per-case answers against the BLIND gold and write the full run record.

    Imports the harness from the sibling evals repo. The gold is read only at this point, after the
    analyst answers are fixed, so the runs stayed blind. The run record carries git_sha + model +
    context_state (D4) so it is self-describing and the monitor can read it directly (BL-C1)."""
    if str(EVALS_REPO) not in sys.path:
        sys.path.insert(0, str(EVALS_REPO))
    from aievals.run_eval import run_eval

    meta = {"git_sha": git_sha(), "model": model, "context_state": context_state()}
    if extra_meta:
        meta.update(extra_meta)
    return run_eval(str(gold_path), per_case_results, conn, out_dir=str(out_dir),
                    split=split, meta=meta)


def verify_candidates(cases_path=CANDIDATES_PATH, split=None):
    """Run every candidate gold sql against Snowflake and print which return a real number.

    Use before merging candidates into the trusted suite (gold discipline: the sql must run and be
    signed off). Preflights Snowflake (D3, fail loud), then recomputes each candidate's sql and
    reports the value or the error. Returns the results list."""
    if str(EVALS_REPO) not in sys.path:
        sys.path.insert(0, str(EVALS_REPO))
    from aievals.verify_gold import verify_cases, format_report

    conn = preflight()
    results = verify_cases(str(cases_path), conn, split=split)
    print(format_report(results))
    return results
