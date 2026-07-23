"""Tests for the skill migration reporting script."""

from pathlib import Path

from scripts.report_skill_migration import build_report, render


def test_skill_migration_report_counts_current_repo():
    report = build_report(Path("."))
    assert report["claude_count"] > 0
    assert report["codex_count"] > 0
    for expected in ["data-inspect", "run-pipeline", "export", "session-handoff"]:
        assert expected in report["ported_same_name"]
    assert "claude-review" in report["codex_only"]


def test_skill_migration_report_renders_sections():
    rendered = render(build_report(Path(".")))
    assert "Skill Migration Report" in rendered
    assert "Same-name ports" in rendered
    assert "Missing Codex ports" in rendered
