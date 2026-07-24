#!/usr/bin/env python3
"""Fail-closed, policy-sealed interface for one evaluated code-graph lane."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import select
import subprocess
import sys
import threading
from pathlib import Path
from typing import Any


MAX_CALLS = 24
CLI_OPERATION_TIMEOUT_SECONDS = 120
TOOL_LANES = ("codegraph", "cbm", "graphify")
TOKEN = re.compile(r"^\{([A-Za-z_][A-Za-z0-9_]*)\}$")
URL = re.compile(r"(?:https?|ssh|git|ftp)://", re.IGNORECASE)
COMMAND_FRAGMENT = re.compile(r"(?:^|[\s;&|`])(?:curl|wget|git|sh|bash)\b", re.I)
FORBIDDEN_ENV_MARKERS = ("KEY", "TOKEN", "SECRET", "PASSWORD", "CREDENTIAL")
ALLOWED_ENV_NAMES = {"PATH", "HOME", "TMPDIR", "LANG", "LC_ALL"}
LANE_ENV_NAMES = {
    "codegraph": {"CODEGRAPH_DIR", "CODEGRAPH_NO_DAEMON", "CODEGRAPH_NO_WATCH"},
    "cbm": {"CBM_CACHE_DIR", "CBM_LOG_LEVEL", "CBM_WORKERS"},
    "graphify": {"GRAPHIFY_OUT"},
}
FORBIDDEN_EXECUTABLES = {
    "sh",
    "bash",
    "dash",
    "zsh",
    "fish",
    "curl",
    "wget",
    "git",
    "ssh",
    "scp",
    "nc",
    "ncat",
    "socat",
    "tee",
    "cp",
    "mv",
    "rm",
    "install",
    "make",
    "powershell",
    "pwsh",
}
ALLOWED_MCP_METHODS = {
    "initialize",
    "notifications/initialized",
    "ping",
    "tools/list",
    "tools/call",
}
ANCHOR_PATTERNS = (
    re.compile(r"expected[\s_.-]*anchors?", re.I),
    re.compile(r"scoring[\s_.-]*key", re.I),
    re.compile(r"reference[\s_.-]*answer", re.I),
    re.compile(r"source[\s_.-]*only[\s_.-]*reference", re.I),
)
LANE_MARKERS = {
    "codegraph": (re.compile(r"\bcodegraph\b", re.I),),
    "cbm": (
        re.compile(r"\bcbm\b", re.I),
        re.compile(r"codebase[\s_.-]*memory", re.I),
    ),
    "graphify": (re.compile(r"\bgraphifyy?\b", re.I),),
}


def find_workspace_root() -> Path:
    for parent in Path(__file__).resolve().parents:
        if (parent / ".git").exists():
            return parent
    raise RuntimeError("cannot locate workspace root")


WORKSPACE_ROOT = find_workspace_root()
APPROVED_ROOT = WORKSPACE_ROOT / "scratchpad" / "code-intelligence"
EXTERNAL_ROOT = WORKSPACE_ROOT / "external"


def compact(value: Any) -> bytes:
    return json.dumps(
        value, separators=(",", ":"), sort_keys=True, ensure_ascii=False
    ).encode()


def append_jsonl(path: Path, record: dict[str, Any]) -> None:
    with path.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(record, sort_keys=True, ensure_ascii=False) + "\n")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def policy_digest(config: dict[str, Any]) -> str:
    payload = {key: value for key, value in config.items() if key != "policy_digest"}
    return hashlib.sha256(compact(payload)).hexdigest()


def seal_policy(config: dict[str, Any]) -> dict[str, Any]:
    sealed = json.loads(json.dumps(config))
    sealed.pop("policy_digest", None)
    sealed["policy_digest"] = policy_digest(sealed)
    return sealed


def is_within(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def normalized_path(value: str) -> Path:
    path = Path(value)
    if not path.is_absolute():
        raise ValueError(f"path must be absolute: {value}")
    return path.resolve()


def iter_values(value: Any, prefix: str = "config"):
    if isinstance(value, dict):
        for key, child in value.items():
            yield from iter_values(child, f"{prefix}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from iter_values(child, f"{prefix}[{index}]")
    elif isinstance(value, str):
        yield prefix, value


def path_allowed(path: Path, fixture_root: Path, scratch_root: Path) -> bool:
    return is_within(path, fixture_root) or is_within(path, scratch_root)


def inspect_policy_content(
    config: dict[str, Any], fixture_root: Path, scratch_root: Path
) -> list[str]:
    """Derive contamination from actual policy strings and referenced files."""
    lane = config["tool_lane"]
    denied_hashes = set(config.get("denied_content_sha256", []))
    reasons: list[str] = []
    for location, value in iter_values(config):
        if location.endswith("policy_digest") or "denied_content_sha256" in location:
            continue
        if URL.search(value):
            reasons.append(f"URL in active policy at {location}")
        if any(pattern.search(value) for pattern in ANCHOR_PATTERNS):
            reasons.append(f"anchor-like content in active policy at {location}")
        for other_lane, patterns in LANE_MARKERS.items():
            if other_lane != lane and any(pattern.search(value) for pattern in patterns):
                reasons.append(
                    f"cross-tool marker for {other_lane} in active policy at {location}"
                )
        if value.startswith("/"):
            path = Path(value).resolve()
            if not path_allowed(path, fixture_root, scratch_root):
                reasons.append(f"path outside approved roots at {location}: {path}")
            elif path.is_file() and sha256_file(path) in denied_hashes:
                reasons.append(f"denied content hash referenced at {location}")
    return sorted(set(reasons))


def validate_environment(
    environment: Any, fixture_root: Path, scratch_root: Path, lane: str
) -> None:
    if not isinstance(environment, dict):
        raise ValueError("environment must be an object")
    for name, value in environment.items():
        if not isinstance(name, str) or not isinstance(value, str):
            raise ValueError("environment names and values must be strings")
        if name not in ALLOWED_ENV_NAMES | LANE_ENV_NAMES[lane]:
            if any(marker in name.upper() for marker in FORBIDDEN_ENV_MARKERS):
                raise ValueError(f"credential-like environment variable rejected: {name}")
            raise ValueError(f"environment variable is not allowlisted: {name}")
        if URL.search(value):
            raise ValueError(f"URL rejected in environment variable {name}")
        if name in {
            "HOME",
            "TMPDIR",
            "CBM_CACHE_DIR",
            "GRAPHIFY_OUT",
            "CODEGRAPH_DIR",
        }:
            path = normalized_path(value)
            if not is_within(path, scratch_root):
                raise ValueError(f"{name} must be inside scratch_root")
        if name == "PATH":
            for part in value.split(os.pathsep):
                if not part:
                    raise ValueError("PATH contains an empty entry")
                path = normalized_path(part)
                if not is_within(path, scratch_root):
                    raise ValueError("PATH entries must be inside scratch_root")
        if name in {"CODEGRAPH_NO_DAEMON", "CODEGRAPH_NO_WATCH"} and value != "1":
            raise ValueError(f"{name} must be fixed to 1")
        if name == "CBM_LOG_LEVEL" and value not in {"none", "error", "warn", "info"}:
            raise ValueError("CBM_LOG_LEVEL is outside the safe allowlist")
        if name == "CBM_WORKERS" and (
            not value.isdigit() or not 1 <= int(value) <= 16
        ):
            raise ValueError("CBM_WORKERS must be between 1 and 16")


def validate_executable(config: dict[str, Any], scratch_root: Path) -> Path:
    executable = config.get("executable")
    if not isinstance(executable, dict):
        raise ValueError("executable must be an object")
    realpath = executable.get("realpath")
    expected_hash = executable.get("sha256")
    if not isinstance(realpath, str) or not isinstance(expected_hash, str):
        raise ValueError("executable requires realpath and sha256")
    path = normalized_path(realpath)
    if path.name.lower() in FORBIDDEN_EXECUTABLES:
        raise ValueError(f"forbidden executable: {path.name}")
    if not is_within(path, scratch_root):
        raise ValueError("executable path outside approved scratch root")
    if not path.is_file() or not os.access(path, os.X_OK):
        raise ValueError("executable realpath is not an executable file")
    if sha256_file(path) != expected_hash:
        raise ValueError("executable sha256 mismatch")
    first_line = path.read_bytes().splitlines()[:1]
    if first_line and first_line[0].startswith(b"#!"):
        shebang = first_line[0][2:].decode(errors="ignore").split()
        interpreter = Path(shebang[0]).name.lower()
        if interpreter == "env" and len(shebang) > 1:
            interpreter = Path(shebang[1]).name.lower()
        if interpreter in FORBIDDEN_EXECUTABLES:
            raise ValueError(f"forbidden executable interpreter: {interpreter}")
    return path


def validate_command_template(
    command: Any,
    executable: Path,
    fixture_root: Path,
    scratch_root: Path,
    label: str,
) -> list[str]:
    if not isinstance(command, list):
        raise ValueError(f"{label} must be a list, not a command string")
    if not command or not all(isinstance(part, str) for part in command):
        raise ValueError(f"{label} must be a non-empty string list")
    if Path(command[0]).resolve() != executable:
        raise ValueError(f"{label} executable does not match sealed realpath")
    for part in command[1:]:
        if part == "-c":
            raise ValueError(f"{label} rejects interpreter -c")
        if URL.search(part):
            raise ValueError(f"URL rejected in {label}")
        if part.startswith("/"):
            path = Path(part).resolve()
            if not path_allowed(path, fixture_root, scratch_root):
                raise ValueError(f"path outside approved roots in {label}: {path}")
        elif ".." in Path(part).parts:
            raise ValueError(f"path escape rejected in {label}")
    return command


def validate_surface(surface: Any) -> dict[str, Any]:
    if not isinstance(surface, dict):
        raise ValueError("expected_surface must be an object")
    result: dict[str, Any] = {}
    for key in (
        "tools",
        "resources",
        "resource_templates",
        "prompts",
        "capabilities",
    ):
        value = surface.get(key)
        if (
            not isinstance(value, list)
            or not all(isinstance(item, str) and item for item in value)
            or len(value) != len(set(value))
        ):
            raise ValueError(f"expected_surface.{key} must be a unique string list")
        result[key] = sorted(value)
    instructions = surface.get("instructions_sha256")
    if instructions is not None and not re.fullmatch(r"[0-9a-f]{64}", instructions):
        raise ValueError("expected_surface.instructions_sha256 must be null or SHA-256")
    result["instructions_sha256"] = instructions
    return result


SURFACE_DIGEST_KEYS = (
    "initialize",
    "tools",
    "resources",
    "resource_templates",
    "prompts",
)


def validate_surface_digests(value: Any) -> dict[str, str]:
    if not isinstance(value, dict) or set(value) != set(SURFACE_DIGEST_KEYS):
        raise ValueError(
            "expected_surface_digests must cover initialize, tools, resources, "
            "resource_templates, and prompts"
        )
    if not all(
        isinstance(value[key], str)
        and re.fullmatch(r"[0-9a-f]{64}", value[key])
        for key in SURFACE_DIGEST_KEYS
    ):
        raise ValueError("expected_surface_digests values must be SHA-256 strings")
    return {key: value[key] for key in SURFACE_DIGEST_KEYS}


def canonical_surface_digest(value: Any) -> str:
    return hashlib.sha256(compact(value)).hexdigest()


def canonical_surface_objects(
    initialize: dict[str, Any],
    tools: list[dict[str, Any]],
    resources: list[dict[str, Any]],
    resource_templates: list[dict[str, Any]],
    prompts: list[dict[str, Any]],
) -> dict[str, Any]:
    """Retain full objects while normalizing only list ordering by identity."""

    def ordered(items: list[dict[str, Any]], identity: str) -> list[dict[str, Any]]:
        if not all(
            isinstance(item, dict) and isinstance(item.get(identity), str)
            for item in items
        ):
            raise ValueError(f"MCP surface object lacks string {identity}")
        return sorted(items, key=lambda item: item[identity])

    return {
        "initialize": initialize,
        "tools": ordered(tools, "name"),
        "resources": ordered(resources, "uri"),
        "resource_templates": ordered(resource_templates, "uriTemplate"),
        "prompts": ordered(prompts, "name"),
    }


def surface_digests(objects: dict[str, Any]) -> dict[str, str]:
    return {
        key: canonical_surface_digest(objects[key]) for key in SURFACE_DIGEST_KEYS
    }


def validate_config(config: dict[str, Any]) -> dict[str, Any]:
    allowed_keys = {
        "policy_version",
        "policy_digest",
        "tool_lane",
        "mode",
        "fixture_root",
        "scratch_root",
        "cwd",
        "environment",
        "executable",
        "command_template",
        "public_operations",
        "expected_surface",
        "expected_surface_digests",
        "allowed_tool_names",
        "allowed_mcp_methods",
        "denied_content_sha256",
    }
    unexpected_keys = set(config) - allowed_keys
    if unexpected_keys:
        raise ValueError(
            f"unsupported policy fields: {', '.join(sorted(unexpected_keys))}"
        )
    if config.get("policy_version") != "1.0":
        raise ValueError("policy_version must be 1.0")
    if config.get("policy_digest") != policy_digest(config):
        raise ValueError("policy_digest does not match active policy")
    if config.get("mode") not in {"cli", "native_mcp"}:
        raise ValueError("mode must be cli or native_mcp")
    lane = config.get("tool_lane")
    if lane not in TOOL_LANES:
        raise ValueError(f"tool_lane must be one of {', '.join(TOOL_LANES)}")

    fixture_root = normalized_path(config.get("fixture_root", ""))
    scratch_root = normalized_path(config.get("scratch_root", ""))
    cwd = normalized_path(config.get("cwd", ""))
    approved = APPROVED_ROOT.resolve()
    if not is_within(fixture_root, approved):
        raise ValueError("fixture_root is outside approved disposable root")
    if not is_within(scratch_root, approved):
        raise ValueError("scratch_root is outside approved disposable root")
    if scratch_root == approved or not any(
        pattern.search(str(scratch_root)) for pattern in LANE_MARKERS[lane]
    ):
        raise ValueError("scratch_root is not tool-lane-specific")
    if not any(pattern.search(str(fixture_root)) for pattern in LANE_MARKERS[lane]):
        raise ValueError("fixture_root is not assigned to the tool lane")
    if fixture_root == scratch_root or is_within(fixture_root, scratch_root):
        raise ValueError("fixture_root and scratch_root must be disjoint")
    if cwd != fixture_root:
        raise ValueError("cwd must exactly equal fixture_root")
    if is_within(fixture_root, EXTERNAL_ROOT.resolve()):
        raise ValueError("live external submodule paths are prohibited")

    validate_environment(
        config.get("environment", {}), fixture_root, scratch_root, lane
    )
    executable = validate_executable(config, scratch_root)
    validate_command_template(
        config.get("command_template"),
        executable,
        fixture_root,
        scratch_root,
        "command_template",
    )
    expected_surface = validate_surface(config.get("expected_surface"))
    expected_surface_digests = validate_surface_digests(
        config.get("expected_surface_digests")
    )
    allowed_tools = config.get("allowed_tool_names")
    if (
        not isinstance(allowed_tools, list)
        or not all(isinstance(name, str) and name for name in allowed_tools)
        or len(allowed_tools) != len(set(allowed_tools))
        or not set(allowed_tools).issubset(expected_surface["tools"])
    ):
        raise ValueError("allowed_tool_names must be a unique expected-tool subset")
    allowed_methods = config.get("allowed_mcp_methods")
    if (
        not isinstance(allowed_methods, list)
        or set(allowed_methods) - ALLOWED_MCP_METHODS
        or len(allowed_methods) != len(set(allowed_methods))
    ):
        raise ValueError("allowed_mcp_methods contains an unsupported method")
    if set(allowed_methods) != ALLOWED_MCP_METHODS:
        raise ValueError("allowed_mcp_methods must match the fixed safe MCP set")

    denied_hashes = config.get("denied_content_sha256")
    if (
        not isinstance(denied_hashes, list)
        or not all(re.fullmatch(r"[0-9a-f]{64}", value) for value in denied_hashes)
    ):
        raise ValueError("denied_content_sha256 must contain SHA-256 strings")

    if config["mode"] == "cli":
        operations = config.get("public_operations")
        if not isinstance(operations, list) or not operations:
            raise ValueError("CLI mode requires public_operations")
        names: set[str] = set()
        for operation in operations:
            if not isinstance(operation, dict):
                raise ValueError("each public operation must be an object")
            name = operation.get("name")
            if not isinstance(name, str) or not name or name in names:
                raise ValueError("public operation names must be unique strings")
            names.add(name)
            if not isinstance(operation.get("description"), str):
                raise ValueError(f"{name}: description must be a string")
            schema = operation.get("input_schema")
            if not isinstance(schema, dict) or schema.get("type") != "object":
                raise ValueError(f"{name}: input_schema must be an object schema")
            argument_policy = operation.get("argument_policy")
            if not isinstance(argument_policy, dict):
                raise ValueError(f"{name}: argument_policy must be an object")
            properties = schema.get("properties", {})
            if set(argument_policy) != set(properties):
                raise ValueError(f"{name}: argument_policy must cover every input")
            for argument, rule in argument_policy.items():
                if not isinstance(rule, dict) or rule.get("kind") not in {"text", "path"}:
                    raise ValueError(f"{name}.{argument}: invalid argument policy")
                if rule["kind"] == "path" and rule.get("root") not in {
                    "fixture",
                    "scratch",
                }:
                    raise ValueError(f"{name}.{argument}: path root is required")
            template = validate_command_template(
                operation.get("argv_template"),
                executable,
                fixture_root,
                scratch_root,
                f"{name}.argv_template",
            )
            if len(template) < 2 or TOKEN.fullmatch(template[1]):
                raise ValueError(f"{name}: public subcommand must be fixed")
            placeholders = {
                match.group(1)
                for part in template
                if (match := TOKEN.fullmatch(part)) is not None
            }
            if placeholders != set(argument_policy):
                raise ValueError(f"{name}: argv placeholders must match arguments")
        if sorted(names) != sorted(allowed_tools):
            raise ValueError("CLI operation names do not match allowed tool names")
        if sorted(allowed_tools) != expected_surface["tools"]:
            raise ValueError("CLI expected surface may not contain hidden tools")
        if (
            expected_surface["resources"]
            or expected_surface["resource_templates"]
            or expected_surface["prompts"]
        ):
            raise ValueError("CLI adapter cannot expose resources or prompts")
        if expected_surface["instructions_sha256"] is not None:
            raise ValueError("CLI adapter cannot expose server instructions")
    elif config.get("public_operations"):
        raise ValueError("native MCP policy cannot define CLI public_operations")

    reasons = inspect_policy_content(config, fixture_root, scratch_root)
    if reasons:
        raise ValueError("; ".join(reasons))
    return {
        "tool_lane": lane,
        "mode": config["mode"],
        "fixture_root": str(fixture_root),
        "scratch_root": str(scratch_root),
        "executable_realpath": str(executable),
        "policy_digest": config["policy_digest"],
        "expected_surface": expected_surface,
        "expected_surface_digests": expected_surface_digests,
        "contamination_reasons": reasons,
    }


def safe_text(value: Any, argument: str) -> str:
    if not isinstance(value, (str, int, float, bool)):
        raise ValueError(f"argument {argument} must be a scalar")
    text = str(value)
    if "\x00" in text or "\n" in text or "\r" in text:
        raise ValueError(f"argument {argument} contains control characters")
    if URL.search(text) or COMMAND_FRAGMENT.search(text):
        raise ValueError(f"argument {argument} contains a command or URL")
    if text.startswith("/") or ".." in Path(text).parts:
        raise ValueError(f"argument {argument} contains a path escape")
    return text


def expand_argument(
    part: str,
    arguments: dict[str, Any],
    argument_policy: dict[str, Any],
    fixture_root: Path,
    scratch_root: Path,
) -> str:
    match = TOKEN.fullmatch(part)
    if not match:
        return part
    name = match.group(1)
    rule = argument_policy[name]
    value = arguments.get(name)
    if rule["kind"] == "text":
        return safe_text(value, name)
    if not isinstance(value, str):
        raise ValueError(f"argument {name} must be a path string")
    if Path(value).is_absolute() or ".." in Path(value).parts:
        raise ValueError(f"argument {name} contains a path escape")
    root = fixture_root if rule["root"] == "fixture" else scratch_root
    resolved = (root / value).resolve()
    if not is_within(resolved, root):
        raise ValueError(f"argument {name} escapes its approved root")
    return str(resolved)


def cli_surface_objects(config: dict[str, Any]) -> dict[str, Any]:
    initialize = {
        "protocolVersion": "2025-06-18",
        "capabilities": {"tools": {}},
        "serverInfo": {"name": "evaluated-interface", "version": "2.0"},
    }
    tools = [
        {
            "name": operation["name"],
            "description": operation["description"],
            "inputSchema": operation["input_schema"],
        }
        for operation in config["public_operations"]
    ]
    return canonical_surface_objects(initialize, tools, [], [], [])


def startup_record(
    config: dict[str, Any],
    observed_surface: dict[str, Any],
    observed_surface_digests: dict[str, str],
    contamination_reasons: list[str],
) -> dict[str, Any]:
    return {
        "record_type": "interface_started",
        "sequence": 0,
        "tool_lane": config["tool_lane"],
        "mode": config["mode"],
        "policy_digest": config["policy_digest"],
        "executable_realpath": str(Path(config["executable"]["realpath"]).resolve()),
        "executable_sha256": config["executable"]["sha256"],
        "fixture_root": str(Path(config["fixture_root"]).resolve()),
        "scratch_root": str(Path(config["scratch_root"]).resolve()),
        "expected_surface": validate_surface(config["expected_surface"]),
        "observed_surface": observed_surface,
        "expected_surface_digests": validate_surface_digests(
            config["expected_surface_digests"]
        ),
        "observed_surface_digests": observed_surface_digests,
        "exposed_surface": {
            "tools": sorted(config["allowed_tool_names"]),
            "resources": [],
            "resource_templates": [],
            "prompts": [],
            "capabilities": ["tools"],
            "instructions_sha256": None,
        },
        "allowed_mcp_methods": sorted(config["allowed_mcp_methods"]),
        "active_mcp_count": 1,
        "contamination_reasons": contamination_reasons,
    }


class EvaluatedInterface:
    """Shell-free CLI adapter for one sealed operation surface."""

    def __init__(self, config: dict[str, Any], audit_log: Path):
        inspection = validate_config(config)
        if config["mode"] != "cli":
            raise ValueError("EvaluatedInterface requires CLI mode")
        self.config = config
        self.audit_log = audit_log
        self.calls = 0
        self.operations = {
            operation["name"]: operation for operation in config["public_operations"]
        }
        self.fixture_root = Path(inspection["fixture_root"])
        self.scratch_root = Path(inspection["scratch_root"])
        self.audit_log.parent.mkdir(parents=True, exist_ok=True)
        if self.audit_log.exists() and self.audit_log.stat().st_size:
            raise ValueError("audit log must be empty before interface startup")
        self.audit_log.touch()
        observed = validate_surface(config["expected_surface"])
        observed_digests = surface_digests(cli_surface_objects(config))
        if observed_digests != validate_surface_digests(
            config["expected_surface_digests"]
        ):
            raise ValueError("CLI full surface digest mismatch")
        append_jsonl(
            self.audit_log,
            startup_record(
                config,
                observed,
                observed_digests,
                inspection["contamination_reasons"],
            ),
        )

    def tools(self) -> list[dict[str, Any]]:
        return [
            {
                "name": operation["name"],
                "description": operation["description"],
                "inputSchema": operation["input_schema"],
            }
            for operation in self.operations.values()
        ]

    def call_tool(self, name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        self.calls += 1
        sequence = self.calls
        input_bytes = len(compact(arguments))
        self._audit(sequence, name, input_bytes, 0, None, "ATTEMPTED", "ATTEMPT")
        if sequence > MAX_CALLS:
            self._audit(sequence, name, input_bytes, 0, None, "CALL_LIMIT_REJECTED")
            return self.result(
                f"evaluated-interface call limit {MAX_CALLS} reached; "
                f"call {sequence} was not dispatched",
                True,
            )
        operation = self.operations.get(name)
        if operation is None:
            self._audit(sequence, name, input_bytes, 0, None, "UNKNOWN_OPERATION")
            return self.result(f"unknown public operation: {name}", True)
        try:
            argv = [
                expand_argument(
                    part,
                    arguments,
                    operation["argument_policy"],
                    self.fixture_root,
                    self.scratch_root,
                )
                for part in operation["argv_template"]
            ]
        except (KeyError, ValueError) as error:
            self._audit(sequence, name, input_bytes, 0, None, "INVALID_INPUT")
            return self.result(str(error), True)
        try:
            completed = subprocess.run(
                argv,
                cwd=self.fixture_root,
                env=self.config["environment"],
                stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                check=False,
                timeout=CLI_OPERATION_TIMEOUT_SECONDS,
            )
        except (OSError, subprocess.TimeoutExpired) as error:
            self._audit(sequence, name, input_bytes, 0, None, "FAILED_NO_RESPONSE")
            return self.result(f"public operation produced no response: {error}", True)
        output = completed.stdout
        status = "SUCCESS" if completed.returncode == 0 else "FAILED"
        self._audit(
            sequence, name, input_bytes, len(output), completed.returncode, status
        )
        return self.result(output.decode(errors="replace"), completed.returncode != 0)

    @staticmethod
    def result(text: str, error: bool) -> dict[str, Any]:
        return {"content": [{"type": "text", "text": text}], "isError": error}

    def _audit(
        self,
        sequence: int,
        name: str,
        input_bytes: int,
        output_bytes: int,
        exit_code: int | None,
        status: str,
        phase: str = "TERMINAL",
    ) -> None:
        append_jsonl(
            self.audit_log,
            {
                "record_type": "call",
                "sequence": sequence,
                "name": name,
                "input_bytes": input_bytes,
                "output_bytes": output_bytes,
                "exit_code": exit_code,
                "status": status,
                "phase": phase,
            },
        )


def send(message: dict[str, Any]) -> None:
    sys.stdout.buffer.write(compact(message) + b"\n")
    sys.stdout.buffer.flush()


def method_allowed(method: Any, allowed: set[str]) -> bool:
    return isinstance(method, str) and method in allowed


def validate_native_arguments(
    value: Any, fixture_root: Path, scratch_root: Path, location: str = "arguments"
) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            validate_native_arguments(
                child, fixture_root, scratch_root, f"{location}.{key}"
            )
    elif isinstance(value, list):
        for index, child in enumerate(value):
            validate_native_arguments(
                child, fixture_root, scratch_root, f"{location}[{index}]"
            )
    elif isinstance(value, str):
        if URL.search(value) or COMMAND_FRAGMENT.search(value):
            raise ValueError(f"{location} contains a command or URL")
        if value.startswith("/"):
            path = Path(value).resolve()
            if not path_allowed(path, fixture_root, scratch_root):
                raise ValueError(f"{location} contains a path outside approved roots")
        elif ".." in Path(value).parts:
            raise ValueError(f"{location} contains a path escape")
    elif value is not None and not isinstance(value, (int, float, bool)):
        raise ValueError(f"{location} contains an unsupported value")


def attest_surface(
    expected: dict[str, Any],
    observed: dict[str, Any],
    expected_digests: dict[str, str] | None = None,
    observed_digests: dict[str, str] | None = None,
) -> None:
    for key in (
        "tools",
        "resources",
        "resource_templates",
        "prompts",
        "capabilities",
    ):
        if sorted(expected.get(key, [])) != sorted(observed.get(key, [])):
            raise ValueError(
                f"MCP {key} surface mismatch: expected "
                f"{sorted(expected.get(key, []))}, observed "
                f"{sorted(observed.get(key, []))}"
            )
    if expected.get("instructions_sha256") != observed.get("instructions_sha256"):
        raise ValueError("MCP server instructions surface mismatch")
    if expected_digests is not None:
        if observed_digests is None:
            raise ValueError("MCP full surface digests missing")
        for key in SURFACE_DIGEST_KEYS:
            if expected_digests[key] != observed_digests.get(key):
                raise ValueError(f"MCP full {key} surface digest mismatch")


def read_rpc_response(
    child: subprocess.Popen[bytes], request_id: int, timeout: float = 10
) -> dict[str, Any]:
    assert child.stdout is not None
    ready, _, _ = select.select([child.stdout], [], [], timeout)
    if not ready:
        raise ValueError(f"MCP startup request {request_id} timed out")
    raw = child.stdout.readline()
    if not raw:
        raise ValueError(f"MCP startup request {request_id} returned no response")
    try:
        response = json.loads(raw)
    except json.JSONDecodeError as error:
        raise ValueError(f"MCP startup returned malformed JSON: {error}") from error
    if response.get("id") != request_id:
        raise ValueError("MCP startup response id mismatch")
    return response


def rpc_request(
    child: subprocess.Popen[bytes],
    request_id: int,
    method: str,
    params: dict[str, Any] | None = None,
) -> dict[str, Any]:
    assert child.stdin is not None
    request: dict[str, Any] = {
        "jsonrpc": "2.0",
        "id": request_id,
        "method": method,
    }
    if params is not None:
        request["params"] = params
    child.stdin.write(compact(request) + b"\n")
    child.stdin.flush()
    return read_rpc_response(child, request_id)


def list_result(
    child: subprocess.Popen[bytes], request_id: int, method: str, key: str
) -> list[dict[str, Any]]:
    response = rpc_request(child, request_id, method)
    if response.get("error", {}).get("code") == -32601:
        return []
    result = response.get("result")
    if not isinstance(result, dict) or not isinstance(result.get(key), list):
        raise ValueError(f"{method} did not return a {key} list")
    return result[key]


def close_native_child(child: subprocess.Popen[bytes]) -> None:
    if child.stdin is not None and not child.stdin.closed:
        child.stdin.close()
    try:
        child.terminate()
    except ProcessLookupError:
        pass
    try:
        child.wait(timeout=3)
    except subprocess.TimeoutExpired:
        child.kill()
        child.wait(timeout=3)
    if child.stdout is not None:
        child.stdout.close()
    if child.stderr is not None:
        child.stderr.close()


def start_native_surface(
    config: dict[str, Any], stderr_target: Any = subprocess.DEVNULL
) -> tuple[
    subprocess.Popen[bytes],
    dict[str, Any],
    dict[str, str],
    dict[str, Any],
]:
    """Start and fully enumerate the exact process that may face the model."""
    child = subprocess.Popen(
        config["command_template"],
        cwd=config["cwd"],
        env=config["environment"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=stderr_target,
    )
    try:
        initialized = rpc_request(
            child,
            1,
            "initialize",
            {
                "protocolVersion": "2025-06-18",
                "capabilities": {},
                "clientInfo": {"name": "evaluated-attestor", "version": "1.0"},
            },
        )
        result = initialized.get("result")
        if not isinstance(result, dict):
            raise ValueError("MCP initialize did not return an object")
        capabilities = result.get("capabilities", {})
        if not isinstance(capabilities, dict):
            raise ValueError("MCP capabilities are not an object")
        instructions = result.get("instructions")
        instructions_hash = (
            hashlib.sha256(instructions.encode()).hexdigest()
            if isinstance(instructions, str) and instructions
            else None
        )
        assert child.stdin is not None
        child.stdin.write(
            compact({"jsonrpc": "2.0", "method": "notifications/initialized"})
            + b"\n"
        )
        child.stdin.flush()
        tools = list_result(child, 2, "tools/list", "tools")
        resources = list_result(child, 3, "resources/list", "resources")
        resource_templates = list_result(
            child, 4, "resources/templates/list", "resourceTemplates"
        )
        prompts = list_result(child, 5, "prompts/list", "prompts")
        objects = canonical_surface_objects(
            result, tools, resources, resource_templates, prompts
        )
        digests = surface_digests(objects)
        observed = {
            "tools": sorted(
                item["name"]
                for item in tools
                if isinstance(item, dict) and isinstance(item.get("name"), str)
            ),
            "resources": sorted(
                item["uri"]
                for item in resources
                if isinstance(item, dict) and isinstance(item.get("uri"), str)
            ),
            "resource_templates": sorted(
                item["uriTemplate"]
                for item in resource_templates
                if isinstance(item, dict)
                and isinstance(item.get("uriTemplate"), str)
            ),
            "prompts": sorted(
                item["name"]
                for item in prompts
                if isinstance(item, dict) and isinstance(item.get("name"), str)
            ),
            "capabilities": sorted(capabilities),
            "instructions_sha256": instructions_hash,
        }
        return child, observed, digests, objects
    except Exception:
        close_native_child(child)
        raise


def discover_native_surface(config: dict[str, Any]) -> dict[str, Any]:
    """Fully attest a disposable discovery instance and return its summary."""
    child, observed, digests, _ = start_native_surface(config)
    try:
        attest_surface(
            validate_surface(config["expected_surface"]),
            observed,
            validate_surface_digests(config["expected_surface_digests"]),
            digests,
        )
        return observed
    finally:
        close_native_child(child)


def cli_server(config: dict[str, Any], audit: Path) -> int:
    adapter = EvaluatedInterface(config, audit)
    for raw in sys.stdin.buffer:
        try:
            request = json.loads(raw)
        except json.JSONDecodeError:
            continue
        request_id = request.get("id")
        method = request.get("method")
        if request_id is None:
            continue
        if method == "initialize":
            result = cli_surface_objects(config)["initialize"]
        elif method == "tools/list":
            result = {"tools": adapter.tools()}
        elif method == "tools/call":
            params = request.get("params", {})
            arguments = params.get("arguments", {})
            if not isinstance(arguments, dict):
                arguments = {}
            result = adapter.call_tool(params.get("name", ""), arguments)
        elif method == "ping":
            result = {}
        else:
            send(
                {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {"code": -32601, "message": f"unsupported method: {method}"},
                }
            )
            continue
        send({"jsonrpc": "2.0", "id": request_id, "result": result})
    return 0


def audit_unresolved_calls(
    audit: Path,
    pending: dict[Any, tuple[int, str, int]],
    lock: threading.Lock,
) -> None:
    """Close every pre-dispatch attempt that never received a terminal response."""
    with lock:
        unresolved = list(pending.values())
        pending.clear()
    for sequence, name, input_bytes in unresolved:
        append_jsonl(
            audit,
            {
                "record_type": "call",
                "sequence": sequence,
                "name": name,
                "input_bytes": input_bytes,
                "output_bytes": 0,
                "exit_code": None,
                "status": "FAILED_NO_RESPONSE",
                "phase": "TERMINAL",
            },
        )


def native_proxy(config: dict[str, Any], audit: Path) -> int:
    """Attest the live child completely before serving any model request."""
    inspection = validate_config(config)
    child, observed, observed_digests, objects = start_native_surface(
        config, sys.stderr.buffer
    )
    try:
        attest_surface(
            validate_surface(config["expected_surface"]),
            observed,
            validate_surface_digests(config["expected_surface_digests"]),
            observed_digests,
        )
    except ValueError:
        close_native_child(child)
        raise
    audit.touch()
    append_jsonl(
        audit,
        startup_record(
            config,
            observed,
            observed_digests,
            inspection["contamination_reasons"],
        ),
    )
    assert child.stdin is not None and child.stdout is not None
    pending: dict[Any, tuple[int, str, int]] = {}
    lock = threading.Lock()
    allowed_methods = set(config["allowed_mcp_methods"])
    allowed_tools = set(config["expected_surface"]["tools"])
    exposed_tools = set(config["allowed_tool_names"])
    fixture_root = Path(config["fixture_root"]).resolve()
    scratch_root = Path(config["scratch_root"]).resolve()
    sanitized_initialize = dict(objects["initialize"])
    sanitized_initialize["capabilities"] = {"tools": {}}
    sanitized_initialize.pop("instructions", None)
    sanitized_tools = [
        tool for tool in objects["tools"] if tool["name"] in exposed_tools
    ]
    call_count = 0

    def downstream() -> None:
        for raw in child.stdout:
            try:
                response = json.loads(raw)
                with lock:
                    pending_call = pending.pop(response.get("id"), None)
                if pending_call:
                    sequence, name, input_bytes = pending_call
                    result = response.get("result")
                    is_error = (
                        "error" in response
                        or isinstance(result, dict) and result.get("isError") is True
                    )
                    append_jsonl(
                        audit,
                        {
                            "record_type": "call",
                            "sequence": sequence,
                            "name": name,
                            "input_bytes": input_bytes,
                            "output_bytes": len(raw.rstrip(b"\r\n")),
                            "exit_code": None,
                            "status": "FAILED" if is_error else "SUCCESS",
                            "phase": "TERMINAL",
                        },
                    )
            except (json.JSONDecodeError, AttributeError):
                pass
            sys.stdout.buffer.write(raw)
            sys.stdout.buffer.flush()

    thread = threading.Thread(target=downstream)
    thread.start()
    return_code = 1
    try:
        for raw in sys.stdin.buffer:
            try:
                request = json.loads(raw)
            except json.JSONDecodeError:
                continue
            method = request.get("method")
            if not method_allowed(method, allowed_methods):
                if request.get("id") is not None:
                    send(
                        {
                            "jsonrpc": "2.0",
                            "id": request["id"],
                            "error": {
                                "code": -32601,
                                "message": f"policy rejects method: {method}",
                            },
                        }
                    )
                continue
            if method == "initialize" and request.get("id") is not None:
                send(
                    {
                        "jsonrpc": "2.0",
                        "id": request["id"],
                        "result": sanitized_initialize,
                    }
                )
                continue
            if method == "tools/list" and request.get("id") is not None:
                send(
                    {
                        "jsonrpc": "2.0",
                        "id": request["id"],
                        "result": {"tools": sanitized_tools},
                    }
                )
                continue
            if method == "ping" and request.get("id") is not None:
                send({"jsonrpc": "2.0", "id": request["id"], "result": {}})
                continue
            if method == "notifications/initialized":
                continue
            if method == "tools/call":
                params = request.get("params", {})
                name = params.get("name", "")
                call_count += 1
                input_bytes = len(compact(params.get("arguments", {})))
                append_jsonl(
                    audit,
                    {
                        "record_type": "call",
                        "sequence": call_count,
                        "name": name,
                        "input_bytes": input_bytes,
                        "output_bytes": 0,
                        "exit_code": None,
                        "status": "ATTEMPTED",
                        "phase": "ATTEMPT",
                    },
                )
                if call_count > MAX_CALLS:
                    append_jsonl(
                        audit,
                        {
                            "record_type": "call",
                            "sequence": call_count,
                            "name": name,
                            "input_bytes": input_bytes,
                            "output_bytes": 0,
                            "exit_code": None,
                            "status": "CALL_LIMIT_REJECTED",
                            "phase": "TERMINAL",
                        },
                    )
                    send(
                        {
                            "jsonrpc": "2.0",
                            "id": request.get("id"),
                            "result": EvaluatedInterface.result(
                                f"evaluated-interface call limit {MAX_CALLS} reached; "
                                f"call {call_count} was not dispatched",
                                True,
                            ),
                        }
                    )
                    continue
                if name not in allowed_tools or name not in exposed_tools:
                    append_jsonl(
                        audit,
                        {
                            "record_type": "call",
                            "sequence": call_count,
                            "name": name,
                            "input_bytes": input_bytes,
                            "output_bytes": 0,
                            "exit_code": None,
                            "status": "POLICY_REJECTED",
                            "phase": "TERMINAL",
                        },
                    )
                    send(
                        {
                            "jsonrpc": "2.0",
                            "id": request.get("id"),
                            "result": EvaluatedInterface.result(
                                f"policy rejects non-exposed tool: {name}", True
                            ),
                        }
                    )
                    continue
                try:
                    validate_native_arguments(
                        params.get("arguments", {}), fixture_root, scratch_root
                    )
                except ValueError as error:
                    append_jsonl(
                        audit,
                        {
                            "record_type": "call",
                            "sequence": call_count,
                            "name": name,
                            "input_bytes": input_bytes,
                            "output_bytes": 0,
                            "exit_code": None,
                            "status": "INVALID_INPUT",
                            "phase": "TERMINAL",
                        },
                    )
                    send(
                        {
                            "jsonrpc": "2.0",
                            "id": request.get("id"),
                            "result": EvaluatedInterface.result(str(error), True),
                        }
                    )
                    continue
                with lock:
                    pending[request.get("id")] = (call_count, name, input_bytes)
            try:
                child.stdin.write(raw)
                child.stdin.flush()
            except (BrokenPipeError, OSError):
                break
    finally:
        try:
            child.stdin.close()
        except (BrokenPipeError, OSError):
            pass
        try:
            return_code = child.wait(timeout=5)
        except subprocess.TimeoutExpired:
            child.kill()
            return_code = child.wait(timeout=5)
        thread.join(timeout=5)
        audit_unresolved_calls(audit, pending, lock)
    return return_code


def replace_placeholders(value: Any, replacements: dict[str, str]) -> Any:
    if isinstance(value, dict):
        return {key: replace_placeholders(child, replacements) for key, child in value.items()}
    if isinstance(value, list):
        return [replace_placeholders(child, replacements) for child in value]
    if isinstance(value, str):
        rendered = value
        for marker, replacement in replacements.items():
            rendered = rendered.replace(marker, replacement)
        if "${" in rendered:
            raise ValueError(f"unresolved policy template placeholder: {rendered}")
        return rendered
    return value


def materialize_policy(
    template: dict[str, Any],
    fixture_root: Path,
    scratch_root: Path,
    executable: Path,
    instructions_sha256: str | None,
) -> dict[str, Any]:
    executable = executable.resolve()
    replacements = {
        "${FIXTURE_ROOT}": str(fixture_root.resolve()),
        "${SCRATCH_ROOT}": str(scratch_root.resolve()),
        "${EXECUTABLE_REALPATH}": str(executable),
        "${EXECUTABLE_SHA256}": sha256_file(executable),
        "${INSTRUCTIONS_SHA256}": instructions_sha256 or "",
    }
    rendered = replace_placeholders(template, replacements)
    if rendered["expected_surface"].get("instructions_sha256") == "":
        rendered["expected_surface"]["instructions_sha256"] = None
    rendered["expected_surface_digests"] = {
        key: "0" * 64 for key in SURFACE_DIGEST_KEYS
    }
    rendered = seal_policy(rendered)
    validate_config(rendered)
    if rendered["mode"] == "cli":
        digests = surface_digests(cli_surface_objects(rendered))
    else:
        child, observed, digests, _ = start_native_surface(rendered)
        try:
            attest_surface(validate_surface(rendered["expected_surface"]), observed)
        finally:
            close_native_child(child)
    rendered["expected_surface_digests"] = digests
    rendered = seal_policy(rendered)
    validate_config(rendered)
    return rendered


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path)
    parser.add_argument("--audit-log", type=Path)
    parser.add_argument("--validate-config", type=Path)
    parser.add_argument("--materialize-template", type=Path)
    parser.add_argument("--fixture-root", type=Path)
    parser.add_argument("--scratch-root", type=Path)
    parser.add_argument("--executable", type=Path)
    parser.add_argument("--instructions-sha256")
    parser.add_argument("--output-config", type=Path)
    args = parser.parse_args()
    try:
        if args.validate_config:
            config = json.loads(args.validate_config.read_text())
            print(json.dumps(validate_config(config), indent=2, sort_keys=True))
            return 0
        if args.materialize_template:
            required = (
                args.fixture_root,
                args.scratch_root,
                args.executable,
                args.output_config,
            )
            if any(value is None for value in required):
                raise ValueError(
                    "materialization requires fixture, scratch, executable, and output"
                )
            template = json.loads(args.materialize_template.read_text())
            config = materialize_policy(
                template,
                args.fixture_root,
                args.scratch_root,
                args.executable,
                args.instructions_sha256,
            )
            if not is_within(
                args.output_config.resolve(), Path(config["scratch_root"]).resolve()
            ):
                raise ValueError("materialized config must be inside scratch_root")
            args.output_config.parent.mkdir(parents=True, exist_ok=True)
            args.output_config.write_text(
                json.dumps(config, indent=2, sort_keys=True) + "\n"
            )
            return 0
        if args.config is None or args.audit_log is None:
            raise ValueError("--config and --audit-log are required")
        config = json.loads(args.config.read_text())
        inspection = validate_config(config)
        scratch_root = Path(inspection["scratch_root"])
        if not is_within(args.config.resolve(), scratch_root):
            raise ValueError("active config must be inside scratch_root")
        if not is_within(args.audit_log.resolve(), scratch_root):
            raise ValueError("audit log must be inside scratch_root")
        args.audit_log.parent.mkdir(parents=True, exist_ok=True)
        if args.audit_log.exists():
            args.audit_log.write_text("")
        return (
            cli_server(config, args.audit_log)
            if config.get("mode") == "cli"
            else native_proxy(config, args.audit_log)
        )
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"evaluated-interface: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
