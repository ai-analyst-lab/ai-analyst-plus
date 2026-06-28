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
        "presentation-themes",
        "session-handoff",
        "google-doc-export",
        "google-slides-export",
        "notion-export",
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


RECENT_EASY_MEDIUM_PORTS = {
    "archive-analysis",
    "business",
    "close-the-loop",
    "compare-datasets",
    "data-profiling",
    "feedback-capture",
    "forecast",
    "guardrails",
    "history",
    "log-correction",
    "metrics",
    "pace",
    "patterns",
    "question-framing",
    "runs",
    "srm-check",
    "stakeholder-communication",
    "teach",
    "theme-picker",
    "trace",
}


def test_easy_medium_migrated_skills_exist():
    found = {p.parent.name for p in SKILLS_DIR.glob("*/SKILL.md")}
    missing = RECENT_EASY_MEDIUM_PORTS - found
    assert not missing, f"Missing newly migrated Codex skills: {sorted(missing)}"


def test_easy_medium_ports_have_codex_native_language():
    for name in sorted(RECENT_EASY_MEDIUM_PORTS):
        path = SKILLS_DIR / name / "SKILL.md"
        text = path.read_text()
        assert f"name: {name}" in text
        assert "# " in text, f"{path} missing body heading"
        assert "## Purpose" in text, f"{path} missing purpose section"
        assert "## Workflow" in text or "## Modes" in text, (
            f"{path} missing workflow/modes section"
        )
        legacy_invocation = "/" + name
        forbidden_invocation_phrases = (
            f"invoked as `{legacy_invocation}`",
            f"user says `{legacy_invocation}`",
            f"type `{legacy_invocation}`",
            f"run `{legacy_invocation}`",
        )
        lowered = text.lower()
        for phrase in forbidden_invocation_phrases:
            assert phrase not in lowered, (
                f"{path} should not depend on slash-command invocation"
            )


def test_easy_medium_ports_preserve_key_artifact_contracts():
    expected_phrases = {
        "archive-analysis": [".knowledge/analyses", "partial: true"],
        "business": ["helpers.business_context", "does not query datasets"],
        "close-the-loop": ["Follow-up Plan", "baseline", "target"],
        "compare-datasets": ["definition drift", "time windows"],
        "data-profiling": ["working/data_profiles", "null rates"],
        "feedback-capture": [".knowledge/corrections", ".knowledge/learnings"],
        "forecast": ["naive baseline", "confidence"],
        "guardrails": ["Guardrail Check", "TRADE-OFF"],
        "history": [".knowledge/analyses/index.yaml", "active dataset"],
        "log-correction": ["CORR-###", "severity"],
        "metrics": ["metric dictionary", "$metric-spec"],
        "pace": ["guided", "autopilot"],
        "patterns": ["_patterns.yaml", "stale"],
        "question-framing": ["Framed Question", "assumptions"],
        "runs": ["working/runs", "clean"],
        "srm-check": ["Sample Ratio Mismatch", "BLOCK"],
        "stakeholder-communication": ["Executive", "Product"],
        "teach": ["outputs/charts/teach", "signal-vs-noise"],
        "theme-picker": ["default_theme", "swd_style"],
        "trace": ["helpers.trace_viewer.build_trace", "unmatched"],
    }
    for name, phrases in expected_phrases.items():
        text = (SKILLS_DIR / name / "SKILL.md").read_text()
        for phrase in phrases:
            assert phrase in text, f"{name} missing expected phrase {phrase!r}"


def test_teach_port_includes_runnable_topic_script():
    topic = SKILLS_DIR / "teach" / "topics" / "signal_vs_noise.py"
    assert topic.exists()
    text = topic.read_text()
    assert "def main" in text
    assert "outputs/charts/teach" in text


def test_teach_port_uses_shared_signal_vs_noise_topic():
    shared_topic = Path("shared/teach/topics/signal_vs_noise.py")
    codex_wrapper = SKILLS_DIR / "teach" / "topics" / "signal_vs_noise.py"
    assert shared_topic.exists()
    assert "def main" in shared_topic.read_text()
    assert "shared" in codex_wrapper.read_text()


def test_migration_report_reflects_easy_medium_batch():
    from scripts.report_skill_migration import build_report

    report = build_report(Path("."))
    assert report["codex_count"] >= 40
    assert not (RECENT_EASY_MEDIUM_PORTS - set(report["ported_same_name"]))
    for name in RECENT_EASY_MEDIUM_PORTS:
        assert name not in report["missing_codex"]


NEXT_MEDIUM_PORTS = {
    "analysis-design",
    "analysis-design-spec",
    "archaeology",
    "causal",
    "data-map",
    "experiment-brief",
    "explore",
    "stress-test",
    "tracking-gaps",
    "triangulation",
}


