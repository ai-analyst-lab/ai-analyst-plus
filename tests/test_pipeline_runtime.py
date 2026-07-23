"""Tests for deterministic pipeline runtime helpers."""

from __future__ import annotations

import json
from pathlib import Path

import yaml

from helpers.pipeline_runtime import compute_ready_agents, compute_tiers, dry_run_plan, resume_plan, validate_registry


def test_compute_ready_agents_respects_depends_on_any():
    registry = {
        "root": {"pipeline_step": 1, "depends_on": []},
        "a": {"pipeline_step": 2, "depends_on": ["root"]},
        "b": {"pipeline_step": 2, "depends_on": ["root"]},
        "join": {"pipeline_step": 3, "depends_on": ["root"], "depends_on_any": ["a", "b"]},
    }
    state = {"agents": {"root": {"status": "completed"}, "a": {"status": "completed"}}}
    assert compute_ready_agents(state, registry) == ["b", "join"]


def test_compute_tiers_detects_ordering():
    registry = {
        "a": {"pipeline_step": 1, "depends_on": []},
        "b": {"pipeline_step": 2, "depends_on": ["a"]},
        "c": {"pipeline_step": 3, "depends_on": ["b"]},
        "standalone": {"pipeline_step": None, "depends_on": []},
    }
    assert compute_tiers(registry) == [["a"], ["b"], ["c"]]


def test_validate_registry_and_dry_run_on_fixture(tmp_path: Path):
    agents = tmp_path / "agents"
    agents.mkdir()
    (agents / "a.md").write_text("# A")
    (agents / "b.md").write_text("# B")
    registry = agents / "registry.yaml"
    registry.write_text(yaml.safe_dump({
        "agents": [
            {"name": "a", "file": "agents/a.md", "pipeline_step": 1, "depends_on": []},
            {"name": "b", "file": "agents/b.md", "pipeline_step": 2, "depends_on": ["a"]},
        ]
    }))
    result = validate_registry(registry, root=tmp_path)
    assert result["ok"] is True
    assert "Tier 0" in dry_run_plan(registry, root=tmp_path)


def test_resume_plan_loads_latest_state(tmp_path: Path):
    agents = tmp_path / "agents"
    agents.mkdir()
    (agents / "a.md").write_text("# A")
    (agents / "b.md").write_text("# B")
    (agents / "registry.yaml").write_text(yaml.safe_dump({
        "agents": [
            {"name": "a", "file": "agents/a.md", "pipeline_step": 1, "depends_on": []},
            {"name": "b", "file": "agents/b.md", "pipeline_step": 2, "depends_on": ["a"]},
        ]
    }))
    latest = tmp_path / "working" / "latest"
    latest.mkdir(parents=True)
    (latest / "pipeline_state.json").write_text(json.dumps({
        "schema_version": 2,
        "run_id": "run",
        "dataset": "demo",
        "question": "Q",
        "agents": {"a": {"status": "completed"}, "b": {"status": "pending"}},
    }))
    plan = resume_plan(tmp_path)
    assert plan["ready"] == ["b"]
    assert plan["completed"] == ["a"]
