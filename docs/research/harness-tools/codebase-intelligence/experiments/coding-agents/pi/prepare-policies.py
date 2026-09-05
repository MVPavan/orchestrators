#!/usr/bin/env python3
"""Materialize the three sealed Pi tracer graph policies."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
CAPABILITIES = HERE.parent / "capabilities"
SUBJECTS = Path("scratchpad/code-intelligence/subjects/pi")
INDEXES = Path("scratchpad/code-intelligence/indexes/pi-tracer-v1")
FROZEN = json.loads((HERE / "tracer-arms.json").read_text(encoding="utf-8"))


def workspace_root() -> Path:
    for parent in HERE.parents:
        if (parent / ".git").exists():
            return parent
    raise RuntimeError("cannot locate workspace root")


def load_interface():
    path = CAPABILITIES / "evaluated-interface.py"
    spec = importlib.util.spec_from_file_location("pi_evaluated_interface", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load evaluated interface")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def arm_operations(arm_id: str) -> list[str]:
    arm = next(arm for arm in FROZEN["arms"] if arm["id"] == arm_id)
    return arm["allowed_graph_operations"]


def main() -> int:
    root = workspace_root()
    interface = load_interface()
    configurations = {
        "graphify": {
            "subject": root / SUBJECTS / "graphify",
            "scratch": root / INDEXES / "graphify",
            "executable": root / INDEXES / "graphify/bin/graphify",
        },
        "cbm": {
            "subject": root / SUBJECTS / "cbm",
            "scratch": root / INDEXES / "cbm",
            "executable": root / INDEXES / "cbm/bin/codebase-memory-mcp",
        },
        "codegraph": {
            "subject": root / SUBJECTS / "codegraph",
            "scratch": root / "scratchpad/code-intelligence/runtime/lanes/codegraph-probe",
            "executable": (
                root
                / "scratchpad/code-intelligence/runtime/lanes/codegraph-probe"
                / "tool/dist/bin/codegraph.js"
            ),
        },
    }
    for lane, paths in configurations.items():
        template_path = CAPABILITIES / f"adapter-policies/{lane}.template.json"
        template = json.loads(template_path.read_text(encoding="utf-8"))
        allowed = arm_operations(f"{lane}-assisted")
        template["allowed_tool_names"] = allowed
        if lane == "cbm":
            template["environment"]["CBM_CACHE_DIR"] = "${SCRATCH_ROOT}/cache"
        elif lane == "codegraph":
            template["environment"]["CODEGRAPH_DIR"] = ".codegraph-tracer"
        elif lane == "graphify":
            template = json.loads(
                json.dumps(template).replace(
                    "${SCRATCH_ROOT}/graph/graph.json",
                    "${SCRATCH_ROOT}/graph.json",
                )
            )
        policy = interface.materialize_policy(
            template,
            paths["subject"],
            paths["scratch"],
            paths["executable"],
            None,
        )
        output = paths["scratch"] / "pi-tracer-policy.json"
        output.write_text(
            json.dumps(policy, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        print(f"PASS: {lane} policy exposes {len(allowed)} operations at {output}")
    print("provider calls: 0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