def test_next_medium_migrated_skills_exist():
    found = {p.parent.name for p in SKILLS_DIR.glob("*/SKILL.md")}
    missing = NEXT_MEDIUM_PORTS - found
    assert not missing, f"Missing next-batch Codex skills: {sorted(missing)}"


def test_next_medium_ports_preserve_key_contracts():
    expected_phrases = {
        "analysis-design": ["Analysis Design Brief", "Confound Scanner"],
        "analysis-design-spec": ["Analysis Design Spec", "seven"],
        "archaeology": ["query-archaeology", "Read-only"],
        "causal": ["Mandatory caveats", "counterfactual"],
        "data-map": ["Join-Rate Matrix", "Relationship Map"],
        "experiment-brief": ["North Star Metric", "Guardrail Metrics"],
        "explore": ["Question Router", "working/explore_notes"],
        "stress-test": ["Stress Test Scorecard", "Kill criteria"],
        "tracking-gaps": ["Tracking Gap Report", "Instrumentation Requests"],
        "triangulation": ["Validation Report", "segment-first"],
    }
    for name, phrases in expected_phrases.items():
        text = (SKILLS_DIR / name / "SKILL.md").read_text()
        assert "## Purpose" in text
        assert "## Workflow" in text
        for phrase in phrases:
            assert phrase in text, f"{name} missing expected phrase {phrase!r}"


def test_next_medium_ports_are_in_docs_and_report():
    index = (SKILLS_DIR / "INDEX.md").read_text()
    matrix = Path("docs/internal/skill-migration-matrix.md").read_text()
    from scripts.report_skill_migration import build_report

    report = build_report(Path("."))
    ported = set(report["ported_same_name"])
    for name in NEXT_MEDIUM_PORTS:
        assert f"`{name}`" in index
        assert f".agents/skills/{name}/SKILL.md" in index
        assert f"`{name}`" in matrix or f"${name}" in matrix
        assert name in ported
        assert name not in report["missing_codex"]

EXPERT_TOOL_PORT_CONTRACTS = {
    "north-star": ['North Star Metric', 'refusal', '7-checklist', 'outputs/north-star'],
    "visualization-patterns": ['swd_style', 'gray everything', 'action title'],
    "semantic-validation": ['Semantic Validation Report', 'Simpson', 'Confidence Score', 'BLOCKER'],
    "question-router": ['L1', 'L5', 'North Star', 'narrated'],
    "setup": ['4-phase', '.knowledge/setup-state.yaml', 'reset everything'],
}


def test_expert_tool_migrated_skills_exist():
    found = {p.parent.name for p in SKILLS_DIR.glob("*/SKILL.md")}
    missing = set(EXPERT_TOOL_PORT_CONTRACTS) - found
    assert not missing, f"Missing expert/tool Codex skills: {sorted(missing)}"


def test_expert_tool_ports_preserve_key_contracts():
    for name, phrases in EXPERT_TOOL_PORT_CONTRACTS.items():
        text = (SKILLS_DIR / name / "SKILL.md").read_text()
        assert "## Purpose" in text
        assert "## Workflow" in text
        for phrase in phrases:
            assert phrase in text, f"{name} missing expected phrase {phrase!r}"


def test_expert_tool_ports_are_in_docs_and_report():
    index = (SKILLS_DIR / "INDEX.md").read_text()
    matrix = Path("docs/internal/skill-migration-matrix.md").read_text()
    from scripts.report_skill_migration import build_report

    report = build_report(Path("."))
    ported = set(report["ported_same_name"])
    for name in EXPERT_TOOL_PORT_CONTRACTS:
        assert f"`{name}`" in index
        assert f".agents/skills/{name}/SKILL.md" in index
        assert f"`{name}`" in matrix or f"${name}" in matrix
        assert name in ported
        assert name not in report["missing_codex"]

REMAINING_PORT_CONTRACTS = {
    "kickoff": ['Slack', 'confirm before posting', 'introductions'],
    "distribution-profiler": ['Distribution Profile', 'skewness', 'A/B'],
    "deck-rescue": ['working/deck_rescue', 'before_after', 'speaker notes'],
    "deck-critique": ['Data Story Checklist', 'SO-WHAT', 'ASK'],
    "connect-snowflake": ['Snowflake', 'ConnectionManager', '.knowledge/datasets'],
    "chart-to-drive": ['outputs/charts', 'working/chart_drive_manifest', 'Drive'],
    "auth-preflight": ['Google Workspace', 'Auth: OK', 'local fallback'],
    "architect": ['multi-persona', 'MASTER_PLAN.md', 'BUILD_STATUS.yaml'],
}


