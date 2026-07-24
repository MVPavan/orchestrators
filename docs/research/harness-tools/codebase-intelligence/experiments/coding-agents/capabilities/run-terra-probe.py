#!/usr/bin/env python3
"""Run one isolated Terra-medium capability probe and validate it fail closed."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

import jsonschema


MODEL = "gpt-5.6-terra"
EFFORT = "medium"
MAX_CALLS = 24
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
    "shell_tool",
    "skill_mcp_dependency_install",
    "standalone_web_search",
    "tool_suggest",
    "unified_exec",
    "workspace_dependencies",
)
CONTAMINATING_ITEM_TYPES = {
    "command_execution",
    "file_change",
    "web_search",
    "image_generation",
    "computer_use",
    "collaboration_tool_call",
}
SMOKE_PROMPT = """This is an excluded structured-output setup smoke. Do not use tools,
inspect files, or infer repository facts. Return schema_version 1.0, fixture_id
mixed-ts-rust-capability-v1, run_status PARTIAL, an empty operations array, and
Q01 through Q11 exactly once in order. For every answer use status ABSTAINED,
the answer 'Synthetic setup smoke; no evaluated tool was exposed.', empty
evidence, and uncertainty ['No repository or tool content was provided.'].
Set limitations to ['SMOKE_EXCLUDED: synthetic no-tool provider/schema check.'].
"""
FORBIDDEN_PAYLOAD_MARKERS = (
    "expected-anchors.json",
    "source-only reference",
    "Pi source",
    "Codex source",
)
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


def toml_string(value: str) -> str:
    return json.dumps(value)


def build_codex_command(
    *,
    codex: str,
    fixture: Path,
    provider_schema: Path,
    output: Path,
    interface_config: Path | None,
    audit_log: Path,
    prompt: str,
    smoke: bool,
) -> list[str]:
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
        f"model_reasoning_effort={toml_string(EFFORT)}",
        "-c",
        'approval_policy="never"',
        "-C",
        str(fixture),
        "--output-schema",
        str(provider_schema),
        "--output-last-message",
        str(output),
        "--json",
    ]
    for feature in DISABLED_FEATURES:
        command.extend(["--disable", feature])
    if not smoke:
        if interface_config is None:
            raise ValueError("non-smoke run requires --interface-config")
        interface = Path(__file__).resolve().with_name("evaluated-interface.py")
        interface_args = [
            str(interface),
            "--config",
            str(interface_config.resolve()),
            "--audit-log",
            str(audit_log.resolve()),
        ]
        command.extend(
            [
                "-c",
                f"mcp_servers.evaluated.command={toml_string(sys.executable)}",
                "-c",
                f"mcp_servers.evaluated.args={json.dumps(interface_args)}",
                "-c",
                "mcp_servers.evaluated.startup_timeout_sec=20",
                "-c",
                "mcp_servers.evaluated.tool_timeout_sec=120",
            ]
        )
    command.append(prompt)
    return command


def provider_environment() -> dict[str, str]:
    """Keep normal file-backed Codex auth while excluding credential variables."""
    return {
        name: value
        for name, value in os.environ.items()
        if name in ALLOWED_PROVIDER_ENV
    }


def read_events(events: Path) -> tuple[list[dict[str, Any]], list[str]]:
    parsed: list[dict[str, Any]] = []
    errors: list[str] = []
    if not events.exists():
        return parsed, ["provider JSONL missing"]
    for number, line in enumerate(events.read_text(errors="replace").splitlines(), 1):
        try:
            item = json.loads(line)
        except json.JSONDecodeError as error:
            errors.append(f"provider JSONL line {number} malformed: {error}")
            continue
        if not isinstance(item, dict):
            errors.append(f"provider JSONL line {number} is not an object")
            continue
        parsed.append(item)
    return parsed, errors


def extract_usage(events: list[dict[str, Any]]) -> dict[str, int | str]:
    usage: dict[str, int | str] = {
        "input_tokens": "UNKNOWN",
        "cached_input_tokens": "UNKNOWN",
        "output_tokens": "UNKNOWN",
        "reasoning_output_tokens": "UNKNOWN",
    }
    for event in events:
        if event.get("type") == "turn.completed" and isinstance(
            event.get("usage"), dict
        ):
            for key in usage:
                value = event["usage"].get(key)
                if type(value) is int:
                    usage[key] = value
    return usage


def event_contamination(events: list[dict[str, Any]]) -> list[str]:
    reasons: list[str] = []
    started_turns = sum(event.get("type") == "turn.started" for event in events)
    completed_turns = sum(event.get("type") == "turn.completed" for event in events)
    if started_turns != 1:
        reasons.append(f"expected exactly one started answer turn, observed {started_turns}")
    if completed_turns != 1:
        reasons.append(
            f"expected exactly one completed answer turn, observed {completed_turns}"
        )
    if any(event.get("type") == "turn.failed" for event in events):
        reasons.append("provider answer turn failed")
    for event in events:
        item = event.get("item")
        if isinstance(item, dict) and item.get("type") in CONTAMINATING_ITEM_TYPES:
            reasons.append(f"forbidden provider item type: {item['type']}")
    return reasons


def finalize_run(output: Path, run_dir: Path, capability_dir: Path) -> dict[str, Any]:
    errors: list[str] = []
    try:
        document = json.loads(output.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        document = None
        errors.append(f"final output is not valid JSON: {error}")
    if document is not None:
        for schema_name in (
            "probe-output.provider.schema.json",
            "probe-output.schema.json",
        ):
            try:
                schema = json.loads(
                    (capability_dir / schema_name).read_text(encoding="utf-8")
                )
                jsonschema.Draft202012Validator(schema).validate(document)
            except (
                OSError,
                json.JSONDecodeError,
                jsonschema.SchemaError,
                jsonschema.ValidationError,
            ) as error:
                errors.append(f"{schema_name}: {error}")
        if not errors:
            validator = capability_dir / "validate-probe-output.py"
            checked = subprocess.run(
                [sys.executable, str(validator), str(output)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False,
            )
            if checked.returncode != 0:
                errors.append(
                    checked.stderr.strip() or "canonical invariant check failed"
                )
    result = {
        "status": "VALIDATED" if not errors else "INVALID_FINAL_OUTPUT",
        "errors": errors,
        "document": document,
    }
    (run_dir / "final-validation.json").write_text(
        json.dumps(
            {key: value for key, value in result.items() if key != "document"},
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    return result


def isolated_fixture_errors(fixture: Path) -> list[str]:
    errors: list[str] = []
    if not (fixture / ".git").exists():
        errors.append("fixture is not an isolated Git repository")
    for name in ("AGENTS.md", "CLAUDE.md", ".codex"):
        if (fixture / name).exists():
            errors.append(f"fixture contains forbidden learning overlay: {name}")
    return errors


def interface_config_errors(path: Path, fixture: Path) -> list[str]:
    errors: list[str] = []
    try:
        config = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        return [f"invalid evaluated-interface config: {error}"]
    try:
        configured_cwd = Path(config["cwd"]).resolve()
    except (KeyError, TypeError):
        return ["evaluated-interface config has no valid cwd"]
    if configured_cwd != fixture:
        errors.append("evaluated-interface cwd is not the isolated fixture")
    serialized = json.dumps(config)
    for marker in FORBIDDEN_PAYLOAD_MARKERS:
        if marker.lower() in serialized.lower():
            errors.append(f"evaluated-interface config contains forbidden marker: {marker}")
    return errors


def load_audit(path: Path) -> tuple[list[dict[str, Any]], list[str]]:
    if not path.exists():
        return [], []
    records: list[dict[str, Any]] = []
    errors: list[str] = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        try:
            record = json.loads(line)
        except json.JSONDecodeError as error:
            errors.append(f"evaluated-interface audit line {number} malformed: {error}")
            continue
        if not isinstance(record, dict):
            errors.append(f"evaluated-interface audit line {number} is not an object")
            continue
        records.append(record)
    records.sort(key=lambda item: item.get("sequence", -1))
    sequences = [record.get("sequence") for record in records]
    if sequences != list(range(1, len(records) + 1)):
        errors.append("audit sequences are not unique, contiguous, and ordered from 1")
    return records, errors


def audit_errors(
    records: list[dict[str, Any]], document: dict[str, Any] | None, smoke: bool
) -> tuple[list[str], int, bool]:
    errors: list[str] = []
    dispatched = [
        record for record in records if record.get("status") != "CALL_LIMIT_REJECTED"
    ]
    rejected = [
        record for record in records if record.get("status") == "CALL_LIMIT_REJECTED"
    ]
    if len(dispatched) > MAX_CALLS:
        errors.append(f"more than {MAX_CALLS} evaluated-interface calls were dispatched")
    if rejected:
        errors.append("call limit exceeded; rejected call makes the run invalid")
    if any(record.get("sequence") != MAX_CALLS + 1 for record in rejected):
        errors.append(f"call-limit rejection sequence was not {MAX_CALLS + 1}")
    if smoke and records:
        errors.append("no-tool smoke unexpectedly invoked the evaluated interface")

    operations = document.get("operations") if isinstance(document, dict) else None
    if isinstance(operations, list):
        if len(operations) != len(dispatched):
            errors.append(
                "final operation count does not match dispatched evaluated-interface calls"
            )
        else:
            result_map = {
                "SUCCESS": "SUCCESS",
                "FAILED": "FAILED",
                "UNKNOWN_OPERATION": "FAILED",
                "INVALID_INPUT": "FAILED",
            }
            for operation, record in zip(operations, dispatched):
                if operation.get("sequence") != record.get("sequence"):
                    errors.append("final operation sequence does not match audit")
                    break
                if operation.get("public_operation") != record.get("name"):
                    errors.append("final public operation name does not match audit")
                    break
                expected_result = result_map.get(record.get("status"))
                if expected_result is None or operation.get("result") != expected_result:
                    errors.append("final operation result does not match audit")
                    break
                output_bytes = operation.get("output_bytes")
                if (
                    output_bytes is not None
                    and output_bytes != record.get("output_bytes")
                ):
                    errors.append("final operation output_bytes does not match audit")
                    break
    return errors, len(dispatched), bool(rejected)


def run(args: argparse.Namespace) -> int:
    capability_dir = Path(__file__).resolve().parent
    run_dir = args.run_dir.resolve()
    fixture = args.fixture.resolve()
    run_dir.mkdir(parents=True, exist_ok=False)
    events = run_dir / "provider-events.jsonl"
    stderr = run_dir / "provider-stderr.txt"
    output = run_dir / "final-output.json"
    audit = run_dir / "evaluated-interface.jsonl"
    status_path = run_dir / "run-status.json"
    provider_schema = capability_dir / "probe-output.provider.schema.json"

    preflight_errors = isolated_fixture_errors(fixture)
    if not args.smoke and args.interface_config is not None:
        preflight_errors.extend(
            interface_config_errors(args.interface_config.resolve(), fixture)
        )
    if preflight_errors:
        status_path.write_text(
            json.dumps(
                {"status": "PREFLIGHT_REJECTED", "errors": preflight_errors},
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        return 2

    prompt = (
        SMOKE_PROMPT
        if args.smoke
        else (capability_dir / "probe-prompt.md").read_text(encoding="utf-8")
    )
    command = build_codex_command(
        codex=args.codex,
        fixture=fixture,
        provider_schema=provider_schema,
        output=output,
        interface_config=args.interface_config,
        audit_log=audit,
        prompt=prompt,
        smoke=args.smoke,
    )
    (run_dir / "invocation.json").write_text(
        json.dumps(
            {
                "argv": command,
                "cwd": str(fixture),
                "model": MODEL,
                "effort": EFFORT,
                "classification": "SMOKE_EXCLUDED"
                if args.smoke
                else "CAPABILITY_PROBE",
                "provider_environment_names": sorted(provider_environment()),
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    started = time.monotonic()
    with events.open("wb") as stdout, stderr.open("wb") as error_stream:
        completed = subprocess.run(
            command,
            cwd=fixture,
            env=provider_environment(),
            stdin=subprocess.DEVNULL,
            stdout=stdout,
            stderr=error_stream,
            check=False,
        )
    elapsed_ms = round((time.monotonic() - started) * 1000)

    parsed_events, event_errors = read_events(events)
    contamination = event_contamination(parsed_events)
    validation = finalize_run(output, run_dir, capability_dir)
    records, record_errors = load_audit(audit)
    checked_audit, dispatched_count, call_25_rejected = audit_errors(
        records, validation["document"], args.smoke
    )
    errors = event_errors + record_errors + contamination + validation["errors"]
    errors.extend(checked_audit)
    status = {
        "status": (
            "VALIDATED"
            if completed.returncode == 0 and not errors
            else "BLOCKED_OR_INVALID"
        ),
        "classification": "SMOKE_EXCLUDED"
        if args.smoke
        else "CAPABILITY_PROBE",
        "provider_exit_code": completed.returncode,
        "elapsed_ms": elapsed_ms,
        "model": MODEL,
        "effort": EFFORT,
        "usage": extract_usage(parsed_events),
        "evaluated_calls_dispatched": dispatched_count,
        "call_25_rejected": call_25_rejected,
        "contamination": contamination,
        "errors": errors,
        "config_audit": {
            "ignore_user_config": "--ignore-user-config" in command,
            "ignore_rules": "--ignore-rules" in command,
            "ephemeral": "--ephemeral" in command,
            "sandbox": "read-only",
            "cwd_is_fixture": True,
            "learning_overlay_scan": "clean",
            "unrelated_mcp_count": 0,
            "builtin_tool_features_disabled": list(DISABLED_FEATURES),
            "provider_environment_names": sorted(provider_environment()),
        },
    }
    status_path.write_text(
        json.dumps(status, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return 0 if status["status"] == "VALIDATED" else 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixture", type=Path, required=True)
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--interface-config", type=Path)
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--codex", default="codex")
    args = parser.parse_args()
    if args.smoke and args.interface_config is not None:
        parser.error("--smoke does not accept --interface-config")
    if not args.smoke and args.interface_config is None:
        parser.error("--interface-config is required outside --smoke")
    try:
        return run(args)
    except (OSError, ValueError) as error:
        print(f"run-terra-probe: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
