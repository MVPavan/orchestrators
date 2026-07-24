#!/usr/bin/env python3
"""Run exactly one frozen Pi tracer arm and record provider usage."""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

import jsonschema


FROZEN_ORDER = (
    "graphify-assisted",
    "source-only",
    "cbm-assisted",
    "codegraph-assisted",
)
HERE = Path(__file__).resolve().parent
MODEL = "gpt-5.6-terra"
EFFORT = "medium"
SUBJECT_COMMIT = "24bace27cf308c89707cf8005b4795d873e23f17"
DISABLED_FEATURES = (
    "apps",
    "browser_use",
    "browser_use_external",
    "browser_use_full_cdp_access",
    "code_mode_host",
    "computer_use",
    "enable_mcp_apps",
    "goals",
    "hooks",
    "image_generation",
    "in_app_browser",
    "memories",
    "multi_agent",
    "plugins",
    "request_permissions_tool",
    "skill_mcp_dependency_install",
    "standalone_web_search",
    "tool_suggest",
    "workspace_dependencies",
)
SOURCE_SEARCH = re.compile(r"(?:^|[;&|]\s*|\s)(?:rg|grep|find|fd)\b")
FILE_READ = re.compile(r"(?:^|[;&|]\s*|\s)(?:cat|sed|head|tail|nl|awk)\b")
WEB_ACCESS = re.compile(r"\b(?:curl|wget)\b|https?://", re.IGNORECASE)
WRITE_ATTEMPT = re.compile(
    r"(?:^|[;&|]\s*|\s)(?:tee|touch|cp|mv|rm|mkdir|install)\b|"
    r"(?:^|[^<])>>?|(?:sed|perl)\s+-i\b"
)
GRAPH_NAMES = {
    "codegraph-assisted": ("cbm", "graphify"),
    "cbm-assisted": ("codegraph", "graphify"),
    "graphify-assisted": ("codegraph", "cbm", "codebase-memory"),
}
ALLOWED_PROVIDER_ENV = {
    "CODEX_HOME",
    "HOME",
    "LANG",
    "LC_ALL",
    "LOGNAME",
    "PATH",
    "SHELL",
    "SSL_CERT_DIR",
    "SSL_CERT_FILE",
    "TERM",
    "TMPDIR",
    "USER",
}


def next_arm(completed: list[str]) -> str | None:
    expected_prefix = list(FROZEN_ORDER[: len(completed)])
    if completed != expected_prefix:
        raise ValueError("completed arms are out of frozen order")
    if len(completed) == len(FROZEN_ORDER):
        return None
    return FROZEN_ORDER[len(completed)]


def build_codex_command(
    *,
    codex: str,
    arm: str,
    subject: Path,
    output: Path,
    events: Path,
    interface_config: Path | None,
    audit_log: Path | None,
) -> list[str]:
    del events  # stdout is captured by the caller.
    command = [
        codex,
        "exec",
        "--ephemeral",
        "--ignore-user-config",
        "--ignore-rules",
        "--strict-config",
        "--sandbox",
        "read-only",
        "--model",
        MODEL,
        "-c",
        f"model_reasoning_effort={json.dumps(EFFORT)}",
        "-c",
        'approval_policy="never"',
        "-c",
        "model_providers.openai.request_max_retries=0",
        "-c",
        "model_providers.openai.stream_max_retries=0",
        "-C",
        str(subject),
        "--output-schema",
        str(HERE / "tracer-answer.schema.json"),
        "--output-last-message",
        str(output),
        "--json",
    ]
    for feature in DISABLED_FEATURES:
        command.extend(["--disable", feature])

    if arm != "source-only":
        if interface_config is None or audit_log is None:
            raise ValueError("assisted arms require one evaluated graph interface")
        interface = HERE.parent / "capabilities/evaluated-interface.py"
        interface_args = [
            str(interface),
            "--config",
            str(interface_config),
            "--audit-log",
            str(audit_log),
        ]
        command.extend(
            [
                "-c",
                f"mcp_servers.evaluated.command={json.dumps(sys.executable)}",
                "-c",
                f"mcp_servers.evaluated.args={json.dumps(interface_args)}",
                "-c",
                "mcp_servers.evaluated.startup_timeout_sec=20",
                "-c",
                "mcp_servers.evaluated.tool_timeout_sec=120",
            ]
        )

    access = (
        "No graph interface is available. Use only read-only source search and "
        "file reads inside the current repository."
        if arm == "source-only"
        else "Your first repository-information operation MUST use the assigned "
        "`evaluated` graph interface. After that, you may use read-only source "
        "search and file reads inside the current repository."
    )
    prompt = (HERE / "tracer-prompt.md").read_text(encoding="utf-8")
    command.append(
        f"{prompt}\n\nAccess contract for this run:\n{access}\n"
        "Do not use the web, Git history, another graph, or any file outside "
        "the current repository. Do not write files or run tests."
    )
    return command


