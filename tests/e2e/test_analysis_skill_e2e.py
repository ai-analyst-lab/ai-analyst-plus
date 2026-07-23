"""Local E2E smoke tests for analysis/review-oriented Codex skills."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from helpers.reliability_stats import compute as compute_reliability
from helpers.review_logging import append_audit_entry


@pytest.mark.e2e
def test_reliability_and_review_logging_local_e2e(tmp_path: Path):
    runs = [
        {"run": 1, "headline": "25.0%", "measured": "25 / 100", "definition_source": "metric dictionary"},
        {"run": 2, "headline": "25.0%", "measured": "25 / 100", "definition_source": "metric dictionary"},
        {"run": 3, "headline": "25.0%", "measured": "25 / 100", "definition_source": "metric dictionary"},
    ]
    stats = compute_reliability(runs)
    assert stats["verdict"] == "STABLE"
    assert stats["agreement_rate"] == 1.0

    run_dir = tmp_path / "review"
    run_dir.mkdir()
    (run_dir / "verdict.json").write_text(json.dumps({
        "question": "Is retention stable?",
        "reviewer": "independent-review",
        "findings": [{"name": "retention", "verdict": "AGREE"}],
    }))
    log_path = tmp_path / ".knowledge" / "independent-review" / "log.jsonl"
    entry = append_audit_entry(run_dir, "independent-review", log_path=log_path, timestamp="2026-01-01T00:00:00+00:00")
    assert entry["agree"] == 1
    assert log_path.exists()


@pytest.mark.e2e
def test_experiment_helper_backed_smoke():
    pytest.importorskip("scipy")
    pytest.importorskip("statsmodels")
    from helpers.experiment_stats import (
        adjust_pvalues,
        duration_estimate,
        power_proportion,
        proportion_test,
        srm_check,
    )

    srm = srm_check([500, 500], [0.5, 0.5], threshold=0.0005)
    assert srm["verdict"] == "PASS"

    result = proportion_test(c_success=100, c_n=1000, t_success=130, t_n=1000)
    assert result["rate_treatment"] > result["rate_control"]
    assert "p_value" in result

    power = power_proportion(0.10, 0.10)
    assert power["total_sample_size"] > 0
    duration = duration_estimate(power["total_sample_size"], daily_traffic=10_000, allocation=0.5)
    assert duration["days"] > 0

    correction = adjust_pvalues([result["p_value"], 0.20], method="holm")
    assert correction["n_tests"] == 2
