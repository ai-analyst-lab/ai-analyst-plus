"""Validation for the Claude-native independent-review skill.

Checks structural requirements, forbidden references, and cross-direction
consistency with the Codex independent-review skill.
"""

from pathlib import Path


CLAUDE_SKILLS_DIR = Path(".claude/skills")
CODEX_SKILLS_DIR = Path(".agents/skills")


def _frontmatter(path: Path) -> dict[str, str]:
    text = path.read_text()
    assert text.startswith("---\n"), f"{path} missing YAML frontmatter"
    front = text.split("---\n", 2)[1]
    values: dict[str, str] = {}
    for line in front.splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            values[key.strip()] = value.strip()
    return values


def test_claude_independent_review_exists():
    path = CLAUDE_SKILLS_DIR / "independent-review" / "skill.md"
    assert path.exists(), f"Missing Claude independent-review at {path}"


def test_claude_independent_review_frontmatter():
    path = CLAUDE_SKILLS_DIR / "independent-review" / "skill.md"
    values = _frontmatter(path)
    assert values.get("name") == "independent-review"
    assert values.get("description"), "Missing description"


def test_claude_independent_review_acceptance_content():
    """Verify the skill contains required structural elements."""
    path = CLAUDE_SKILLS_DIR / "independent-review" / "skill.md"
    text = path.read_text()
    required = [
        # Hard gate
        "HARD GATE",
        "do not fake independence",
        # Blind brief requirement
        "Do **NOT** include original SQL",
        # Run directory convention
        "working/independent_review/",
        # Verdict system
        "AGREE",
        "PARTIAL",
        "DISAGREE",
        # Audit log
        ".knowledge/independent-review/log.jsonl",
        # Verdict schema
        "verdict.json",
        "verdict.md",
        "brief.md",
        "original_result.md",
        "independent_result.md",
    ]
    for phrase in required:
        assert phrase in text, f"Missing required phrase: {phrase!r}"


def test_claude_independent_review_no_codex_cli_dependency():
    """The Claude skill should not depend on Codex CLI or plugin mechanics."""
    path = CLAUDE_SKILLS_DIR / "independent-review" / "skill.md"
    text = path.read_text()
    forbidden_as_dependency = [
        "codex_validation.py --check",
        "/reload-plugins",
        "/plugin install",
        "openai/codex-plugin-cc",
    ]
    for forbidden in forbidden_as_dependency:
        assert forbidden not in text, (
            f"Claude skill should not depend on: {forbidden!r}"
        )


def test_claude_independent_review_uses_agent_tool():
    """The Claude skill should use the Agent tool for isolation, not Codex CLI."""
    path = CLAUDE_SKILLS_DIR / "independent-review" / "skill.md"
    text = path.read_text()
    assert "Agent tool" in text, "Should reference Agent tool for dispatching subagent"


def test_both_skills_share_verdict_schema():
    """Claude and Codex independent-review must use the same verdict keys."""
    claude_path = CLAUDE_SKILLS_DIR / "independent-review" / "skill.md"
    codex_path = CODEX_SKILLS_DIR / "independent-review" / "SKILL.md"

    if not codex_path.exists():
        return  # Codex skill not present; skip

    claude_text = claude_path.read_text()
    codex_text = codex_path.read_text()

    # Both must use the same verdict values
    for verdict in ["AGREE", "PARTIAL", "DISAGREE"]:
        assert verdict in claude_text, f"Claude missing verdict: {verdict}"
        assert verdict in codex_text, f"Codex missing verdict: {verdict}"

    # Both must write to the same audit log
    log_path = ".knowledge/independent-review/log.jsonl"
    assert log_path in claude_text, f"Claude missing audit log: {log_path}"
    assert log_path in codex_text, f"Codex missing audit log: {log_path}"


def test_both_skills_share_artifact_paths():
    """Both skills should use the same run directory and file conventions."""
    claude_path = CLAUDE_SKILLS_DIR / "independent-review" / "skill.md"
    codex_path = CODEX_SKILLS_DIR / "independent-review" / "SKILL.md"

    if not codex_path.exists():
        return

    claude_text = claude_path.read_text()
    codex_text = codex_path.read_text()

    shared_artifacts = [
        "working/independent_review/",
        "brief.md",
        "original_result.md",
        "independent_result.md",
        "verdict.md",
        "verdict.json",
    ]
    for artifact in shared_artifacts:
        assert artifact in claude_text, f"Claude missing artifact: {artifact}"
        assert artifact in codex_text, f"Codex missing artifact: {artifact}"
