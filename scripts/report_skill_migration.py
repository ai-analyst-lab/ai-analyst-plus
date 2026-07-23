#!/usr/bin/env python3
"""Report Claude/Codex skill migration coverage."""

from __future__ import annotations

import argparse
from pathlib import Path


def skill_names(root: Path, kind: str) -> set[str]:
    if kind == "claude":
        base = root / ".claude" / "skills"
        return {p.parent.name for p in base.glob("*/skill.md")} | {p.parent.name for p in base.glob("*/SKILL.md")}
    if kind == "codex":
        return {p.parent.name for p in (root / ".agents" / "skills").glob("*/SKILL.md")}
    raise ValueError(kind)


def build_report(root: Path) -> dict[str, object]:
    claude = skill_names(root, "claude")
    codex = skill_names(root, "codex")
    return {
        "claude_count": len(claude),
        "codex_count": len(codex),
        "ported_same_name": sorted(claude & codex),
        "codex_only": sorted(codex - claude),
        "missing_codex": sorted(claude - codex),
    }


def render(report: dict[str, object]) -> str:
    lines = [
        "Skill Migration Report",
        "======================",
        f"Claude skills: {report['claude_count']}",
        f"Codex skills:  {report['codex_count']}",
        f"Same-name ports: {len(report['ported_same_name'])}",
        f"Codex-only: {len(report['codex_only'])}",
        f"Missing Codex: {len(report['missing_codex'])}",
        "",
        "Same-name ports:",
    ]
    lines.extend(f"  - {name}" for name in report["ported_same_name"])
    lines.append("")
    lines.append("Codex-only:")
    lines.extend(f"  - {name}" for name in report["codex_only"])
    lines.append("")
    lines.append("Missing Codex ports:")
    lines.extend(f"  - {name}" for name in report["missing_codex"])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".")
    args = parser.parse_args()
    print(render(build_report(Path(args.root))))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
