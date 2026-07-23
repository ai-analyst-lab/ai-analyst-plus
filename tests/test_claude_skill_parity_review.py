"""Validation for the Claude-native skill-parity-review skill.

Mirrors the Codex-side tests in test_codex_skills.py but validates the Claude
skill that reviews Codex → Claude direction.
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


def test_claude_skill_parity_review_exists():
    """The Claude-native skill-parity-review must exist."""
    path = CLAUDE_SKILLS_DIR / "skill-parity-review" / "skill.md"
    assert path.exists(), f"Missing Claude skill-parity-review at {path}"


def test_claude_skill_parity_review_frontmatter():
    """Frontmatter name must match directory, description must be present."""
    path = CLAUDE_SKILLS_DIR / "skill-parity-review" / "skill.md"
    values = _frontmatter(path)
    assert values.get("name") == "skill-parity-review", (
        f"name mismatch: {values.get('name')}"
    )
    assert values.get("description"), "Missing description"


def test_claude_skill_parity_review_acceptance_content():
    """Verify the skill contains required structural elements."""
    path = CLAUDE_SKILLS_DIR / "skill-parity-review" / "skill.md"
    text = path.read_text()
    required = [
        "Compatibility does **not** mean copy-paste equivalence",
        "Never edit the Codex skill unless explicitly requested",
        "working/skill_parity_review/<UTC-timestamp>-<skill-name>/",
        "COMPATIBLE_WITH_NOTES",
        "BLOCKED_BY_PLATFORM",
        "static parity review",
    ]
    for phrase in required:
        assert phrase in text, f"Missing required phrase: {phrase!r}"


def test_claude_skill_parity_review_direction():
    """The Claude skill must review Codex→Claude, not Claude→Codex."""
    path = CLAUDE_SKILLS_DIR / "skill-parity-review" / "skill.md"
    text = path.read_text()
    # Must reference the codex-to-claude direction
    assert "codex-to-claude" in text, "Missing codex-to-claude direction marker"
    # Must reference editing the Claude skill, not the Codex skill by default
    assert "scaffold `.claude/skills/" in text, (
        "Should scaffold Claude skills, not Codex skills"
    )


def test_claude_skill_parity_review_has_rubric_categories():
    """All 9 compatibility categories must be present."""
    path = CLAUDE_SKILLS_DIR / "skill-parity-review" / "skill.md"
    text = path.read_text()
    categories = [
        "Metadata parity",
        "Intent parity",
        "Workflow parity",
        "Artifact/provenance parity",
        "Platform assumption safety",
        "Safety/truthfulness parity",
        "Helper/script parity",
        "Testability parity",
        "Documentation parity",
    ]
    for cat in categories:
        assert cat in text, f"Missing rubric category: {cat!r}"


def test_both_skills_share_verdict_system():
    """Claude and Codex skill-parity-review must use the same verdict system."""
    claude_path = CLAUDE_SKILLS_DIR / "skill-parity-review" / "skill.md"
    codex_path = CODEX_SKILLS_DIR / "skill-parity-review" / "SKILL.md"

    if not codex_path.exists():
        return  # Codex skill not present; skip cross-check

    claude_text = claude_path.read_text()
    codex_text = codex_path.read_text()

    # Both must use the same per-category verdicts
    per_category = ["PASS", "MINOR_GAP", "MAJOR_GAP", "BLOCKED", "NOT_APPLICABLE"]
    for verdict in per_category:
        assert verdict in claude_text, f"Claude skill missing verdict: {verdict}"
        assert verdict in codex_text, f"Codex skill missing verdict: {verdict}"

    # Both must use the same overall verdicts
    overall = [
        "COMPATIBLE",
        "COMPATIBLE_WITH_NOTES",
        "NEEDS_PORTING",
        "BLOCKED_BY_PLATFORM",
        "LEGACY_ONLY",
    ]
    for verdict in overall:
        assert verdict in claude_text, f"Claude skill missing overall: {verdict}"
        assert verdict in codex_text, f"Codex skill missing overall: {verdict}"


def test_claude_skill_parity_review_no_codex_invocation_as_self():
    """The Claude skill should not instruct itself using Codex invocation patterns."""
    path = CLAUDE_SKILLS_DIR / "skill-parity-review" / "skill.md"
    text = path.read_text()
    # $skill-name invocation used as self-instruction (not as reference to Codex)
    # The skill may mention $skill-parity-review when referring to the Codex counterpart,
    # which is acceptable. We check it doesn't use $ as its own invocation.
    lines = text.split("\n")
    for i, line in enumerate(lines, 1):
        if line.strip().startswith("$") and "invoked as" in line.lower():
            assert False, (
                f"Line {i}: Uses $ invocation as self-instruction: {line.strip()}"
            )
