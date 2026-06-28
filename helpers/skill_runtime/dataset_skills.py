"""Runtime helpers for dataset-oriented Codex skills."""

from __future__ import annotations

import difflib
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

SECRET_KEYS = {"password", "token", "secret", "private_key", "api_key"}


@dataclass
class DatasetSummary:
    dataset_id: str
    display_name: str
    active: bool
    connection_type: str
    table_count: int | None
    date_range: str
    status: str = "ok"


def _safe_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    data = yaml.safe_load(path.read_text())
    return data if isinstance(data, dict) else {}


def _knowledge(root: Path) -> Path:
    return root / ".knowledge"


def read_active_dataset(root: str | Path = ".") -> str | None:
    data = _safe_yaml(_knowledge(Path(root)) / "active.yaml")
    active = data.get("active_dataset")
    return str(active) if active else None


def discover_datasets(root: str | Path = ".") -> list[DatasetSummary]:
    root = Path(root)
    active = read_active_dataset(root)
    datasets_dir = _knowledge(root) / "datasets"
    summaries: list[DatasetSummary] = []
    if not datasets_dir.exists():
        return summaries

    for ds_dir in sorted(p for p in datasets_dir.iterdir() if p.is_dir()):
        manifest = _safe_yaml(ds_dir / "manifest.yaml")
        if not manifest:
            summaries.append(
                DatasetSummary(
                    dataset_id=ds_dir.name,
                    display_name=ds_dir.name,
                    active=ds_dir.name == active,
                    connection_type="unknown",
                    table_count=None,
                    date_range="unknown",
                    status="missing_manifest",
                )
            )
            continue
        conn = manifest.get("connection", {}) if isinstance(manifest.get("connection"), dict) else {}
        summary = manifest.get("summary", {}) if isinstance(manifest.get("summary"), dict) else {}
        date_range = summary.get("date_range") or "unknown"
        if isinstance(date_range, dict):
            start = date_range.get("start", "unknown")
            end = date_range.get("end", "unknown")
            date_range = f"{start} to {end}"
        summaries.append(
            DatasetSummary(
                dataset_id=ds_dir.name,
                display_name=str(manifest.get("display_name") or ds_dir.name),
                active=ds_dir.name == active,
                connection_type=str(conn.get("type") or manifest.get("connection_type") or "unknown"),
                table_count=summary.get("table_count"),
                date_range=str(date_range),
            )
        )
    return summaries


def render_datasets(root: str | Path = ".") -> str:
    datasets = discover_datasets(root)
    if not datasets:
        return "No connected datasets found. Use `$connect-data` to add a dataset."
    lines = ["Connected Datasets:", ""]
    for ds in datasets:
        marker = "*" if ds.active else "-"
        active = " (active)" if ds.active else ""
        tables = "unknown" if ds.table_count is None else str(ds.table_count)
        lines.extend([
            f"  {marker} {ds.dataset_id}{active}",
            f"    {ds.display_name} — {tables} tables, {ds.date_range}",
            f"    Connection: {ds.connection_type}",
        ])
        if ds.status != "ok":
            lines.append(f"    Status: {ds.status}")
        lines.append("")
    lines.extend([
        "Commands:",
        "  $switch-dataset {name}  — switch active dataset",
        "  $connect-data           — connect a new dataset",
        "  $data-inspect           — inspect active dataset schema",
    ])
    return "\n".join(lines)


def _parse_schema_tables(schema_text: str) -> dict[str, str]:
    matches = list(re.finditer(r"^##\s+(.+?)\s*$", schema_text, flags=re.MULTILINE))
    tables: dict[str, str] = {}
    for i, match in enumerate(matches):
        name = match.group(1).strip().strip("`")
        start = match.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(schema_text)
        tables[name] = schema_text[start:end].strip()
    return tables


def inspect_data(root: str | Path = ".", table: str | None = None) -> str:
    root = Path(root)
    active = read_active_dataset(root)
    if not active:
        return "No active dataset configured. Use `$connect-data` or `$datasets`."
    schema_path = _knowledge(root) / "datasets" / active / "schema.md"
    if not schema_path.exists():
        return f"No schema.md found for active dataset {active}."
    schema = schema_path.read_text()
    tables = _parse_schema_tables(schema)
    if table:
        match = next((name for name in tables if name.lower() == table.lower()), None)
        if not match:
            available = ", ".join(tables) if tables else "(none)"
            suggestion = difflib.get_close_matches(table, list(tables), n=1)
            extra = f"\nDid you mean: {suggestion[0]}?" if suggestion else ""
            return f"Table `{table}` was not found in {active}.\n\nAvailable tables: {available}{extra}"
        return f"Active Dataset: {active}\nTable: {match}\n\n{tables[match]}"
    lines = [f"Active Dataset: {active}", "", "Tables:"]
    for name, section in tables.items():
        col_count = section.count("| `")
        row_match = re.search(r"\*\*Rows:\*\*\s*([^\n]+)", section)
        rows = row_match.group(1).strip() if row_match else "rows not profiled"
        lines.append(f"  {name:<15} {rows:<14} {col_count} columns")
    return "\n".join(lines)


def switch_dataset(
    root: str | Path,
    target: str,
    *,
    confirm_in_progress: bool = False,
    in_progress_threshold: int = 3,
) -> dict[str, Any]:
    root = Path(root)
    datasets = discover_datasets(root)
    ids = [d.dataset_id for d in datasets if d.status == "ok"]
    lowered = {i.lower(): i for i in ids}
    actual = lowered.get(target.lower())
    if actual is None:
        matches = [i for i in ids if target.lower() in i.lower()]
        if len(matches) == 1:
            actual = matches[0]
        elif len(matches) > 1:
            return {"ok": False, "reason": "ambiguous", "matches": matches}
        else:
            return {"ok": False, "reason": "not_found", "available": ids}

    old = read_active_dataset(root)
    if actual == old:
        return {"ok": True, "changed": False, "active_dataset": actual, "message": "already active"}

    working = root / "working"
    items = []
    if working.exists():
        items = [p.name for p in working.iterdir() if not p.name.startswith(".") and p.name != ".gitkeep"]
    if len(items) >= in_progress_threshold and not confirm_in_progress:
        return {"ok": False, "reason": "needs_confirmation", "items": items[:5], "old_dataset": old}

    active_path = _knowledge(root) / "active.yaml"
    data = _safe_yaml(active_path)
    data["active_dataset"] = actual
    active_path.parent.mkdir(parents=True, exist_ok=True)
    active_path.write_text(yaml.safe_dump(data, sort_keys=False))
    return {"ok": True, "changed": True, "old_dataset": old, "active_dataset": actual}
