#!/usr/bin/env python3
"""Deterministic self-tests for the Terra capability-probe runner."""

from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def load_module(filename: str, name: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / filename)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {filename}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


schema_adapter = load_module("generate-provider-schema.py", "schema_adapter")
interface = load_module("evaluated-interface.py", "evaluated_interface")
runner = load_module("run-terra-probe.py", "terra_runner")


def answer(question_id: str) -> dict[str, object]:
    return {
        "question_id": question_id,
        "status": "ABSTAINED",
        "answer": "Synthetic setup answer.",
        "evidence": [],
        "uncertainty": ["No evaluated tool was exposed."],
    }


def valid_output() -> dict[str, object]:
    return {
        "schema_version": "1.0",
        "fixture_id": "mixed-ts-rust-capability-v1",
        "run_status": "PARTIAL",
        "answers": [answer(f"Q{i:02d}") for i in range(1, 12)],
        "operations": [],
        "limitations": ["Synthetic setup smoke."],
    }


def cli_config(tmp: Path, command: Path) -> dict[str, object]:
    return {
        "mode": "cli",
        "cwd": str(tmp),
        "environment": {"PATH": os.environ["PATH"], "LANG": "C.UTF-8"},
        "public_operations": [
            {
                "name": "query",
                "description": "Synthetic public query.",
                "input_schema": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {},
                    "required": [],
                },
                "argv": [str(command)],
            }
        ],
    }


class SchemaTests(unittest.TestCase):
    def test_provider_schema_is_deterministic_and_semantically_equivalent(self) -> None:
        canonical = json.loads((ROOT / "probe-output.schema.json").read_text())
        first = schema_adapter.provider_schema(canonical)
        second = schema_adapter.provider_schema(canonical)
        self.assertEqual(first, second)
        schema_adapter.assert_semantic_equivalence(canonical, first)
        self.assertNotIn("allOf", json.dumps(first))
        self.assertNotIn("prefixItems", first["properties"]["answers"])
        self.assertEqual(
            first["properties"]["answers"]["items"],
            {"$ref": "#/$defs/provider_answer"},
        )
        self.assertEqual(
            first["$defs"]["provider_answer"]["properties"]["question_id"],
            {
                "type": "string",
                "enum": [f"Q{number:02d}" for number in range(1, 12)],
            },
        )

    def test_generated_schema_matches_checked_in_artifact(self) -> None:
        expected = schema_adapter.render(
            schema_adapter.provider_schema(
                json.loads((ROOT / "probe-output.schema.json").read_text())
            )
        )
        self.assertEqual(
            expected, (ROOT / "probe-output.provider.schema.json").read_text()
        )