def test_remaining_migrated_skills_exist():
    found = {p.parent.name for p in SKILLS_DIR.glob("*/SKILL.md")}
    missing = set(REMAINING_PORT_CONTRACTS) - found
    assert not missing, f"Missing remaining Codex skills: {sorted(missing)}"


def test_remaining_ports_preserve_key_contracts():
    for name, phrases in REMAINING_PORT_CONTRACTS.items():
        text = (SKILLS_DIR / name / "SKILL.md").read_text()
        assert "## Purpose" in text
        assert "## Workflow" in text
        for phrase in phrases:
            assert phrase in text, f"{name} missing expected phrase {phrase!r}"


def test_remaining_ports_are_in_docs_and_report():
    index = (SKILLS_DIR / "INDEX.md").read_text()
    matrix = Path("docs/internal/skill-migration-matrix.md").read_text()
    from scripts.report_skill_migration import build_report

    report = build_report(Path("."))
    ported = set(report["ported_same_name"])
    for name in REMAINING_PORT_CONTRACTS:
        assert f"`{name}`" in index
        assert f".agents/skills/{name}/SKILL.md" in index
        assert f"`{name}`" in matrix or f"${name}" in matrix
        assert name in ported
        assert name not in report["missing_codex"]

FINAL_PORT_CONTRACTS = {
    "slide-transform": ['SO-WHAT', 'working/slide_transform', 'Headline Fix'],
    "skill-creator": ['progressive disclosure', 'evals/evals.json', 'benchmark'],
    "show-off": ['git status --short', 'ASCII diagram', 'confirm before posting'],
    "setup-snowflake": ['Snowflake', 'read-only', '.knowledge/datasets'],
    "setup-notion": ['OAuth', 'Analysis Gallery', '.mcp.json'],
    "setup-dev-context": ['.knowledge/user/dev-context.yaml', 'SQL conventions', 'dev_context'],
    "notion-ingest": ['BFS', '.knowledge/query-archaeology/raw', 'business/metrics/index.yaml'],
    "knowledge-bootstrap": ['.knowledge/active.yaml', 'semantic/entities.yaml', '.bootstrap_timestamp'],
    "eval": ['held-out', 'blind', 'query similarity'],
    "codex-review": ['AGREE', 'DISAGREE', 'blind brief'],
}


def test_final_migrated_skills_exist():
    found = {p.parent.name for p in SKILLS_DIR.glob("*/SKILL.md")}
    missing = set(FINAL_PORT_CONTRACTS) - found
    assert not missing, f"Missing final Codex skills: {sorted(missing)}"


def test_final_ports_preserve_key_contracts():
    for name, phrases in FINAL_PORT_CONTRACTS.items():
        text = (SKILLS_DIR / name / "SKILL.md").read_text()
        assert "## Purpose" in text
        assert "## Workflow" in text
        for phrase in phrases:
            assert phrase in text, f"{name} missing expected phrase {phrase!r}"


def test_final_ports_are_in_docs_and_report():
    index = (SKILLS_DIR / "INDEX.md").read_text()
    matrix = Path("docs/internal/skill-migration-matrix.md").read_text()
    from scripts.report_skill_migration import build_report

    report = build_report(Path("."))
    ported = set(report["ported_same_name"])
    for name in FINAL_PORT_CONTRACTS:
        assert f"`{name}`" in index
        assert f".agents/skills/{name}/SKILL.md" in index
        assert f"`{name}`" in matrix or f"${name}" in matrix
        assert name in ported
        assert name not in report["missing_codex"]


def test_all_claude_skills_have_codex_ports_except_codex_only():
    from scripts.report_skill_migration import build_report

    report = build_report(Path("."))
    assert report["missing_codex"] == []
    assert report["codex_only"] == ["claude-review"]

SHARED_CONTENT_CONTRACTS = {
    "architect": ["shared/PLANNING_METHODOLOGY.md"],
    "causal": ["helpers/experiment_stats/causal/"],
    "north-star": ["helpers/north_star/", "shared/north-star/wiki/"],
    "skill-creator": ["shared/skill-creator/README.md", ".claude/skills/skill-creator/scripts/"],
}


def test_codex_skills_reference_shared_provider_neutral_content():
    for name, phrases in SHARED_CONTENT_CONTRACTS.items():
        text = (SKILLS_DIR / name / "SKILL.md").read_text()
        for phrase in phrases:
            assert phrase in text, f"{name} missing shared content reference {phrase!r}"


def test_skill_creator_shared_tooling_contract_exists():
    path = Path("shared/skill-creator/README.md")
    assert path.exists()
    text = path.read_text()
    assert "progressive disclosure" in text
    assert "evals/evals.json" in text
    assert "aggregate_benchmark.py" in text
