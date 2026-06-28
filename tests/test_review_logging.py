"""Tests for deterministic blind review audit logging."""

import json
from pathlib import Path

import pytest

from helpers.review_logging import (
    ReviewLoggingError,
    append_audit_entry,
    count_verdicts,
    load_verdict,
)


def test_count_verdicts_includes_unknown():
    findings = [
        {"verdict": "AGREE"},
        {"verdict": "partial"},
        {"verdict": "DISAGREE"},
        {"verdict": "not-a-verdict"},
        {},
    ]
    assert count_verdicts(findings) == {
        "AGREE": 1,
        "PARTIAL": 1,
        "DISAGREE": 1,
        "UNKNOWN": 2,
    }


def test_append_audit_entry_creates_log_dir_and_counts(tmp_path):
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    (run_dir / "verdict.json").write_text(json.dumps({
        "question": "What changed?",
        "reviewer": "independent-review",
        "findings": [
            {"name": "a", "verdict": "AGREE"},
            {"name": "b", "verdict": "DISAGREE"},
        ],
    }))
    log_path = tmp_path / "nested" / "log.jsonl"

    entry = append_audit_entry(
        run_dir,
        "independent-review",
        log_path=log_path,
        timestamp="2026-01-01T00:00:00+00:00",
    )

    assert entry == {
        "ts": "2026-01-01T00:00:00+00:00",
        "question": "What changed?",
        "reviewer": "independent-review",
        "n_findings": 2,
        "agree": 1,
        "partial": 0,
        "disagree": 1,
        "unknown": 0,
        "dir": str(run_dir),
    }
    rows = [json.loads(line) for line in log_path.read_text().splitlines()]
    assert rows == [entry]


def test_load_verdict_rejects_malformed_json(tmp_path):
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    (run_dir / "verdict.json").write_text("{")

    with pytest.raises(ReviewLoggingError, match="Malformed verdict.json"):
        load_verdict(run_dir)


def test_load_verdict_requires_findings_list(tmp_path):
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    (run_dir / "verdict.json").write_text(json.dumps({"findings": {}}))

    with pytest.raises(ReviewLoggingError, match="findings"):
        load_verdict(run_dir)
