# Repository Guidelines

## Project Structure & Module Organization
This repository is a Python 3.10+ product analytics toolkit organized around three layers:
- `.claude/skills/`: legacy Claude reusable analysis standards and slash-command workflows.
- `.agents/skills/`: Codex-native skills, including `$independent-review` for provider-neutral blind validation and `$claude-review` for Claude second opinions on Codex results.
- `agents/`: Markdown prompt templates for multi-step workflows; see `agents/INDEX.md`.
- `helpers/`: importable Python modules for charts, SQL, validation, experiments, exports, and provenance.

Tests live in `tests/` and use `test_*.py` naming. Example data is in `data/examples/`. Runtime/intermediate artifacts belong in `working/`; final charts, decks, and reports belong in `outputs/`. Persistent dataset context is stored under `.knowledge/`, including `.knowledge/active.yaml` and per-dataset manifests, schema docs, and quirks.

## Build, Test, and Development Commands
- `bash scripts/setup.sh`: create the local virtual environment and install baseline dependencies.
- `pip install -e ".[dev]"`: install the package in editable mode with pytest, coverage, and Faker.
- `pip install -r requirements.txt`: install the full connector dependency set.
- `pytest`: run the full test suite with configured verbose short tracebacks.
- `pytest -m "not slow"`: skip slow tests.
- `pytest tests/test_chart_palette.py`: run a focused test file.
- `python scripts/check_imports.py`: verify helper imports are clean.
- `python scripts/lint_chart_colors.py` and `python scripts/lint_wcag.py`: validate chart palette and contrast rules.
- `python scripts/check_theme_sync.py`: verify theme CSS and `themes/_base.yaml` stay aligned.

## Coding Style & Naming Conventions
Use standard Python style: 4-space indentation, descriptive snake_case for functions/modules, PascalCase for classes, and constants in UPPER_SNAKE_CASE. Keep helper logic in `helpers/` and avoid duplicating statistical routines; use `helpers/experiment_stats/` for experiment and causal calculations. For charts, call `swd_style()` before rendering and use palette/theme helpers instead of hardcoded hex values.

## Testing Guidelines
Pytest is the test framework. Add or update `tests/test_*.py` files for changed behavior. Mark long-running tests with `@pytest.mark.slow`, integration tests with `@pytest.mark.integration`, and statistical tests with `@pytest.mark.statistical`. Prefer small fixture-backed tests and include regression coverage for bug fixes.

## Commit & Pull Request Guidelines
Git history follows Conventional Commits, often with scopes, such as `feat(compare): ...` and `fix(connect): ...`. Use concise, imperative commit subjects. Pull requests should include a clear summary, motivation or linked issue, test commands run, and screenshots or output paths when charts, decks, or generated documents change.

## Security & Configuration Tips
Never print or commit credentials. The repo includes Gitleaks pre-commit configuration; run hooks before pushing when secrets or connection files changed. Before SQL analysis, read active dataset metadata in `.knowledge/`, verify connectivity, and log executed queries with `scripts/log_query.py`.
