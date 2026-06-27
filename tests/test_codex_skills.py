"""Validation for Codex-native skills under .agents/skills."""

from pathlib import Path


SKILLS_DIR = Path(".agents/skills")
FORBIDDEN_CODEX_REFERENCES = (
    "/reload-plugins",
    "/codex:setup",
    "codex:codex-rescue",
    "openai/codex-plugin-cc",
    "~/.claude/plugins",
)


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


def test_codex_skill_frontmatter_matches_directory():
    skill_files = sorted(SKILLS_DIR.glob("*/SKILL.md"))
    assert skill_files, "No Codex skills found under .agents/skills"

    for path in skill_files:
        values = _frontmatter(path)
        assert values.get("name") == path.parent.name
        assert values.get("description"), f"{path} missing description"


def test_codex_skills_avoid_legacy_claude_plugin_mechanics():
    for path in sorted(SKILLS_DIR.glob("*/SKILL.md")):
        # skill-parity-review is itself the compatibility auditor, so it must
        # name forbidden legacy mechanics as data to flag. Other Codex skills
        # should not instruct users through those Claude/plugin flows.
        if path.parent.name == "skill-parity-review":
            continue
        text = path.read_text()
        for forbidden in FORBIDDEN_CODEX_REFERENCES:
            assert forbidden not in text, f"{path} contains forbidden reference {forbidden!r}"


def test_skill_parity_review_acceptance_content():
    path = SKILLS_DIR / "skill-parity-review" / "SKILL.md"
    text = path.read_text()
    required = [
        "Compatibility does **not** mean copy-paste equivalence",
        "Never edit the Claude skill unless explicitly requested",
        "working/skill_parity_review/<UTC-timestamp>-<skill-name>/",
        "COMPATIBLE_WITH_NOTES",
        "BLOCKED_BY_PLATFORM",
        "static parity review",
    ]
    for phrase in required:
        assert phrase in text