def summarize_events(events: list[dict]) -> dict:
    started = sum(event.get("type") == "turn.started" for event in events)
    completed = [
        event for event in events if event.get("type") == "turn.completed"
    ]
    if started != 1:
        raise ValueError(f"expected exactly one started turn, observed {started}")
    if len(completed) != 1:
        raise ValueError(
            f"expected exactly one completed turn, observed {len(completed)}"
        )
    usage = completed[0].get("usage")
    keys = (
        "input_tokens",
        "cached_input_tokens",
        "output_tokens",
        "reasoning_output_tokens",
    )
    if not isinstance(usage, dict) or any(
        type(usage.get(key)) is not int for key in keys
    ):
        raise ValueError("provider completion event has incomplete token usage")
    return {
        "answer_turns": 1,
        "usage": {key: usage[key] for key in keys},
    }


def classify_operations(events: list[dict], *, arm: str) -> dict:
    positions: dict[str, int] = {}
    ordered: list[dict] = []
    for index, event in enumerate(events):
        item = event.get("item")
        if not isinstance(item, dict):
            continue
        item_id = str(item.get("id") or f"{index}:{item.get('type')}")
        if item_id in positions:
            ordered[positions[item_id]] = item
            continue
        positions[item_id] = len(ordered)
        ordered.append(item)

    graph_seen = False
    graph_calls = 0
    source_searches = 0
    file_reads = 0
    returned_bytes = 0
    contamination = {
        "other_graph_tool_seen": False,
        "reference_or_scoring_anchor_seen": False,
        "web_access_seen": False,
        "live_submodule_access_seen": False,
        "pre_graph_source_access_seen": False,
        "unexpected_write_seen": False,
        "multiple_turns_seen": False,
        "notes": [],
    }
    for item in ordered:
        item_type = item.get("type")
        if item_type in {"mcp_tool_call", "mcp_call"}:
            server = item.get("server") or item.get("server_name")
            if server == "evaluated":
                graph_seen = True
                graph_calls += 1
            else:
                contamination["other_graph_tool_seen"] = True
            continue
        if item_type == "web_search":
            contamination["web_access_seen"] = True
            continue
        if item_type == "file_change":
            contamination["unexpected_write_seen"] = True
            continue
        if item_type != "command_execution":
            continue

        command_value = item.get("command", "")
        command = (
            " ".join(str(part) for part in command_value)
            if isinstance(command_value, list)
            else str(command_value)
        )
        is_search = bool(SOURCE_SEARCH.search(command))
        is_read = bool(FILE_READ.search(command))
        if is_search:
            source_searches += 1
        if is_read:
            file_reads += 1
        if arm != "source-only" and (is_search or is_read) and not graph_seen:
            contamination["pre_graph_source_access_seen"] = True
        if WEB_ACCESS.search(command):
            contamination["web_access_seen"] = True
        if WRITE_ATTEMPT.search(command):
            contamination["unexpected_write_seen"] = True
        if (
            "/external/" in command
            or "external/coding-agents/pi" in command
        ):
            contamination["live_submodule_access_seen"] = True
        if re.search(
            r"reference-ledger|tracer-scoring-key|reference-freeze|docs/research",
            command,
            re.IGNORECASE,
        ):
            contamination["reference_or_scoring_anchor_seen"] = True
        if any(name in command.lower() for name in GRAPH_NAMES.get(arm, ())):
            contamination["other_graph_tool_seen"] = True
        output = item.get("aggregated_output")
        if isinstance(output, str):
            returned_bytes += len(output.encode())

    if arm != "source-only" and graph_calls == 0:
        contamination["notes"].append("assigned graph was never called")
    if arm == "source-only" and graph_calls:
        contamination["other_graph_tool_seen"] = True
    return {
        "operations": {
            "graph_calls": graph_calls,
            "source_searches": source_searches,
            "file_reads": file_reads,
            "returned_bytes": returned_bytes,
            "returned_local_tokens": "UNKNOWN",
        },
        "contamination": contamination,
    }


