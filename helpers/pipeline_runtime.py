"""Deterministic pipeline runtime helpers.

Small, production-safe primitives for validating the agent registry, computing
execution tiers and READY sets, rendering dry-run plans, and preparing resume
plans. These helpers intentionally do not execute LLM agents; they make the
pipeline orchestration rules testable and reusable by Codex/Claude wrappers.
"""

from __future__ import annotations

import json
from collections import defaultdict, deque
from pathlib import Path
from typing import Any

import yaml

from helpers.pipeline_state import detect_schema_version, migrate_v1_to_v2

TERMINAL_COMPLETE = {"complete", "completed", "skipped", "degraded"}


def load_registry(path: str | Path = "agents/registry.yaml") -> dict[str, dict[str, Any]]:
    data = yaml.safe_load(Path(path).read_text())
    agents = data.get("agents", []) if isinstance(data, dict) else []
    return {a["name"]: a for a in agents if isinstance(a, dict) and a.get("name")}


def validate_registry(path: str | Path = "agents/registry.yaml", root: str | Path = ".") -> dict[str, Any]:
    root = Path(root)
    registry = load_registry(path)
    errors: list[str] = []
    for name, agent in registry.items():
        file_path = root / agent.get("file", "")
        if not file_path.exists():
            errors.append(f"Agent file not found: {agent.get('file')} ({name})")
        for dep in agent.get("depends_on") or []:
            if dep not in registry:
                errors.append(f"Unknown dependency: {name} depends on {dep}")
        for dep in agent.get("depends_on_any") or []:
            if dep not in registry:
                errors.append(f"Unknown OR dependency: {name} depends on {dep}")
    tiers = compute_tiers(registry) if not errors else []
    return {"ok": not errors, "errors": errors, "agent_count": len(registry), "tiers": tiers}


def compute_tiers(registry: dict[str, dict[str, Any]]) -> list[list[str]]:
    active = {name: a for name, a in registry.items() if a.get("pipeline_step") is not None}
    indegree = {name: 0 for name in active}
    children: dict[str, list[str]] = defaultdict(list)
    for name, agent in active.items():
        deps = [d for d in (agent.get("depends_on") or []) if d in active]
        # OR deps are real ordering edges for tiering, even though readiness is any-one.
        deps += [d for d in (agent.get("depends_on_any") or []) if d in active]
        for dep in deps:
            children[dep].append(name)
            indegree[name] += 1
    queue = deque(sorted([name for name, deg in indegree.items() if deg == 0]))
    tiers: list[list[str]] = []
    processed = set()
    while queue:
        tier = list(queue)
        queue.clear()
        tiers.append(tier)
        for node in tier:
            processed.add(node)
            for child in children[node]:
                indegree[child] -= 1
                if indegree[child] == 0:
                    queue.append(child)
        queue = deque(sorted(queue))
    if len(processed) != len(active):
        remaining = sorted(set(active) - processed)
        raise ValueError(f"Cycle detected or unresolved dependencies: {remaining}")
    return tiers


def dry_run_plan(
    registry_path: str | Path = "agents/registry.yaml",
    *,
    root: str | Path = ".",
    plan_name: str = "full_presentation",
) -> str:
    validation = validate_registry(registry_path, root=root)
    if not validation["ok"]:
        return "Registry validation failed:\n" + "\n".join(validation["errors"])
    lines = [
        "Execution Plan (dry-run):",
        f"Plan: {plan_name}",
        f"Agents: {validation['agent_count']} registered",
        "",
    ]
    for i, tier in enumerate(validation["tiers"]):
        mode = "parallel" if len(tier) > 1 else "sequential"
        lines.append(f"Tier {i}: {tier} ({mode})")
    return "\n".join(lines)


def locate_pipeline_state(root: str | Path = ".", run_id: str | None = None) -> Path | None:
    root = Path(root)
    candidates = []
    latest = root / "working" / "latest" / "pipeline_state.json"
    candidates.append(latest)
    if run_id:
        candidates.append(root / "working" / "runs" / run_id / "pipeline_state.json")
    candidates.append(root / "working" / "pipeline_state.json")
    return next((p for p in candidates if p.exists()), None)


def compute_ready_agents(state: dict[str, Any], registry: dict[str, dict[str, Any]]) -> list[str]:
    states = state.get("agents", {})

    def complete(agent_name: str) -> bool:
        return str(states.get(agent_name, {}).get("status", "pending")) in TERMINAL_COMPLETE

    ready = []
    for name, agent in registry.items():
        if agent.get("pipeline_step") is None:
            continue
        status = str(states.get(name, {}).get("status", "pending"))
        if status in TERMINAL_COMPLETE or status not in {"pending", "failed", "running", "in_progress"}:
            continue
        deps = agent.get("depends_on") or []
        any_deps = agent.get("depends_on_any") or []
        if all(complete(dep) for dep in deps) and (not any_deps or any(complete(dep) for dep in any_deps)):
            ready.append(name)
    return sorted(ready)


def resume_plan(root: str | Path = ".", registry_path: str | Path | None = None) -> dict[str, Any]:
    root = Path(root)
    state_path = locate_pipeline_state(root)
    if state_path is None:
        return {"ok": False, "reason": "no_state"}
    state = json.loads(state_path.read_text())
    if detect_schema_version(state) < 2:
        dataset = state.get("dataset") or "unknown"
        state = migrate_v1_to_v2(state, dataset=dataset)
    registry = load_registry(registry_path or root / "agents" / "registry.yaml")
    # Treat interrupted/failed as pending for readiness calculation.
    for entry in state.get("agents", {}).values():
        if entry.get("status") in {"failed", "running", "in_progress"}:
            entry["status"] = "pending"
    ready = compute_ready_agents(state, registry)
    completed = [n for n, s in state.get("agents", {}).items() if s.get("status") in TERMINAL_COMPLETE]
    return {
        "ok": True,
        "state_path": str(state_path),
        "run_id": state.get("run_id"),
        "question": state.get("question"),
        "dataset": state.get("dataset"),
        "completed": sorted(completed),
        "ready": ready,
    }