class InterfaceTests(unittest.TestCase):
    def test_25th_cli_call_is_rejected_before_command_execution(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            tmp = Path(directory)
            counter = tmp / "counter"
            command = tmp / "fake-command.py"
            command.write_text(
                "#!/usr/bin/env python3\n"
                "from pathlib import Path\n"
                f"p=Path({str(counter)!r})\n"
                "p.write_text(str(int(p.read_text())+1) if p.exists() else '1')\n"
                "print('ok')\n"
            )
            command.chmod(0o755)
            adapter = interface.EvaluatedInterface(
                cli_config(tmp, command), tmp / "audit.jsonl"
            )
            for call in range(24):
                self.assertFalse(adapter.call_tool("query", {})["isError"], call)
            self.assertTrue(adapter.call_tool("query", {})["isError"])
            self.assertEqual(counter.read_text(), "24")
            records = [
                json.loads(line) for line in (tmp / "audit.jsonl").read_text().splitlines()
            ]
            self.assertEqual(records[-1]["status"], "CALL_LIMIT_REJECTED")
            self.assertEqual(records[-1]["sequence"], 25)

    def test_25th_native_mcp_call_is_rejected_before_child_dispatch(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            tmp = Path(directory)
            counter = tmp / "counter"
            server = tmp / "fake-server.py"
            server.write_text(
                "#!/usr/bin/env python3\n"
                "import json, sys\n"
                "from pathlib import Path\n"
                f"counter=Path({str(counter)!r})\n"
                "for line in sys.stdin:\n"
                " request=json.loads(line)\n"
                " if request.get('method') == 'tools/call':\n"
                "  counter.write_text(str(int(counter.read_text())+1)"
                " if counter.exists() else '1')\n"
                " response={'jsonrpc':'2.0','id':request.get('id'),"
                "'result':{'content':[{'type':'text','text':'ok'}],"
                "'isError':False}}\n"
                " print(json.dumps(response), flush=True)\n"
            )
            server.chmod(0o755)
            config = tmp / "config.json"
            config.write_text(
                json.dumps(
                    {
                        "mode": "native_mcp",
                        "cwd": str(tmp),
                        "environment": {
                            "PATH": os.environ["PATH"],
                            "LANG": "C.UTF-8",
                        },
                        "command": [str(server)],
                    }
                )
            )
            audit = tmp / "audit.jsonl"
            process = subprocess.Popen(
                [
                    sys.executable,
                    str(ROOT / "evaluated-interface.py"),
                    "--config",
                    str(config),
                    "--audit-log",
                    str(audit),
                ],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            requests = "".join(
                json.dumps(
                    {
                        "jsonrpc": "2.0",
                        "id": number,
                        "method": "tools/call",
                        "params": {"name": "query", "arguments": {}},
                    }
                )
                + "\n"
                for number in range(1, 26)
            )
            stdout, stderr = process.communicate(requests, timeout=10)
            self.assertEqual(process.returncode, 0, stderr)
            self.assertEqual(len(stdout.splitlines()), 25)
            self.assertEqual(counter.read_text(), "24")
            records = [json.loads(line) for line in audit.read_text().splitlines()]
            self.assertEqual(records[-1]["status"], "CALL_LIMIT_REJECTED")
            self.assertEqual(records[-1]["sequence"], 25)


class RunnerTests(unittest.TestCase):
    def test_valid_output_passes_both_schemas_and_canonical_validator(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            tmp = Path(directory)
            target = tmp / "valid.json"
            target.write_text(json.dumps(valid_output()))
            self.assertEqual(
                runner.finalize_run(target, tmp, ROOT)["status"], "VALIDATED"
            )

    def test_malformed_json_and_non_contiguous_sequence_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            tmp = Path(directory)
            malformed = tmp / "malformed.json"
            malformed.write_text("{")
            self.assertEqual(
                runner.finalize_run(malformed, tmp, ROOT)["status"],
                "INVALID_FINAL_OUTPUT",
            )

            output = valid_output()
            output["operations"] = [
                {
                    "sequence": 2,
                    "public_operation": "query",
                    "purpose": "synthetic",
                    "result": "SUCCESS",
                    "output_bytes": 2,
                }
            ]
            invalid = tmp / "sequence.json"
            invalid.write_text(json.dumps(output))
            self.assertEqual(
                runner.finalize_run(invalid, tmp, ROOT)["status"],
                "INVALID_FINAL_OUTPUT",
            )

    def test_schema_rejection_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            tmp = Path(directory)
            output = valid_output()
            del output["fixture_id"]
            target = tmp / "invalid.json"
            target.write_text(json.dumps(output))
            self.assertEqual(
                runner.finalize_run(target, tmp, ROOT)["status"],
                "INVALID_FINAL_OUTPUT",
            )

    def test_audit_count_must_match_final_operations_and_rejection_is_invalid(self) -> None:
        document = valid_output()
        document["operations"] = [
            {
                "sequence": 1,
                "public_operation": "query",
                "purpose": "synthetic",
                "result": "SUCCESS",
                "output_bytes": 2,
            }
        ]
        record = {
            "sequence": 1,
            "name": "query",
            "input_bytes": 2,
            "output_bytes": 2,
            "exit_code": 0,
            "status": "SUCCESS",
        }
        errors, dispatched, rejected = runner.audit_errors(
            [record], document, False
        )
        self.assertEqual(errors, [])
        self.assertEqual(dispatched, 1)
        self.assertFalse(rejected)

        errors, _, rejected = runner.audit_errors(
            [
                record,
                {
                    "sequence": 25,
                    "name": "query",
                    "input_bytes": 2,
                    "output_bytes": 0,
                    "exit_code": None,
                    "status": "CALL_LIMIT_REJECTED",
                },
            ],
            document,
            False,
        )
        self.assertTrue(rejected)
        self.assertIn(
            "call limit exceeded; rejected call makes the run invalid", errors
        )

    def test_overlay_scan_and_clean_command_are_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            fixture = Path(directory)
            (fixture / ".git").mkdir()
            self.assertEqual(runner.isolated_fixture_errors(fixture), [])
            (fixture / "AGENTS.md").write_text("contaminating")
            self.assertIn(
                "fixture contains forbidden learning overlay: AGENTS.md",
                runner.isolated_fixture_errors(fixture),
            )

        command = runner.build_codex_command(
            codex="codex",
            fixture=Path("/isolated-fixture"),
            provider_schema=Path("/schema.json"),
            output=Path("/output.json"),
            interface_config=Path("/interface.json"),
            audit_log=Path("/audit.jsonl"),
            prompt="synthetic",
            smoke=False,
        )
        joined = "\0".join(command)
        for required in (
            "--ephemeral",
            "--ignore-user-config",
            "--ignore-rules",
            "--sandbox\0read-only",
            "--model\0gpt-5.6-terra",
            'model_reasoning_effort="medium"',
        ):
            self.assertIn(required, joined)
        cd_index = command.index("-C")
        self.assertEqual(command[cd_index + 1], "/isolated-fixture")
        self.assertEqual(joined.count("mcp_servers."), 4)


if __name__ == "__main__":
    unittest.main(verbosity=2)
