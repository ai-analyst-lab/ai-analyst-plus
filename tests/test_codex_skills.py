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


def test_core_codex_migrated_skills_exist():
    expected = {
        "connect-data",
        "datasets",
        "switch-dataset",
        "data-inspect",
        "data-quality-check",
        "metric-spec",
        "reliability",
        "compare",
        "experiment",
        "run-pipeline",
        "resume-pipeline",
        "export",
        "independent-review",
        "claude-review",
        "skill-parity-review",
    }
    found = {p.parent.name for p in SKILLS_DIR.glob("*/SKILL.md")}
    missing = expected - found
    assert not missing, f"Missing expected Codex skills: {sorted(missing)}"


def test_codex_skill_index_lists_all_skills():
    index = (SKILLS_DIR / "INDEX.md").read_text()
    for path in sorted(SKILLS_DIR.glob("*/SKILL.md")):
        name = path.parent.name
        assert f"`{name}`" in index, f"INDEX.md missing {name}"
        assert str(path) in index, f"INDEX.md missing path for {name}"


def test_migration_matrix_lists_all_codex_skills():
    matrix = Path("docs/internal/skill-migration-matrix.md").read_text()
    for path in sorted(SKILLS_DIR.glob("*/SKILL.md")):
        name = path.parent.name
        if name == "skill-parity-review":
            # Migration utility is listed, but keep the assertion explicit below.
            pass
        assert f"`{name}`" in matrix or f"${name}" in matrix, (
            f"Migration matrix missing {name}"
        )
