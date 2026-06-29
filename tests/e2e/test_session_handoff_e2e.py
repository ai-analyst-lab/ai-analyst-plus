"""E2E smoke tests for deterministic session handoff writing."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from helpers.session_handoff import create_and_write, default_state, merge_state, validate_state


@pytest.mark.e2e
def test_session_handoff_writes_required_yaml_and_redacts_secrets(tmp_path: Path):
    path = create_and_write(
        root=tmp_path,
        dataset="demo",
        task="Create Google Doc export",
        next_step="verify Google Doc formatting",
        updates={
            "resources": {
                "google_doc": {
                    "id": "doc123",
                    "title": "Demo Analysis",
                    "url": "https://docs.google.com/document/d/doc123/edit",
                    "status": "content complete",
                }
            },
            "auth": {"google_email": "analyst@example.com", "access_token": "secret-token"},
        },
    )

    assert path == tmp_path / "working" / "session_state.yaml"
    state = yaml.safe_load(path.read_text())
    assert validate_state(state) == []
    assert state["dataset"] == "demo"
    assert state["resources"]["google_doc"]["id"] == "doc123"
    assert state["auth"]["access_token"] == "<redacted>"
    assert state["resume"]["command"] == "$resume-pipeline"


@pytest.mark.e2e
def test_default_session_state_is_complete():
    state = default_state(dataset="demo", task="pause", next_step="continue charts", now="2026-01-01 00:00 UTC")
    assert validate_state(state) == []
    assert state["pipeline"]["next_step"] == "continue charts"
    assert "resources" in state and "local_files" in state and "issues" in state


@pytest.mark.e2e
def test_session_handoff_merge_preserves_defaults():
    base = default_state(dataset="demo", task="task")
    merged = merge_state(base, {"pipeline": {"run_id": "run-1"}})
    assert merged["pipeline"]["run_id"] == "run-1"
    assert merged["pipeline"]["steps_remaining"]
    assert merged["resources"]["google_doc"]["status"] == "not used"
