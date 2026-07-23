"""Runtime helpers for local export skill smoke tests."""

from __future__ import annotations

import csv
import shutil
from datetime import date
from pathlib import Path


def find_primary_source(root: str | Path = ".") -> Path | None:
    root = Path(root)
    patterns = [
        (root / "outputs", "narrative_*.md"),
        (root / "outputs", "analysis_*.md"),
        (root / "outputs", "analysis_report_*.md"),
        (root / "working", "pipeline_summary.md"),
        (root / "working", "storyboard_*.md"),
    ]
    for directory, pattern in patterns:
        matches = [directory / pattern] if "*" not in pattern and (directory / pattern).exists() else sorted(directory.glob(pattern)) if directory.exists() else []
        if matches:
            return max(matches, key=lambda p: (p.name, p.stat().st_mtime))
    return None


def export_text_format(root: str | Path, fmt: str, *, today: str | None = None) -> Path:
    root = Path(root)
    source = find_primary_source(root)
    if source is None:
        raise FileNotFoundError("No analysis results to export")
    text = source.read_text()
    today = today or date.today().isoformat()
    outputs = root / "outputs"
    outputs.mkdir(exist_ok=True)
    mapping = {
        "email": (f"email_summary_{today}.md", "Subject: Analysis update"),
        "slack": (f"slack_update_{today}.md", "**Analysis update**"),
        "brief": (f"decision_brief_{today}.md", "# Decision Brief"),
    }
    if fmt not in mapping:
        raise ValueError(f"Unsupported local text format: {fmt}")
    filename, header = mapping[fmt]
    out = outputs / filename
    out.write_text(f"{header}\n\nSource: `{source}`\n\n{text.strip()}\n")
    return out


def export_data_package(root: str | Path) -> Path:
    root = Path(root)
    out_dir = root / "outputs" / "data"
    out_dir.mkdir(parents=True, exist_ok=True)
    copied = []
    for src in sorted((root / "working").glob("*.csv")) if (root / "working").exists() else []:
        dest = out_dir / src.name
        shutil.copyfile(src, dest)
        copied.append(dest)
    readme = out_dir / "README.md"
    lines = ["# Exported Data", ""]
    for path in copied:
        with path.open(newline="") as fh:
            reader = csv.reader(fh)
            header = next(reader, [])
            rows = sum(1 for _ in reader)
        lines.append(f"- `{path.name}` — {rows} rows, columns: {', '.join(header)}")
    if not copied:
        lines.append("No CSV data artifacts were found in `working/`.")
    readme.write_text("\n".join(lines) + "\n")
    return readme
