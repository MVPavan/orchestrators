#!/usr/bin/env python3
"""Validate the frozen Pi tracer contract without launching a provider."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


HERE = Path(__file__).resolve().parent
FROZEN_OPERATIONS = {
    "source-only": [],
    "codegraph-assisted": [
        "query",
        "explore",
        "callers",
        "callees",
        "impact",
        "node",
        "status",
        "files",
    ],
    "cbm-assisted": [
        "search_graph",
        "query_graph",
        "trace_path",
        "get_code_snippet",
        "get_graph_schema",
        "get_architecture",
        "search_code",
        "list_projects",
        "index_status",
    ],
    "graphify-assisted": [
        "query",
        "explain",
        "path",
        "affected",
        "god_nodes",
        "diagnose",
        "benchmark",
    ],
}
FROZEN_STOP_CONDITIONS = [
    "preflight failure",
    "setup failure before inference",
    "missing provider usage event",
    "more than one answer turn",
    "source access before the assigned graph in an assisted arm",
    "access to another graph tool, web, reference answer, or scoring anchor",
    "unexpected source write or live-submodule access",
    "one arm exceeds 12 credit-equivalent",
]


def workspace_root() -> Path:
    for parent in HERE.parents:
        if (parent / ".git").exists():
            return parent
    raise RuntimeError("cannot locate workspace root")


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def git_output(repo: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", "-C", str(repo), *args],
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        raise ValueError(completed.stderr.strip() or f"git failed in {repo}")
    return completed.stdout.strip()


def check(config_path: Path) -> list[str]:
    errors: list[str] = []
    root = workspace_root()
    config = load_json(config_path)
    if (
        config.get("experiment_id") != "pi-primary-agent-turn-v1"
        or config.get("question_id") != "PI-T01"
    ):
        errors.append("experiment or question identity differs from the frozen tracer")
    if config.get("stop_conditions") != FROZEN_STOP_CONDITIONS:
        errors.append("stop conditions differ from the frozen contract")

    expected_model = {
        "name": "gpt-5.6-terra",
        "reasoning_effort": "medium",
        "answer_turns": 1,
        "automatic_retries": 0,
        "automatic_repairs": 0,
        "runs_per_arm": 1,
        "additional_replicates": 0,
    }
    if config.get("model") != expected_model:
        errors.append("model contract is not the frozen one-turn Terra-medium contract")

    artifact_sha256 = config.get("artifact_sha256", {})
    prompt = (HERE / str(config.get("prompt_file", ""))).resolve()
    for field in ("prompt_file", "answer_schema", "metrics_schema"):
        path = (HERE / str(config.get(field, ""))).resolve()
        expected_digest = artifact_sha256.get(path.name)
        if (
            not isinstance(expected_digest, str)
            or hashlib.sha256(path.read_bytes()).hexdigest() != expected_digest
        ):
            errors.append(f"{field} does not match its frozen SHA-256")
        if field == "prompt_file":
            continue
        try:
            Draft202012Validator.check_schema(load_json(path))
        except (OSError, ValueError, json.JSONDecodeError) as error:
            errors.append(f"{field} is invalid: {error}")
        except Exception as error:  # jsonschema reports precise schema failures.
            errors.append(f"{field} is not a valid Draft 2020-12 schema: {error}")
    if not prompt.is_file():
        errors.append("tracer prompt is missing")

    subject = config.get("subject", {})
    subject_commit = subject.get("commit")
    if subject_commit != "24bace27cf308c89707cf8005b4795d873e23f17":
        errors.append("Pi commit does not match the frozen revision")

    arms = config.get("arms")
    if not isinstance(arms, list):
        return errors + ["arms must be an array"]
    by_id = {arm.get("id"): arm for arm in arms if isinstance(arm, dict)}
    expected_ids = {
        "source-only",
        "codegraph-assisted",
        "cbm-assisted",
        "graphify-assisted",
    }
    if len(arms) != 4 or set(by_id) != expected_ids:
        errors.append("the protocol must define exactly the four frozen arms")

    order = config.get("order", {})
    seed = order.get("seed")
    if not isinstance(seed, str):
        errors.append("arm-order seed is missing")
    else:
        derived = sorted(
            expected_ids,
            key=lambda arm_id: hashlib.sha256(
                f"{seed}:{arm_id}".encode()
            ).hexdigest(),
        )
        if order.get("arms") != derived:
            errors.append("recorded arm order does not match its SHA-256 rule")

    for arm_id, arm in by_id.items():
        clone = (root / str(arm.get("subject_clone", ""))).resolve()
        expected_clone = (
            root
            / "scratchpad/code-intelligence/subjects/pi"
            / arm_id.removesuffix("-assisted")
        ).resolve()
        if clone != expected_clone:
            errors.append(f"{arm_id}: subject clone does not match its frozen lane")
            continue
        try:
            clone.relative_to((root / "scratchpad/code-intelligence/subjects/pi").resolve())
        except ValueError:
            errors.append(f"{arm_id}: subject clone escapes the Pi scratch root")
            continue
        try:
            if git_output(clone, "rev-parse", "HEAD") != subject_commit:
                errors.append(f"{arm_id}: subject clone is at the wrong commit")
            if git_output(clone, "status", "--porcelain=v1", "--untracked-files=all"):
                errors.append(f"{arm_id}: subject clone is not clean")
            if Path(git_output(clone, "rev-parse", "--show-toplevel")).resolve() != clone:
                errors.append(f"{arm_id}: subject clone is not an independent Git root")
        except ValueError as error:
            errors.append(f"{arm_id}: {error}")

        operations = arm.get("allowed_graph_operations")
        if not isinstance(operations, list) or len(operations) != len(set(operations)):
            errors.append(f"{arm_id}: graph operation list is invalid")
            continue
        if operations != FROZEN_OPERATIONS[arm_id]:
            errors.append(
                f"{arm_id}: graph operation surface does not match the exact frozen list"
            )
        if arm_id == "source-only":
            if arm.get("adapter_policy") is not None or operations:
                errors.append("source-only: graph access must be empty")
            if arm.get("graph_required_before_source") is not False:
                errors.append("source-only: must not require a graph call")
            continue

        if arm.get("graph_required_before_source") is not True:
            errors.append(f"{arm_id}: assigned graph must be called before source access")
        policy_path = (root / str(arm.get("adapter_policy", ""))).resolve()
        try:
            policy = load_json(policy_path)
        except (OSError, ValueError, json.JSONDecodeError) as error:
            errors.append(f"{arm_id}: adapter policy is invalid: {error}")
            continue
        public = set(policy.get("allowed_tool_names", []))
        if not operations or not set(operations).issubset(public):
            errors.append(f"{arm_id}: enabled operations escape the frozen public surface")

    access = config.get("common_access", {})
    required_access = {
        "sandbox": "workspace-write",
        "source_search": True,
        "source_read": True,
        "source_write": False,
        "web": False,
        "git_history": False,
        "reference_answers": False,
        "scoring_anchors": False,
        "other_graph_tools": False,
        "learning_workspace": False,
    }
    if access != required_access:
        errors.append("common access controls differ from the frozen contract")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    args = parser.parse_args()

    try:
        errors = check(args.config.resolve())
    except (OSError, ValueError, json.JSONDecodeError, RuntimeError) as error:
        errors = [str(error)]
    if errors:
        for error in errors:
            print(f"FAIL: {error}", file=sys.stderr)
        return 1
    print("PASS: 4 Pi tracer arms; provider calls: 0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