def build_metrics(
    *,
    run_id: str,
    arm: str,
    elapsed_ms: int,
    event_summary: dict,
    classified: dict,
    result: str,
) -> dict:
    usage = event_summary["usage"]
    contamination = dict(classified["contamination"])
    contamination["multiple_turns_seen"] = event_summary["answer_turns"] != 1
    return {
        "schema_version": "1.0",
        "run_id": run_id,
        "arm": arm,
        "subject_commit": SUBJECT_COMMIT,
        "model": MODEL,
        "reasoning_effort": EFFORT,
        "answer_turns": event_summary["answer_turns"],
        "provider_usage": {
            "input_tokens": usage["input_tokens"],
            "cached_input_tokens": usage["cached_input_tokens"],
            "output_tokens": usage["output_tokens"],
            "reasoning_tokens": usage["reasoning_output_tokens"],
            "measurement_source": "provider_completion_event",
        },
        "operations": classified["operations"],
        "elapsed_ms": elapsed_ms,
        "result": result,
        "contamination": contamination,
    }


def workspace_root() -> Path:
    for parent in HERE.parents:
        if (parent / ".git").exists():
            return parent
    raise RuntimeError("cannot locate workspace root")


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def provider_environment() -> dict[str, str]:
    return {
        name: value
        for name, value in os.environ.items()
        if name in ALLOWED_PROVIDER_ENV
    }


def read_jsonl(path: Path) -> list[dict]:
    events: list[dict] = []
    for number, line in enumerate(path.read_text(errors="replace").splitlines(), 1):
        try:
            event = json.loads(line)
        except json.JSONDecodeError as error:
            raise ValueError(f"{path.name} line {number}: {error}") from error
        if not isinstance(event, dict):
            raise ValueError(f"{path.name} line {number} is not an object")
        events.append(event)
    return events


