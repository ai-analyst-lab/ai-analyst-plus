"""Local E2E smoke tests for pipeline/resume/export Codex skills."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import pytest
import yaml

from helpers.skill_runtime.export_skill import export_data_package, export_text_format
from helpers.skill_runtime.pipeline_skills import dry_run_plan, resume_plan, validate_registry


@pytest.mark.e2e
def test_export_local_formats_and_data_package(tmp_path: Path):
    root = tmp_path
    (root / "outputs").mkdir()
    (root / "working").mkdir()
    (root / "outputs" / "narrative_2026-01-01.md").write_text(
        "# Analysis\n\nConversion fell 5% in March. Recommendation: fix checkout errors.\n"
    )
    pd.DataFrame({"segment": ["mobile", "desktop"], "conversion": [0.10, 0.15]}).to_csv(
        root / "working" / "conversion_by_segment.csv", index=False
    )

    email = export_text_format(root, "email", today="2026-01-02")
    slack = export_text_format(root, "slack", today="2026-01-02")
    brief = export_text_format(root, "brief", today="2026-01-02")
    readme = export_data_package(root)

    assert email.name == "email_summary_2026-01-02.md"
    assert slack.name == "slack_update_2026-01-02.md"
    assert brief.name == "decision_brief_2026-01-02.md"
    assert "Conversion fell 5%" in email.read_text()
    assert "conversion_by_segment.csv" in readme.read_text()


@pytest.mark.e2e
def test_pipeline_dry_run_validates_real_registry():
    validation = validate_registry("agents/registry.yaml")
    assert validation["ok"] is True, validation["errors"]
    assert validation["agent_count"] > 10
    assert any("question-framing" in tier for tier in validation["tiers"])

    plan = dry_run_plan("agents/registry.yaml")
    assert "Execution Plan (dry-run):" in plan
    assert "Tier 0" in plan
    assert "question-framing" in plan


@pytest.mark.e2e
def test_resume_pipeline_computes_ready_set_from_fixture_state(tmp_path: Path):
    root = tmp_path
    agents_dir = root / "agents"
    agents_dir.mkdir()
    for name in ["a", "b", "c"]:
        (agents_dir / f"{name}.md").write_text(f"# {name}\n")
    (agents_dir / "registry.yaml").write_text(yaml.safe_dump({
        "version": 1,
        "agents": [
            {"name": "a", "file": "agents/a.md", "pipeline_step": 1, "depends_on": []},
            {"name": "b", "file": "agents/b.md", "pipeline_step": 2, "depends_on": ["a"]},
            {"name": "c", "file": "agents/c.md", "pipeline_step": 3, "depends_on": ["b"]},
        ],
    }))
    latest = root / "working" / "latest"
    latest.mkdir(parents=True)
    (latest / "pipeline_state.json").write_text(json.dumps({
        "schema_version": 2,
        "run_id": "demo-run",
        "dataset": "demo",
        "question": "Why did conversion drop?",
        "status": "paused",
        "agents": {
            "a": {"status": "completed", "output_file": "outputs/a.md"},
            "b": {"status": "running"},
            "c": {"status": "pending"},
        },
    }))

    plan = resume_plan(root)
    assert plan["ok"] is True
    assert plan["completed"] == ["a"]
    assert plan["ready"] == ["b"]
