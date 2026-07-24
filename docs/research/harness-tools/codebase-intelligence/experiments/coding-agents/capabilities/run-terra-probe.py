#!/usr/bin/env python3
"""Run one isolated Terra-medium capability probe and validate it fail closed."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

import jsonschema


MODEL = "gpt-5.6-terra"
EFFORT = "medium"
MAX_CALLS = 24
TOOL_LANES = ("codegraph", "cbm", "graphify")
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
ANCHOR_CONTENT = (
    re.compile(r"expected[\s_.-]*anchors?", re.I),
    re.compile(r"scoring[\s_.-]*key", re.I),
    re.compile(r"reference[\s_.-]*answer", re.I),
    re.compile(r"source[\s_.-]*only[\s_.-]*reference", re.I),
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

HERE = Path(__file__).resolve().parent


def find_workspace_root() -> Path:
    for parent in HERE.parents:
        if (parent / ".git").exists():
            return parent
    raise RuntimeError("cannot locate workspace root")


WORKSPACE_ROOT = find_workspace_root()
APPROVED_ROOT = WORKSPACE_ROOT / "scratchpad" / "code-intelligence"
SESSION_RUN_ROOT = APPROVED_ROOT / "sessions" / "capability-runner"
FROZEN_FIXTURE_ROOT = APPROVED_ROOT / "fixtures"
EXTERNAL_ROOT = WORKSPACE_ROOT / "external"


def is_within(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def load_interface_module():
    path = Path(__file__).resolve().with_name("evaluated-interface.py")
    spec = importlib.util.spec_from_file_location("evaluated_interface_runtime", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load evaluated-interface.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


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


def runtime_version(codex: str) -> str:
    try:
        completed = subprocess.run(
            [codex, "--version"],
            env=provider_environment(),
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
            timeout=10,
        )
    except (OSError, subprocess.TimeoutExpired):
        return "UNKNOWN"
    lines = completed.stdout.strip().splitlines()
    return lines[-1] if completed.returncode == 0 and lines else "UNKNOWN"


def fixture_identity(fixture: Path) -> tuple[dict[str, str], list[str]]:
    errors: list[str] = []
    digest_path = fixture / ".fixture-manifest.digest"
    try:
        digest = digest_path.read_text(encoding="utf-8").strip()
    except OSError as error:
        digest = ""
        errors.append(f"fixture manifest digest unavailable: {error}")
    if not re.fullmatch(r"[0-9a-f]{64}", digest):
        errors.append("fixture manifest digest is not a lowercase SHA-256")
    try:
        completed = subprocess.run(
            ["git", "-C", str(fixture), "rev-parse", "HEAD"],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )
        commit = completed.stdout.strip()
    except OSError as error:
        commit = ""
        errors.append(f"fixture commit unavailable: {error}")
    if not re.fullmatch(r"[0-9a-f]{40}", commit):
        errors.append("fixture source commit is not a 40-character SHA-1")
    return {
        "fixture_manifest_sha256": digest,
        "source_commit": commit,
    }, errors


def tracked_fixture_identity(
    capability_dir: Path,
) -> tuple[dict[str, str], list[str]]:
    errors: list[str] = []
    values: dict[str, str] = {}
    for field, filename, pattern in (
        (
            "fixture_manifest_sha256",
            "fixture-manifest.digest",
            r"[0-9a-f]{64}",
        ),
        ("source_commit", "fixture-commit.sha1", r"[0-9a-f]{40}"),
    ):
        try:
            value = (capability_dir / filename).read_text(encoding="utf-8").strip()
        except OSError as error:
            value = ""
            errors.append(f"tracked fixture identity unavailable: {filename}: {error}")
        if not re.fullmatch(pattern, value):
            errors.append(f"tracked fixture identity is invalid: {filename}")
        values[field] = value
    return values, errors


def target_binding_errors(
    *,
    run_dir: Path,
    fixture: Path,
    tool_lane: str,
    capability_dir: Path,
) -> list[str]:
    """Validate all runner-owned paths and frozen identity before any mutation."""
    errors: list[str] = []
    run_root = SESSION_RUN_ROOT.resolve()
    run_dir = run_dir.resolve()
    fixture = fixture.resolve()
    if run_dir == run_root or not is_within(run_dir, run_root):
        errors.append("run directory is outside the approved capability-runner session root")

    expected_fixture = (FROZEN_FIXTURE_ROOT / tool_lane).resolve()
    if is_within(fixture, EXTERNAL_ROOT.resolve()):
        errors.append("live external submodule fixture paths are prohibited")
    if fixture != expected_fixture:
        errors.append(
            f"fixture does not match declared tool_lane {tool_lane}: "
            f"expected {expected_fixture}"
        )
        return errors

    actual, actual_errors = fixture_identity(fixture)
    tracked, tracked_errors = tracked_fixture_identity(capability_dir)
    errors.extend(actual_errors)
    errors.extend(tracked_errors)
    for field in ("fixture_manifest_sha256", "source_commit"):
        if actual.get(field) != tracked.get(field):
            errors.append(
                f"fixture {field} does not match the tracked frozen identity"
            )
    return errors


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


def build_metrics(
    *,
    run_id: str,
    tool_lane: str,
    classification: str,
    fixture_manifest_sha256: str,
    source_commit: str,
    runtime_version: str,
    usage: dict[str, int | str],
    document: dict[str, Any] | None,
    audit_records: list[dict[str, Any]],
    elapsed_ms: int,
    contamination: dict[str, Any],
    schema_tokens: int | str,
    raw_output_tokens: int | str,
    raw_output_bytes: int | str,
) -> dict[str, Any]:
    evidence_counts = {
        "tool_returned_source": 0,
        "tool_graph_fact": 0,
        "tool_status": 0,
        "documentation_only": 0,
    }
    source_keys = {
        "TOOL_RETURNED_SOURCE": "tool_returned_source",
        "TOOL_GRAPH_FACT": "tool_graph_fact",
        "TOOL_STATUS": "tool_status",
        "DOCUMENTATION_RETURNED_BY_TOOL": "documentation_only",
    }
    if isinstance(document, dict):
        for answer in document.get("answers", []):
            if not isinstance(answer, dict):
                continue
            for evidence in answer.get("evidence", []):
                if not isinstance(evidence, dict):
                    continue
                key = source_keys.get(evidence.get("source"))
                if key is not None:
                    evidence_counts[key] += 1
    dispatched = [
        record
        for record in audit_records
        if record.get("status") != "CALL_LIMIT_REJECTED"
    ]
    return {
        "schema_version": "1.0",
        "run_id": run_id,
        "tool_lane": tool_lane,
        "classification": classification,
        "fixture_manifest_sha256": fixture_manifest_sha256,
        "source_commit": source_commit,
        "model": MODEL,
        "reasoning_effort": EFFORT,
        "runtime_version": runtime_version,
        "provider_usage": {
            "input_tokens": usage["input_tokens"],
            "cached_input_tokens": usage["cached_input_tokens"],
            "output_tokens": usage["output_tokens"],
            "reasoning_tokens": usage["reasoning_output_tokens"],
            "measurement_source": "provider_completion_event",
        },
        "artifact_estimates": {
            "tokenizer": "gpt-tokenizer@3.4.0:o200k_base",
            "schema_tokens": schema_tokens,
            "raw_output_tokens": raw_output_tokens,
            "raw_output_bytes": raw_output_bytes,
        },
        "evidence_counts": evidence_counts,
        "operations": {
            "tool_calls": len(dispatched),
            "file_reads": "UNKNOWN",
            "fallback_searches": 0,
        },
        "elapsed_ms": elapsed_ms,
        "contamination": contamination,
    }


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


def structured_contamination(
    events: list[dict[str, Any]],
    document: dict[str, Any] | None,
    unrelated_mcp_count: int,
    notes: list[str],
    tool_lane: str,
) -> dict[str, Any]:
    serialized = (
        json.dumps(document, ensure_ascii=False).lower()
        if isinstance(document, dict)
        else ""
    )
    expected_anchors_seen = any(pattern.search(serialized) for pattern in ANCHOR_CONTENT)
    subject_repo_seen = bool(
        re.search(r"external[/\\]coding-agents|\bpi source\b|\bcodex source\b", serialized)
    )
    other_tool_patterns = {
        "codegraph": (r"\bcodegraph\b",),
        "cbm": (r"\bcbm\b", r"codebase[\s_.-]*memory"),
        "graphify": (r"\bgraphifyy?\b",),
    }
    cross_tool_output_seen = any(
        re.search(pattern, serialized, re.I)
        for lane, patterns in other_tool_patterns.items()
        if lane != tool_lane
        for pattern in patterns
    ) or any("cross-tool" in note.lower() for note in notes)
    independent_source_access = False
    for event in events:
        item = event.get("item")
        if isinstance(item, dict) and item.get("type") in CONTAMINATING_ITEM_TYPES:
            independent_source_access = True
            break
    return {
        "cross_tool_output_seen": cross_tool_output_seen or unrelated_mcp_count > 0,
        "expected_anchors_seen": expected_anchors_seen
        or any("anchor-like" in note.lower() for note in notes),
        "subject_repo_seen": subject_repo_seen
        or any("subject repo" in note.lower() for note in notes),
        "independent_source_access": independent_source_access,
        "unauthorized_operation": independent_source_access
        or unrelated_mcp_count > 0
        or any(
            marker in note.lower()
            for note in notes
            for marker in ("outside approved", "credential", "url", "path escape")
        ),
        "notes": list(dict.fromkeys(notes)),
    }


def contamination_record_errors(record: dict[str, Any]) -> list[str]:
    return [
        f"structured contamination detected: {name}"
        for name in (
            "cross_tool_output_seen",
            "expected_anchors_seen",
            "subject_repo_seen",
            "independent_source_access",
            "unauthorized_operation",
        )
        if record.get(name) is True
    ]


def mcp_event_errors(
    events: list[dict[str, Any]],
    audit_records: list[dict[str, Any]],
    smoke: bool,
) -> tuple[list[str], list[dict[str, str]], int]:
    errors: list[str] = []
    calls_by_id: dict[str, dict[str, str]] = {}
    order: list[str] = []
    for index, event in enumerate(events):
        item = event.get("item")
        if not isinstance(item, dict) or item.get("type") not in {
            "mcp_tool_call",
            "mcp_call",
        }:
            continue
        call_id = str(item.get("id") or f"event-{index}")
        server = item.get("server") or item.get("server_name") or item.get("mcp_server")
        name = item.get("tool") or item.get("tool_name") or item.get("name")
        if isinstance(name, str) and name.startswith("mcp__"):
            parts = name.split("__", 2)
            if len(parts) == 3:
                server = server or parts[1]
                name = parts[2]
        if not isinstance(server, str) or not isinstance(name, str):
            errors.append("provider MCP event lacks a server or public operation name")
            continue
        if call_id not in calls_by_id:
            order.append(call_id)
        calls_by_id[call_id] = {"server": server, "name": name}
    calls = [calls_by_id[call_id] for call_id in order]
    unrelated = sum(call["server"] != "evaluated" for call in calls)
    for server in sorted(
        {call["server"] for call in calls if call["server"] != "evaluated"}
    ):
        errors.append(f"unrelated MCP server invoked: {server}")
    if smoke and calls:
        errors.append("no-tool smoke emitted MCP tool-call events")
    expected_names = [record.get("name") for record in audit_records]
    evaluated_names = [
        call["name"] for call in calls if call["server"] == "evaluated"
    ]
    if evaluated_names != expected_names:
        errors.append(
            "provider evaluated MCP calls do not match the interface audit"
        )
    return errors, calls, unrelated


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


def isolated_fixture_errors(
    fixture: Path,
    denied_content_sha256: set[str] | None = None,
    ignored_generated_dirs: set[str] | None = None,
) -> list[str]:
    """Scan the actual fixture recursively, independent of leak filenames."""
    errors: list[str] = []
    denied_content_sha256 = denied_content_sha256 or set()
    ignored_generated_dirs = ignored_generated_dirs or set()
    if not (fixture / ".git").exists():
        errors.append("fixture is not an isolated Git repository")
    for name in ("AGENTS.md", "CLAUDE.md", ".codex"):
        if (fixture / name).exists():
            errors.append(f"fixture contains forbidden learning overlay: {name}")
    for path in fixture.rglob("*"):
        relative = path.relative_to(fixture)
        if ".git" in relative.parts:
            continue
        if relative.parts and relative.parts[0] in ignored_generated_dirs:
            continue
        if path.is_symlink():
            try:
                path.resolve().relative_to(fixture)
            except ValueError:
                errors.append(f"fixture symlink escapes isolated root: {path}")
            continue
        if not path.is_file():
            continue
        try:
            content = path.read_bytes()
        except OSError as error:
            errors.append(f"fixture input unreadable: {path}: {error}")
            continue
        digest = hashlib.sha256(content).hexdigest()
        if digest in denied_content_sha256:
            errors.append(f"fixture contains denied content hash: {path}")
        if len(content) > 1024 * 1024:
            continue
        text = content.decode(errors="ignore")
        if any(pattern.search(text) for pattern in ANCHOR_CONTENT):
            errors.append(f"fixture contains anchor-like content: {path}")
        if re.search(
            r"external[/\\]coding-agents|\bpi source\b|\bcodex source\b",
            text,
            re.I,
        ):
            errors.append(f"fixture contains private subject-repo content: {path}")
    return sorted(set(errors))


def interface_config_errors(
    path: Path, fixture: Path, expected_lane: str
) -> list[str]:
    try:
        config = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        return [f"invalid evaluated-interface config: {error}"]
    try:
        inspection = load_interface_module().validate_config(config)
    except (OSError, RuntimeError, ValueError) as error:
        return [f"evaluated-interface policy rejected: {error}"]
    errors: list[str] = []
    if Path(inspection["fixture_root"]).resolve() != fixture.resolve():
        errors.append("evaluated-interface fixture_root is not the isolated fixture")
    scratch_root = Path(inspection["scratch_root"]).resolve()
    try:
        path.resolve().relative_to(scratch_root)
    except ValueError:
        errors.append("evaluated-interface config is outside its scratch_root")
    if inspection["tool_lane"] != expected_lane:
        errors.append(
            "evaluated-interface tool_lane "
            f"{inspection['tool_lane']} does not match requested lane {expected_lane}"
        )
    return errors


def load_startup_record(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            return {}
        return record if isinstance(record, dict) else {}
    return {}


def load_audit(
    path: Path, require_started: bool = False
) -> tuple[list[dict[str, Any]], list[str]]:
    if not path.exists():
        return (
            [],
            ["evaluated-interface audit missing"] if require_started else [],
        )
    journal: list[dict[str, Any]] = []
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
        journal.append(record)
    startup_records = [
        record for record in journal if record.get("record_type") == "interface_started"
    ]
    if require_started:
        if not journal:
            errors.append("evaluated-interface audit is empty")
        elif journal[0].get("record_type") != "interface_started":
            errors.append("first audit record is not interface_started")
        if len(startup_records) != 1:
            errors.append(
                f"evaluated-interface audit has {len(startup_records)} startup records"
            )
    elif startup_records:
        errors.append("smoke audit unexpectedly contains interface startup")
    call_journal = [
        record
        for record in journal
        if record.get("record_type") == "call"
        or (
            "record_type" not in record
            and record.get("sequence") != 0
        )
    ]
    grouped: dict[int, list[dict[str, Any]]] = {}
    for record in call_journal:
        sequence = record.get("sequence")
        if type(sequence) is not int or sequence < 1:
            errors.append("audit record has no valid positive sequence")
            continue
        grouped.setdefault(sequence, []).append(record)
    if sorted(grouped) != list(range(1, len(grouped) + 1)):
        errors.append("audit sequences are not unique, contiguous, and ordered from 1")
    records: list[dict[str, Any]] = []
    for sequence in sorted(grouped):
        entries = grouped[sequence]
        attempts = [
            record
            for record in entries
            if record.get("phase") == "ATTEMPT"
            and record.get("status") == "ATTEMPTED"
        ]
        terminals = [
            record for record in entries if record.get("phase") == "TERMINAL"
        ]
        if len(attempts) != 1:
            errors.append(
                f"audit sequence {sequence} has {len(attempts)} attempt records"
            )
        if len(terminals) > 1:
            errors.append(
                f"audit sequence {sequence} has {len(terminals)} terminal records"
            )
        if terminals:
            records.append(terminals[-1])
            continue
        attempt = attempts[-1] if attempts else entries[-1]
        unresolved = dict(attempt)
        unresolved.update(
            {
                "output_bytes": 0,
                "exit_code": None,
                "status": "FAILED_NO_RESPONSE",
                "phase": "TERMINAL",
            }
        )
        records.append(unresolved)
        errors.append(f"audit sequence {sequence} received no terminal response")
    return records, errors


def audit_startup_errors(
    startup: dict[str, Any],
    config: dict[str, Any],
    fixture: Path,
    expected_lane: str,
) -> list[str]:
    errors: list[str] = []
    if not startup:
        return ["evaluated-interface startup attestation missing"]
    if startup.get("policy_digest") != config.get("policy_digest"):
        errors.append("audit policy digest does not match active interface config")
    if startup.get("tool_lane") != expected_lane:
        errors.append("audit tool lane does not match requested lane")
    if Path(startup.get("fixture_root", "/")).resolve() != fixture.resolve():
        errors.append("audit fixture root does not match isolated fixture")
    if startup.get("active_mcp_count") != 1:
        errors.append("audit active MCP count is not exactly one")
    if startup.get("expected_surface") != startup.get("observed_surface"):
        errors.append("audit expected and observed MCP surfaces differ")
    if startup.get("expected_surface_digests") != startup.get(
        "observed_surface_digests"
    ):
        errors.append("audit expected and observed full MCP surface digests differ")
    exposed = startup.get("exposed_surface", {})
    if sorted(exposed.get("tools", [])) != sorted(
        config.get("allowed_tool_names", [])
    ):
        errors.append("audit exposed tool surface does not match policy")
    if (
        exposed.get("resources")
        or exposed.get("resource_templates")
        or exposed.get("prompts")
        or exposed.get("instructions_sha256") is not None
    ):
        errors.append("audit exposed a prohibited non-tool MCP surface")
    if startup.get("contamination_reasons"):
        errors.append("audit startup reports contaminated active configuration")
    return errors


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
    if any(record.get("status") == "FAILED_NO_RESPONSE" for record in dispatched):
        errors.append("evaluated-interface call completed without a response")
    if any(record.get("status") == "POLICY_REJECTED" for record in dispatched):
        errors.append("evaluated-interface policy rejected an attempted operation")
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
                "POLICY_REJECTED": "FAILED",
                "FAILED_NO_RESPONSE": "FAILED",
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


def derive_config_audit(
    *,
    command: list[str],
    fixture_errors: list[str],
    startup: dict[str, Any],
    provider_environment: dict[str, str],
) -> dict[str, Any]:
    """Report only facts derived from the active argv, scan, and startup journal."""
    disabled = [
        command[index + 1]
        for index, item in enumerate(command[:-1])
        if item == "--disable"
    ]
    config_values = [
        command[index + 1]
        for index, item in enumerate(command[:-1])
        if item == "-c"
    ]
    servers = {
        match.group(1)
        for value in config_values
        if (match := re.match(r"mcp_servers\.([^.]+)\.", value))
    }
    sandbox = None
    cwd = None
    if "--sandbox" in command:
        sandbox = command[command.index("--sandbox") + 1]
    if "-C" in command:
        cwd = command[command.index("-C") + 1]
    observed = startup.get("observed_surface", {}) if startup else {}
    exposed = startup.get("exposed_surface", {}) if startup else {}
    return {
        "ignore_user_config": "--ignore-user-config" in command,
        "ignore_rules": "--ignore-rules" in command,
        "ephemeral": "--ephemeral" in command,
        "sandbox": sandbox,
        "configured_cwd": cwd,
        "learning_overlay_scan": "clean" if not fixture_errors else "contaminated",
        "learning_overlay_findings": fixture_errors,
        "active_mcp_count": startup.get("active_mcp_count", len(servers))
        if startup
        else len(servers),
        "configured_mcp_servers": sorted(servers),
        "observed_tools": observed.get("tools", []),
        "observed_resources": observed.get("resources", []),
        "observed_resource_templates": observed.get("resource_templates", []),
        "observed_prompts": observed.get("prompts", []),
        "observed_capabilities": observed.get("capabilities", []),
        "observed_instructions_sha256": observed.get("instructions_sha256"),
        "exposed_tools": exposed.get("tools", []),
        "exposed_resources": exposed.get("resources", []),
        "exposed_resource_templates": exposed.get("resource_templates", []),
        "exposed_prompts": exposed.get("prompts", []),
        "exposed_instructions_sha256": exposed.get("instructions_sha256"),
        "startup_contamination_reasons": startup.get(
            "contamination_reasons", []
        )
        if startup
        else [],
        "builtin_tool_features_disabled": disabled,
        "provider_environment_names": sorted(provider_environment),
    }


def run(args: argparse.Namespace) -> int:
    capability_dir = Path(__file__).resolve().parent
    run_dir = args.run_dir.resolve()
    fixture = args.fixture.resolve()
    interface_config: dict[str, Any] = {}
    denied_hashes: set[str] = set()
    if not args.smoke and args.interface_config is not None:
        try:
            interface_config = json.loads(
                args.interface_config.read_text(encoding="utf-8")
            )
            denied_hashes = set(
                interface_config.get("denied_content_sha256", [])
            )
        except (OSError, json.JSONDecodeError) as error:
            interface_config = {}
            pre_config_error = f"invalid evaluated-interface config: {error}"
        else:
            pre_config_error = ""
    else:
        pre_config_error = ""
    preflight_errors = target_binding_errors(
        run_dir=run_dir,
        fixture=fixture,
        tool_lane=args.tool_lane,
        capability_dir=capability_dir,
    )
    fixture_scan_errors = (
        isolated_fixture_errors(
            fixture,
            denied_hashes,
            {
                interface_config.get("environment", {}).get("CODEGRAPH_DIR", "")
            }
            if args.tool_lane == "codegraph" and interface_config
            else set(),
        )
        if not preflight_errors
        else []
    )
    preflight_errors.extend(fixture_scan_errors)
    if pre_config_error:
        preflight_errors.append(pre_config_error)
    if not args.smoke and args.interface_config is not None:
        preflight_errors.extend(
            interface_config_errors(
                args.interface_config.resolve(), fixture, args.tool_lane
            )
        )
        if interface_config:
            try:
                run_dir.relative_to(
                    Path(interface_config["scratch_root"]).resolve()
                )
            except (KeyError, TypeError, ValueError):
                preflight_errors.append(
                    "real run directory is outside interface scratch_root"
                )
    if preflight_errors:
        print(
            "run-terra-probe: preflight rejected: "
            + "; ".join(dict.fromkeys(preflight_errors)),
            file=sys.stderr,
        )
        return 2
    identity, identity_errors = fixture_identity(fixture)
    if identity_errors:
        raise ValueError("; ".join(identity_errors))

    run_dir.mkdir(parents=True, exist_ok=False)
    events = run_dir / "provider-events.jsonl"
    stderr = run_dir / "provider-stderr.txt"
    output = run_dir / "final-output.json"
    audit = run_dir / "evaluated-interface.jsonl"
    status_path = run_dir / "run-status.json"
    metrics_path = run_dir / "metrics.json"
    provider_schema = capability_dir / "probe-output.provider.schema.json"

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
                "tool_lane": args.tool_lane,
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
    validation = finalize_run(output, run_dir, capability_dir)
    records, record_errors = load_audit(audit, require_started=not args.smoke)
    startup = load_startup_record(audit) if not args.smoke else {}
    startup_errors = (
        audit_startup_errors(
            startup, interface_config, fixture, args.tool_lane
        )
        if not args.smoke
        else []
    )
    mcp_errors, mcp_calls, unrelated_mcp_count = mcp_event_errors(
        parsed_events, records, args.smoke
    )
    contamination = (
        event_contamination(parsed_events)
        + mcp_errors
        + list(startup.get("contamination_reasons", []))
        + fixture_scan_errors
    )
    checked_audit, dispatched_count, call_25_rejected = audit_errors(
        records, validation["document"], args.smoke
    )
    errors = (
        event_errors
        + record_errors
        + startup_errors
        + contamination
        + validation["errors"]
    )
    errors.extend(checked_audit)
    contamination_record = structured_contamination(
        parsed_events,
        validation["document"],
        unrelated_mcp_count,
        contamination,
        args.tool_lane,
    )
    structured_errors = contamination_record_errors(contamination_record)
    contamination.extend(structured_errors)
    errors.extend(structured_errors)
    contamination_record["notes"] = list(dict.fromkeys(contamination))
    usage = extract_usage(parsed_events)
    classification = "SMOKE_EXCLUDED" if args.smoke else "CAPABILITY_PROBE"
    raw_output_bytes: int | str = (
        output.stat().st_size if output.exists() else "UNKNOWN"
    )
    metrics = build_metrics(
        run_id=args.run_id or run_dir.name,
        tool_lane=args.tool_lane,
        classification=classification,
        fixture_manifest_sha256=identity["fixture_manifest_sha256"],
        source_commit=identity["source_commit"],
        runtime_version=runtime_version(args.codex),
        usage=usage,
        document=validation["document"],
        audit_records=records,
        elapsed_ms=elapsed_ms,
        contamination=contamination_record,
        schema_tokens="UNKNOWN",
        raw_output_tokens="UNKNOWN",
        raw_output_bytes=raw_output_bytes,
    )
    metrics_path.write_text(
        json.dumps(metrics, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    try:
        metrics_schema = json.loads(
            (capability_dir / "metrics.schema.json").read_text(encoding="utf-8")
        )
        jsonschema.Draft202012Validator(metrics_schema).validate(metrics)
    except (
        OSError,
        json.JSONDecodeError,
        jsonschema.SchemaError,
        jsonschema.ValidationError,
    ) as error:
        errors.append(f"metrics.schema.json: {error}")
    status = {
        "status": (
            "VALIDATED"
            if completed.returncode == 0 and not errors
            else "BLOCKED_OR_INVALID"
        ),
        "classification": classification,
        "provider_exit_code": completed.returncode,
        "elapsed_ms": elapsed_ms,
        "model": MODEL,
        "effort": EFFORT,
        "usage": usage,
        "evaluated_calls_dispatched": dispatched_count,
        "call_25_rejected": call_25_rejected,
        "contamination": contamination,
        "errors": errors,
        "config_audit": {
            **derive_config_audit(
                command=command,
                fixture_errors=fixture_scan_errors,
                startup=startup,
                provider_environment=provider_environment(),
            ),
            "unrelated_mcp_count": unrelated_mcp_count,
            "observed_mcp_calls": mcp_calls,
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
    parser.add_argument("--tool-lane", choices=TOOL_LANES, required=True)
    parser.add_argument("--run-id")
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
