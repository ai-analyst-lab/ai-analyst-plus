#!/usr/bin/env python3
"""Deterministic audit logging for blind review verdicts.

Supports Codex-native review workflows that write a ``verdict.json`` with a
``findings`` list containing per-finding verdicts. The helper counts verdicts
from JSON, creates the audit directory when needed, appends one JSONL entry,
and returns the entry for display/tests.

Usage:
    python3 helpers/review_logging.py <run_dir> independent-review
    python3 helpers/review_logging.py <run_dir> claude-review
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

VALID_REVIEWERS = {
    "independent-review": Path(".knowledge/independent-review/log.jsonl"),
    "claude-review": Path(".knowledge/claude-review/log.jsonl"),
}
VALID_VERDICTS = ("AGREE", "PARTIAL", "DISAGREE")


class ReviewLoggingError(ValueError):
    """Raised when a review verdict cannot be logged safely."""


def load_verdict(run_dir: str | Path) -> dict[str, Any]:
    """Load and validate ``verdict.json`` from a review run directory."""
    run_path = Path(run_dir)
    verdict_path = run_path / "verdict.json"
    if not verdict_path.exists():
        raise ReviewLoggingError(f"Missing verdict.json: {verdict_path}")

    try:
        payload = json.loads(verdict_path.read_text())
    except json.JSONDecodeError as exc:
        raise ReviewLoggingError(f"Malformed verdict.json: {exc}") from exc

    if not isinstance(payload, dict):
        raise ReviewLoggingError("verdict.json must contain a JSON object")
    findings = payload.get("findings")
    if findings is None:
        payload["findings"] = []
    elif not isinstance(findings, list):
        raise ReviewLoggingError("verdict.json field 'findings' must be a list")
    return payload


def count_verdicts(findings: list[dict[str, Any]]) -> dict[str, int]:
    """Count AGREE/PARTIAL/DISAGREE/UNKNOWN verdicts deterministically."""
    counts = {"AGREE": 0, "PARTIAL": 0, "DISAGREE": 0, "UNKNOWN": 0}
    for finding in findings:
        verdict = ""
        if isinstance(finding, dict):
            verdict = str(finding.get("verdict", "")).strip().upper()
        counts[verdict if verdict in VALID_VERDICTS else "UNKNOWN"] += 1
    return counts


def build_audit_entry(
    payload: dict[str, Any],
    run_dir: str | Path,
    reviewer: str,
    *,
    timestamp: str | None = None,
) -> dict[str, Any]:
    """Build the stable JSONL audit entry for a review verdict."""
    if reviewer not in VALID_REVIEWERS:
        raise ReviewLoggingError(
            f"Unknown reviewer {reviewer!r}; expected one of {sorted(VALID_REVIEWERS)}"
        )

    findings = payload.get("findings", [])
    if not isinstance(findings, list):
        raise ReviewLoggingError("verdict.json field 'findings' must be a list")

    counts = count_verdicts(findings)
    return {
        "ts": timestamp or datetime.now(timezone.utc).isoformat(),
        "question": payload.get("question", "(unknown)"),
        "reviewer": payload.get("reviewer", reviewer),
        "n_findings": len(findings),
        "agree": counts["AGREE"],
        "partial": counts["PARTIAL"],
        "disagree": counts["DISAGREE"],
        "unknown": counts["UNKNOWN"],
        "dir": str(Path(run_dir)),
    }


def append_audit_entry(
    run_dir: str | Path,
    reviewer: str,
    *,
    log_path: str | Path | None = None,
    timestamp: str | None = None,
) -> dict[str, Any]:
    """Append one audit JSONL row for ``run_dir`` and return the entry."""
    payload = load_verdict(run_dir)
    entry = build_audit_entry(payload, run_dir, reviewer, timestamp=timestamp)
    target = Path(log_path) if log_path is not None else VALID_REVIEWERS[reviewer]
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("a") as fh:
        fh.write(json.dumps(entry, sort_keys=True) + "\n")
    return entry


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_dir", help="Review run directory containing verdict.json")
    parser.add_argument("reviewer", choices=sorted(VALID_REVIEWERS))
    parser.add_argument("--log-path", help="Override audit log path, mainly for tests")
    args = parser.parse_args()

    try:
        entry = append_audit_entry(args.run_dir, args.reviewer, log_path=args.log_path)
    except ReviewLoggingError as exc:
        parser.error(str(exc))
    print(json.dumps(entry, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