def git_output(repo: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", "-C", str(repo), *args],
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    if completed.returncode:
        raise ValueError(completed.stderr.strip() or "git command failed")
    return completed.stdout.strip()


def completed_arms(run_root: Path) -> list[str]:
    completed: list[str] = []
    for index, arm in enumerate(FROZEN_ORDER, 1):
        run_dir = run_root / f"{index:02d}-{arm}"
        if not run_dir.exists():
            break
        metrics_path = run_dir / "metrics.json"
        if not metrics_path.is_file():
            raise ValueError(f"prior arm is incomplete; do not retry: {run_dir}")
        metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
        if metrics.get("result") not in {"COMPLETED", "PARTIAL"}:
            raise ValueError(
                f"prior arm stopped the batch with {metrics.get('result')}: {run_dir}"
            )
        completed.append(arm)
    return completed


def policy_path(root: Path, arm: str) -> Path | None:
    if arm == "source-only":
        return None
    if arm == "codegraph-assisted":
        return (
            root
            / "scratchpad/code-intelligence/runtime/lanes/codegraph-probe"
            / "pi-tracer-policy.json"
        )
    lane = arm.removesuffix("-assisted")
    return (
        root
        / "scratchpad/code-intelligence/indexes/pi-tracer-v1"
        / lane
        / "pi-tracer-policy.json"
    )


def validate_request(root: Path, run_root: Path, arm: str) -> tuple[Path, Path | None]:
    completed = completed_arms(run_root)
    expected = next_arm(completed)
    if arm != expected:
        raise ValueError(f"next frozen arm is {expected}, not {arm}")
    lane = arm.removesuffix("-assisted")
    subject = root / "scratchpad/code-intelligence/subjects/pi" / lane
    if git_output(subject, "rev-parse", "HEAD") != SUBJECT_COMMIT:
        raise ValueError(f"{arm}: subject commit drift")
    if git_output(subject, "status", "--porcelain=v1", "--untracked-files=all"):
        raise ValueError(f"{arm}: subject clone is not clean")

    preflight = load_module(HERE / "preflight.py", "pi_tracer_preflight")
    errors = preflight.check(HERE / "tracer-arms.json")
    if errors:
        raise ValueError("; ".join(errors))

    policy = policy_path(root, arm)
    if policy is not None:
        interface = load_module(
            HERE.parent / "capabilities/evaluated-interface.py",
            "pi_tracer_interface",
        )
        config = json.loads(policy.read_text(encoding="utf-8"))
        inspection = interface.validate_config(config)
        if Path(inspection["fixture_root"]).resolve() != subject.resolve():
            raise ValueError(f"{arm}: policy fixture differs from subject clone")
    return subject, policy


def credit_equivalent(usage: dict[str, int]) -> float:
    uncached = usage["input_tokens"] - usage["cached_input_tokens"]
    if uncached < 0:
        raise ValueError("cached input exceeds total input")
    return round(
        (
            uncached * 62.5
            + usage["cached_input_tokens"] * 6.25
            + usage["output_tokens"] * 375.0
        )
        / 1_000_000,
        6,
    )


def write_json(path: Path, value: dict) -> None:
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def run(args: argparse.Namespace) -> int:
    root = workspace_root()
    run_root = args.run_root.resolve()
    subject, policy = validate_request(root, run_root, args.arm)
    if args.preflight_only:
        print(f"PASS: next arm {args.arm}; provider calls: 0")
        return 0

    index = FROZEN_ORDER.index(args.arm) + 1
    run_dir = run_root / f"{index:02d}-{args.arm}"
    run_dir.mkdir(parents=True, exist_ok=False)
    events_path = run_dir / "provider-events.jsonl"
    stderr_path = run_dir / "provider-stderr.txt"
    output_path = run_dir / "answer.json"
    audit_path = run_dir / "evaluated-interface.jsonl" if policy else None
    command = build_codex_command(
        codex=args.codex,
        arm=args.arm,
        subject=subject,
        output=output_path,
        events=events_path,
        interface_config=policy,
        audit_log=audit_path,
    )
    write_json(
        run_dir / "invocation.json",
        {
            "argv": command,
            "cwd": str(subject),
            "arm": args.arm,
            "model": MODEL,
            "reasoning_effort": EFFORT,
            "request_max_retries": 0,
            "stream_max_retries": 0,
        },
    )

    started = time.monotonic()
    with events_path.open("wb") as stdout, stderr_path.open("wb") as stderr:
        completed = subprocess.run(
            command,
            cwd=subject,
            env=provider_environment(),
            stdin=subprocess.DEVNULL,
            stdout=stdout,
            stderr=stderr,
            check=False,
        )
    elapsed_ms = round((time.monotonic() - started) * 1000)
    errors: list[str] = []
    try:
        events = read_jsonl(events_path)
        event_summary = summarize_events(events)
    except (OSError, ValueError) as error:
        errors.append(str(error))
        write_json(
            run_dir / "run-status.json",
            {
                "status": "STOPPED",
                "arm": args.arm,
                "provider_exit_code": completed.returncode,
                "elapsed_ms": elapsed_ms,
                "errors": errors,
                "provider_usage": "UNKNOWN",
            },
        )
        print(json.dumps({"arm": args.arm, "status": "STOPPED", "errors": errors}))
        return 2

    document: dict | None = None
    try:
        document = json.loads(output_path.read_text(encoding="utf-8"))
        schema = json.loads(
            (HERE / "tracer-answer.schema.json").read_text(encoding="utf-8")
        )
        jsonschema.Draft202012Validator(schema).validate(document)
    except (
        OSError,
        json.JSONDecodeError,
        jsonschema.SchemaError,
        jsonschema.ValidationError,
    ) as error:
        errors.append(f"answer validation: {error}")

    classified = classify_operations(events, arm=args.arm)
    if audit_path is not None:
        try:
            audit = read_jsonl(audit_path)
            terminal_calls = [
                record
                for record in audit
                if record.get("record_type") == "call"
                and record.get("phase") == "TERMINAL"
            ]
            event_calls = classified["operations"]["graph_calls"]
            classified["operations"]["graph_calls"] = len(terminal_calls)
            classified["operations"]["returned_bytes"] += sum(
                record.get("output_bytes", 0)
                for record in terminal_calls
                if type(record.get("output_bytes")) is int
            )
            if event_calls != len(terminal_calls):
                classified["contamination"]["notes"].append(
                    "provider MCP events do not match evaluated-interface audit"
                )
        except (OSError, ValueError) as error:
            classified["contamination"]["notes"].append(str(error))

    contamination = classified["contamination"]
    contaminated = bool(contamination["notes"]) or any(
        value is True for key, value in contamination.items() if key != "notes"
    )
    if completed.returncode or errors or document is None:
        result = "PROVIDER_FAILURE"
    elif contaminated:
        result = "CONTAMINATED"
    elif document.get("run_status") == "COMPLETED":
        result = "COMPLETED"
    elif document.get("run_status") == "PARTIAL":
        result = "PARTIAL"
    else:
        result = "PROVIDER_FAILURE"

    metrics = build_metrics(
        run_id=f"pi-t01-{args.arm}",
        arm=args.arm,
        elapsed_ms=elapsed_ms,
        event_summary=event_summary,
        classified=classified,
        result=result,
    )
    metrics_schema = json.loads(
        (HERE / "tracer-metrics.schema.json").read_text(encoding="utf-8")
    )
    jsonschema.Draft202012Validator(metrics_schema).validate(metrics)
    write_json(run_dir / "metrics.json", metrics)

    credit = credit_equivalent(event_summary["usage"])
    status = {
        "status": "VALIDATED"
        if result in {"COMPLETED", "PARTIAL"} and credit <= 12
        else "STOPPED",
        "arm": args.arm,
        "provider_exit_code": completed.returncode,
        "elapsed_ms": elapsed_ms,
        "result": result,
        "provider_usage": metrics["provider_usage"],
        "credit_equivalent": credit,
        "within_credit_limit": credit <= 12,
        "errors": errors,
        "contamination": contamination,
    }
    write_json(run_dir / "run-status.json", status)
    print(json.dumps(status, sort_keys=True))
    return 0 if status["status"] == "VALIDATED" else 3


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--arm", choices=FROZEN_ORDER, required=True)
    parser.add_argument(
        "--run-root",
        type=Path,
        default=workspace_root()
        / "scratchpad/code-intelligence/sessions/pi-tracer-v1/runs",
    )
    parser.add_argument("--codex", default="codex")
    parser.add_argument("--preflight-only", action="store_true")
    args = parser.parse_args()
    try:
        return run(args)
    except (OSError, RuntimeError, ValueError, json.JSONDecodeError) as error:
        print(f"run-tracer-arm: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
