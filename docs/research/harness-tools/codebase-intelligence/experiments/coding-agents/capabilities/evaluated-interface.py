#!/usr/bin/env python3
"""Fail-closed MCP call counter for native servers and allowlisted CLI tools."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import threading
from pathlib import Path
from typing import Any, BinaryIO


MAX_CALLS = 24
TOKEN = re.compile(r"^\{([A-Za-z_][A-Za-z0-9_]*)\}$")
FORBIDDEN_ENV_MARKERS = ("KEY", "TOKEN", "SECRET", "PASSWORD", "CREDENTIAL")


def compact(value: Any) -> bytes:
    return json.dumps(value, separators=(",", ":"), ensure_ascii=False).encode()


def append_jsonl(path: Path, record: dict[str, Any]) -> None:
    with path.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(record, sort_keys=True, ensure_ascii=False) + "\n")


def validate_config(config: dict[str, Any]) -> None:
    if config.get("mode") not in {"cli", "native_mcp"}:
        raise ValueError("mode must be cli or native_mcp")
    cwd = config.get("cwd")
    if not isinstance(cwd, str) or not Path(cwd).is_absolute():
        raise ValueError("cwd must be an absolute path")
    environment = config.get("environment", {})
    if not isinstance(environment, dict):
        raise ValueError("environment must be an object")
    for name, value in environment.items():
        if not isinstance(name, str) or not isinstance(value, str):
            raise ValueError("environment names and values must be strings")
        if any(marker in name.upper() for marker in FORBIDDEN_ENV_MARKERS):
            raise ValueError(f"credential-like environment variable rejected: {name}")

    if config["mode"] == "native_mcp":
        command = config.get("command")
        if (
            not isinstance(command, list)
            or not command
            or not all(isinstance(part, str) for part in command)
            or not Path(command[0]).is_absolute()
        ):
            raise ValueError("native command executable must be absolute")
        return

    names: set[str] = set()
    operations = config.get("public_operations")
    if not isinstance(operations, list) or not operations:
        raise ValueError("CLI mode requires public_operations")
    for operation in operations:
        if not isinstance(operation, dict):
            raise ValueError("each public operation must be an object")
        name = operation.get("name")
        if not isinstance(name, str) or not name:
            raise ValueError("public operation name must be a non-empty string")
        if name in names:
            raise ValueError(f"duplicate public operation: {name}")
        names.add(name)
        if not isinstance(operation.get("description"), str):
            raise ValueError(f"{name}: description must be a string")
        argv = operation.get("argv")
        if (
            not isinstance(argv, list)
            or not argv
            or not all(isinstance(part, str) for part in argv)
            or not Path(argv[0]).is_absolute()
        ):
            raise ValueError(f"{name}: argv executable must be absolute")
        schema = operation.get("input_schema")
        if not isinstance(schema, dict) or schema.get("type") != "object":
            raise ValueError(f"{name}: input_schema must be an object schema")


class EvaluatedInterface:
    """A shell-free adapter for an explicitly allowlisted CLI surface."""

    def __init__(self, config: dict[str, Any], audit_log: Path):
        validate_config(config)
        self.config = config
        self.audit_log = audit_log
        self.calls = 0
        self.operations = {
            operation["name"]: operation
            for operation in config.get("public_operations", [])
        }

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
            argv = [self._expand(part, arguments) for part in operation["argv"]]
        except ValueError as error:
            self._audit(sequence, name, input_bytes, 0, None, "INVALID_INPUT")
            return self.result(str(error), True)
        completed = subprocess.run(
            argv,
            cwd=self.config["cwd"],
            env=self.config.get("environment", {}),
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
        output = completed.stdout
        status = "SUCCESS" if completed.returncode == 0 else "FAILED"
        self._audit(
            sequence, name, input_bytes, len(output), completed.returncode, status
        )
        return self.result(output.decode(errors="replace"), completed.returncode != 0)

    @staticmethod
    def _expand(part: str, arguments: dict[str, Any]) -> str:
        match = TOKEN.fullmatch(part)
        if not match:
            return part
        name = match.group(1)
        value = arguments.get(name)
        if not isinstance(value, (str, int, float, bool)):
            raise ValueError(f"argument {name} must be a scalar")
        return str(value)

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
    ) -> None:
        append_jsonl(
            self.audit_log,
            {
                "sequence": sequence,
                "name": name,
                "input_bytes": input_bytes,
                "output_bytes": output_bytes,
                "exit_code": exit_code,
                "status": status,
            },
        )


def send(message: dict[str, Any]) -> None:
    sys.stdout.buffer.write(compact(message) + b"\n")
    sys.stdout.buffer.flush()


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
            result = {
                "protocolVersion": request.get("params", {}).get(
                    "protocolVersion", "2025-06-18"
                ),
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "evaluated-interface", "version": "1.0"},
            }
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


def copy_stream(source: BinaryIO, destination: BinaryIO) -> None:
    for line in source:
        destination.write(line)
        destination.flush()


def native_proxy(config: dict[str, Any], audit: Path) -> int:
    """Proxy one native stdio MCP server and stop call 25 before child stdin."""
    validate_config(config)
    child = subprocess.Popen(
        config["command"],
        cwd=config["cwd"],
        env=config.get("environment", {}),
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=sys.stderr.buffer,
    )
    assert child.stdin is not None and child.stdout is not None
    pending: dict[Any, tuple[int, str, int]] = {}
    pending_lock = threading.Lock()
    call_count = 0

    def downstream() -> None:
        for raw in child.stdout:
            try:
                response = json.loads(raw)
                with pending_lock:
                    pending_call = pending.pop(response.get("id"), None)
                if pending_call:
                    sequence, name, input_bytes = pending_call
                    result = response.get("result")
                    is_error = (
                        "error" in response
                        or isinstance(result, dict)
                        and result.get("isError") is True
                    )
                    append_jsonl(
                        audit,
                        {
                            "sequence": sequence,
                            "name": name,
                            "input_bytes": input_bytes,
                            "output_bytes": len(raw.rstrip(b"\r\n")),
                            "exit_code": None,
                            "status": "FAILED" if is_error else "SUCCESS",
                        },
                    )
            except (json.JSONDecodeError, AttributeError):
                pass
            sys.stdout.buffer.write(raw)
            sys.stdout.buffer.flush()

    thread = threading.Thread(target=downstream)
    thread.start()
    for raw in sys.stdin.buffer:
        try:
            request = json.loads(raw)
        except json.JSONDecodeError:
            child.stdin.write(raw)
            child.stdin.flush()
            continue
        if request.get("method") == "tools/call":
            call_count += 1
            params = request.get("params", {})
            name = params.get("name", "")
            input_bytes = len(compact(params.get("arguments", {})))
            if call_count > MAX_CALLS:
                append_jsonl(
                    audit,
                    {
                        "sequence": call_count,
                        "name": name,
                        "input_bytes": input_bytes,
                        "output_bytes": 0,
                        "exit_code": None,
                        "status": "CALL_LIMIT_REJECTED",
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
            with pending_lock:
                pending[request.get("id")] = (call_count, name, input_bytes)
        child.stdin.write(raw)
        child.stdin.flush()
    child.stdin.close()
    return_code = child.wait()
    thread.join(timeout=5)
    records = [
        json.loads(line) for line in audit.read_text().splitlines() if line.strip()
    ]
    audit.write_text(
        "".join(
            json.dumps(record, sort_keys=True, ensure_ascii=False) + "\n"
            for record in sorted(records, key=lambda item: item["sequence"])
        )
    )
    return return_code


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--audit-log", type=Path, required=True)
    args = parser.parse_args()
    try:
        config = json.loads(args.config.read_text())
        args.audit_log.parent.mkdir(parents=True, exist_ok=True)
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
