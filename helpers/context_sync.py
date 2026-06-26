"""Resolve where the analyst reads its context from: local (in this tool) or a communal git repo.

Reads .knowledge/context-source.yaml. If source is 'git', clone (or pull) the communal context repo into a
local cache and return the dataset directory inside it. If 'local' (or no config), return the in-repo
dataset directory. knowledge-bootstrap calls this BEFORE loading the semantic layer, so the same loader
works whether context lives in the tool (the C0-C2 individual setup) or in the team's repo (the C3 team
setup). The team curates the context repo via PRs; each analyst points at it and pulls.

Only context is synced here (semantic layer + metric defs). The gold/answer-key is never in the context
repo; it stays hidden with the eval harness.
"""
from __future__ import annotations

import subprocess
from pathlib import Path


def _git(*args: str) -> int:
    return subprocess.run(["git", *args], capture_output=True, text=True).returncode


def resolve_context_dir(active_dataset: str, project_root: str | Path = ".") -> tuple[Path, str]:
    """Return (dataset_context_dir, source) where source is 'local' or 'git'.

    dataset_context_dir is the directory that holds this dataset's semantic/ and metrics/ - either the
    in-repo .knowledge/datasets/{active}/ (local) or the synced communal repo's dataset path (git)."""
    root = Path(project_root)
    local_dir = root / ".knowledge" / "datasets" / active_dataset
    cfg_path = root / ".knowledge" / "context-source.yaml"
    if not cfg_path.exists():
        return local_dir, "local"

    import yaml
    cfg = yaml.safe_load(cfg_path.read_text()) or {}
    if cfg.get("source", "local") != "git":
        return local_dir, "local"

    repo = cfg["repo"]
    ref = str(cfg.get("ref", "main"))
    dataset_path = cfg.get("dataset_path", f"datasets/{active_dataset}")
    cache = root / cfg.get("cache", ".knowledge/.context-cache")

    if (cache / ".git").exists():
        # Already cloned: fetch + checkout + pull the ref (latest team context, or a pinned commit).
        _git("-C", str(cache), "fetch", "--quiet", "origin", ref)
        _git("-C", str(cache), "checkout", "--quiet", ref)
        _git("-C", str(cache), "pull", "--quiet", "origin", ref)
    else:
        cache.parent.mkdir(parents=True, exist_ok=True)
        _git("clone", "--quiet", repo, str(cache))
        _git("-C", str(cache), "checkout", "--quiet", ref)

    return cache / dataset_path, "git"
