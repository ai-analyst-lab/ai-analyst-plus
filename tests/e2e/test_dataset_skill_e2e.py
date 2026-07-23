"""Fixture-backed E2E smoke tests for dataset-oriented Codex skills."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from helpers.skill_runtime.dataset_skills import (
    discover_datasets,
    inspect_data,
    render_datasets,
    switch_dataset,
)


@pytest.fixture()
def demo_repo(tmp_path: Path) -> Path:
    root = tmp_path
    knowledge = root / ".knowledge"
    ds = knowledge / "datasets" / "demo"
    other = knowledge / "datasets" / "marketing-prod"
    ds.mkdir(parents=True)
    other.mkdir(parents=True)
    (root / "working").mkdir()
    (root / "outputs").mkdir()
    (knowledge / "active.yaml").write_text("active_dataset: demo\nactive_org: acme\n")
    manifest = {
        "dataset_id": "demo",
        "display_name": "Demo Commerce",
        "connection": {"type": "csv", "password": "SHOULD_NOT_RENDER"},
        "summary": {"table_count": 2, "date_range": {"start": "2024-01-01", "end": "2024-03-31"}},
    }
    (ds / "manifest.yaml").write_text(yaml.safe_dump(manifest))
    (other / "manifest.yaml").write_text(yaml.safe_dump({
        "dataset_id": "marketing-prod",
        "display_name": "Marketing Prod",
        "connection": {"type": "duckdb"},
        "summary": {"table_count": 1, "date_range": "unknown"},
    }))
    (ds / "schema.md").write_text(
        "# Schema: demo\n\n"
        "## users\n"
        "**Rows:** 100\n\n"
        "| Column | Type | Nullable | Description |\n"
        "|--------|------|----------|-------------|\n"
        "| `user_id` | INTEGER | No | Primary key |\n"
        "| `signup_date` | DATE | Yes | Signup date |\n\n"
        "## orders\n"
        "**Rows:** 500\n\n"
        "| Column | Type | Nullable | Description |\n"
        "|--------|------|----------|-------------|\n"
        "| `order_id` | INTEGER | No | Primary key |\n"
        "| `user_id` | INTEGER | Yes | FK to users |\n"
        "| `amount` | DOUBLE | Yes | Order amount |\n"
    )
    (ds / "quirks.md").write_text("# Quirks\n\n- orders.amount excludes refunds.\n")
    return root


@pytest.mark.e2e
def test_datasets_rendering_is_fixture_backed_and_redacts_secrets(demo_repo: Path):
    datasets = discover_datasets(demo_repo)
    assert [d.dataset_id for d in datasets] == ["demo", "marketing-prod"]
    assert datasets[0].active is True

    rendered = render_datasets(demo_repo)
    assert "* demo (active)" in rendered
    assert "Demo Commerce — 2 tables" in rendered
    assert "Connection: csv" in rendered
    assert "SHOULD_NOT_RENDER" not in rendered
    assert "password" not in rendered.lower()


@pytest.mark.e2e
def test_data_inspect_overview_detail_and_missing_table(demo_repo: Path):
    overview = inspect_data(demo_repo)
    assert "Active Dataset: demo" in overview
    assert "users" in overview and "orders" in overview
    assert "2 columns" in overview and "3 columns" in overview

    detail = inspect_data(demo_repo, "orders")
    assert "Table: orders" in detail
    assert "`amount`" in detail

    missing = inspect_data(demo_repo, "ordres")
    assert "not found" in missing
    assert "Available tables" in missing
    assert "orders" in missing


@pytest.mark.e2e
def test_switch_dataset_requires_confirmation_then_preserves_active_yaml_keys(demo_repo: Path):
    for i in range(3):
        (demo_repo / "working" / f"artifact_{i}.md").write_text("work")

    blocked = switch_dataset(demo_repo, "marketing", confirm_in_progress=False)
    assert blocked["ok"] is False
    assert blocked["reason"] == "needs_confirmation"

    switched = switch_dataset(demo_repo, "marketing", confirm_in_progress=True)
    assert switched["ok"] is True
    assert switched["active_dataset"] == "marketing-prod"

    active = yaml.safe_load((demo_repo / ".knowledge" / "active.yaml").read_text())
    assert active["active_dataset"] == "marketing-prod"
    assert active["active_org"] == "acme"
