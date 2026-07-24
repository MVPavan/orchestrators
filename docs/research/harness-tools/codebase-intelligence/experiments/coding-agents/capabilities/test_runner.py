#!/usr/bin/env python3
"""Adversarial self-tests for the fail-closed Terra capability runner."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import threading
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock


ROOT = Path(__file__).resolve().parent


def load_module(filename: str, name: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / filename)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {filename}")
    module = importlib.util.module_from_spec(spec)
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


class SafeTree:
    def __init__(self, lane: str = "codegraph"):
        interface.APPROVED_ROOT.mkdir(parents=True, exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(
            prefix=f"runner-test-{lane}-", dir=interface.APPROVED_ROOT
        )
        self.root = Path(self.temp.name)
        self.fixture = self.root / "fixture"
        self.scratch = self.root / lane
        self.bin = self.scratch / "bin"
        self.fixture.mkdir()
        self.bin.mkdir(parents=True)
        (self.fixture / ".git").mkdir()
        (self.scratch / "home").mkdir()
        (self.scratch / "tmp").mkdir()
        self.executable = self.bin / f"{lane}-fake"
        self.executable.write_text("#!/usr/bin/python3\nprint('ok')\n")
        self.executable.chmod(0o755)
        self.lane = lane

    def close(self) -> None:
        self.temp.cleanup()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def cli_policy(tree: SafeTree) -> dict[str, object]:
    config: dict[str, object] = {
        "policy_version": "1.0",
        "tool_lane": tree.lane,
        "mode": "cli",
        "fixture_root": str(tree.fixture.resolve()),
        "scratch_root": str(tree.scratch.resolve()),
        "cwd": str(tree.fixture.resolve()),
        "environment": {
            "PATH": str(tree.bin.resolve()),
            "HOME": str((tree.scratch / "home").resolve()),
            "TMPDIR": str((tree.scratch / "tmp").resolve()),
            "LANG": "C.UTF-8",
        },
        "executable": {
            "realpath": str(tree.executable.resolve()),
            "sha256": sha256(tree.executable),
        },
        "command_template": [str(tree.executable.resolve())],
        "public_operations": [
            {
                "name": "query",
                "description": "Synthetic public query.",
                "input_schema": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {"query": {"type": "string"}},
                    "required": ["query"],
                },
                "argument_policy": {"query": {"kind": "text"}},
                "argv_template": [
                    str(tree.executable.resolve()),
                    "query",
                    "{query}",
                    "--path",
                    str(tree.fixture.resolve()),
                ],
            }
        ],
        "expected_surface": {
            "tools": ["query"],
            "resources": [],
            "resource_templates": [],
            "prompts": [],
            "capabilities": ["tools"],
            "instructions_sha256": None,
        },
        "expected_surface_digests": {
            key: "0" * 64 for key in interface.SURFACE_DIGEST_KEYS
        },
        "allowed_tool_names": ["query"],
        "allowed_mcp_methods": [
            "initialize",
            "notifications/initialized",
            "ping",
            "tools/list",
            "tools/call",
        ],
        "denied_content_sha256": [],
    }
    config["expected_surface_digests"] = interface.surface_digests(
        interface.cli_surface_objects(config)
    )
    return interface.seal_policy(config)


def native_policy(tree: SafeTree) -> dict[str, object]:
    config = cli_policy(tree)
    config.pop("policy_digest")
    config["mode"] = "native_mcp"
    config.pop("public_operations")
    config["expected_surface"]["tools"] = ["query", "delete_project"]
    config["allowed_tool_names"] = ["query"]
    config["expected_surface_digests"] = {
        key: "0" * 64 for key in interface.SURFACE_DIGEST_KEYS
    }
    provisional = interface.seal_policy(config)
    child, _, digests, _ = interface.start_native_surface(provisional)
    interface.close_native_child(child)
    config["expected_surface_digests"] = digests
    return interface.seal_policy(config)


def write_fake_mcp(path: Path, extra_tool: bool = False) -> None:
    tools = [
        {"name": "query", "description": "safe", "inputSchema": {"type": "object"}},
        {
            "name": "delete_project",
            "description": "not exposed",
            "inputSchema": {"type": "object"},
        },
    ]
    if extra_tool:
        tools.append(
            {
                "name": "surprise",
                "description": "unexpected",
                "inputSchema": {"type": "object"},
            }
        )
    path.write_text(
        "#!/usr/bin/python3\n"
        "import json, sys\n"
        f"tools={tools!r}\n"
        "for line in sys.stdin:\n"
        " request=json.loads(line)\n"
        " method=request.get('method')\n"
        " if request.get('id') is None:\n"
        "  continue\n"
        " if method == 'initialize':\n"
        "  result={'protocolVersion':'2025-06-18','capabilities':{'tools':{}},"
        "'serverInfo':{'name':'fake','version':'1'}}\n"
        " elif method == 'tools/list': result={'tools':tools}\n"
        " elif method == 'resources/list': result={'resources':[]}\n"
        " elif method == 'prompts/list': result={'prompts':[]}\n"
        " elif method == 'tools/call':\n"
        "  result={'content':[{'type':'text','text':'ok'}],'isError':False}\n"
        " elif method == 'ping': result={}\n"
        " else:\n"
        "  print(json.dumps({'jsonrpc':'2.0','id':request['id'],"
        "'error':{'code':-32601,'message':'missing'}}),flush=True)\n"
        "  continue\n"
        " print(json.dumps({'jsonrpc':'2.0','id':request['id'],"
        "'result':result}),flush=True)\n"
    )
    path.chmod(0o755)


def write_surface_mcp(path: Path, surface: dict[str, object]) -> None:
    tools = [
        {"name": name, "description": "synthetic", "inputSchema": {"type": "object"}}
        for name in surface["tools"]
    ]
    resources = [{"uri": uri, "name": uri} for uri in surface["resources"]]
    resource_templates = [
        {"uriTemplate": uri, "name": uri}
        for uri in surface["resource_templates"]
    ]
    prompts = [{"name": name, "description": "synthetic"} for name in surface["prompts"]]
    capabilities = {name: {} for name in surface["capabilities"]}
    path.write_text(
        "#!/usr/bin/python3\n"
        "import json, sys\n"
        f"tools={tools!r}\n"
        f"resources={resources!r}\n"
        f"resource_templates={resource_templates!r}\n"
        f"prompts={prompts!r}\n"
        f"capabilities={capabilities!r}\n"
        "for line in sys.stdin:\n"
        " request=json.loads(line)\n"
        " method=request.get('method')\n"
        " if request.get('id') is None:\n"
        "  continue\n"
        " if method == 'initialize':\n"
        "  result={'protocolVersion':'2025-06-18','capabilities':capabilities,"
        "'serverInfo':{'name':'surface-fake','version':'1'}}\n"
        " elif method == 'tools/list': result={'tools':tools}\n"
        " elif method == 'resources/list': result={'resources':resources}\n"
        " elif method == 'resources/templates/list':\n"
        "  result={'resourceTemplates':resource_templates}\n"
        " elif method == 'prompts/list': result={'prompts':prompts}\n"
        " else:\n"
        "  print(json.dumps({'jsonrpc':'2.0','id':request['id'],"
        "'error':{'code':-32601,'message':'missing'}}),flush=True)\n"
        "  continue\n"
        " print(json.dumps({'jsonrpc':'2.0','id':request['id'],"
        "'result':result}),flush=True)\n"
    )
    path.chmod(0o755)


class SchemaTests(unittest.TestCase):
    def test_provider_schema_is_deterministic_and_semantically_equivalent(self) -> None:
        canonical = json.loads((ROOT / "probe-output.schema.json").read_text())
        first = schema_adapter.provider_schema(canonical)
        second = schema_adapter.provider_schema(canonical)
        self.assertEqual(first, second)
        schema_adapter.assert_semantic_equivalence(canonical, first)
        self.assertNotIn("allOf", json.dumps(first))
        self.assertNotIn("prefixItems", first["properties"]["answers"])

    def test_generated_schema_matches_checked_in_artifact(self) -> None:
        expected = schema_adapter.render(
            schema_adapter.provider_schema(
                json.loads((ROOT / "probe-output.schema.json").read_text())
            )
        )
        self.assertEqual(
            expected, (ROOT / "probe-output.provider.schema.json").read_text()
        )


class PolicyTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tree = SafeTree()

    def tearDown(self) -> None:
        self.tree.close()

    def assert_rejected(self, config: dict[str, object], pattern: str) -> None:
        config.pop("policy_digest", None)
        config = interface.seal_policy(config)
        with self.assertRaisesRegex(ValueError, pattern):
            interface.validate_config(config)

    def test_valid_sealed_policy_is_accepted(self) -> None:
        inspection = interface.validate_config(cli_policy(self.tree))
        self.assertEqual(inspection["tool_lane"], "codegraph")
        self.assertEqual(inspection["contamination_reasons"], [])

    def test_tampered_policy_signature_is_rejected(self) -> None:
        config = cli_policy(self.tree)
        config["cwd"] = str(self.tree.scratch)
        with self.assertRaisesRegex(ValueError, "policy_digest"):
            interface.validate_config(config)

    def test_shell_interpreter_and_command_string_are_rejected(self) -> None:
        config = cli_policy(self.tree)
        config["executable"] = {
            "realpath": str(Path("/bin/sh").resolve()),
            "sha256": sha256(Path("/bin/sh").resolve()),
        }
        config["command_template"] = [str(Path("/bin/sh").resolve()), "-c", "true"]
        config["public_operations"][0]["argv_template"] = config["command_template"]
        self.assert_rejected(config, "forbidden executable")

        config = cli_policy(self.tree)
        config["command_template"] = "codegraph query"
        self.assert_rejected(config, "command_template must be a list")

    def test_network_clients_git_and_writer_commands_are_rejected(self) -> None:
        for candidate in ("curl", "wget", "git", "tee"):
            path = next(
                (Path(root) / candidate for root in ("/usr/bin", "/bin") if (Path(root) / candidate).exists()),
                None,
            )
            if path is None:
                continue
            config = cli_policy(self.tree)
            config["executable"] = {
                "realpath": str(path.resolve()),
                "sha256": sha256(path.resolve()),
            }
            config["command_template"] = [str(path.resolve())]
            config["public_operations"][0]["argv_template"] = [str(path.resolve())]
            self.assert_rejected(config, "forbidden executable")

    def test_parent_repo_private_and_live_submodule_paths_are_rejected(self) -> None:
        for forbidden in (
            interface.WORKSPACE_ROOT,
            Path.home(),
            interface.WORKSPACE_ROOT / "external" / "coding-agents" / "pi",
        ):
            config = cli_policy(self.tree)
            config["public_operations"][0]["argv_template"].append(str(forbidden))
            self.assert_rejected(config, "path outside approved roots")

    def test_url_and_credential_environment_are_rejected(self) -> None:
        config = cli_policy(self.tree)
        config["public_operations"][0]["argv_template"].append(
            "https://example.invalid"
        )
        self.assert_rejected(config, "URL")

        config = cli_policy(self.tree)
        config["environment"]["OPENAI_API_KEY"] = "secret"
        self.assert_rejected(config, "credential-like")

    def test_dynamic_path_escape_and_command_fragment_are_rejected(self) -> None:
        config = cli_policy(self.tree)
        operation = config["public_operations"][0]
        operation["input_schema"]["properties"]["target"] = {"type": "string"}
        operation["input_schema"]["required"].append("target")
        operation["argument_policy"]["target"] = {
            "kind": "path",
            "root": "fixture",
        }
        operation["argv_template"].append("{target}")
        config["expected_surface_digests"] = interface.surface_digests(
            interface.cli_surface_objects(config)
        )
        config = interface.seal_policy({k: v for k, v in config.items() if k != "policy_digest"})
        adapter = interface.EvaluatedInterface(config, self.tree.root / "audit.jsonl")
        self.assertTrue(
            adapter.call_tool(
                "query", {"query": "safe", "target": "../../external"}
            )["isError"]
        )
        self.assertTrue(
            adapter.call_tool(
                "query", {"query": "safe; curl https://example.invalid", "target": "x"}
            )["isError"]
        )

    def test_cross_tool_and_renamed_anchor_content_are_detected(self) -> None:
        config = cli_policy(self.tree)
        config["public_operations"][0]["description"] = "Reads graphify output"
        config = interface.seal_policy({k: v for k, v in config.items() if k != "policy_digest"})
        with self.assertRaisesRegex(ValueError, "cross-tool"):
            interface.validate_config(config)

        leaked = self.tree.fixture / "neutral.bin"
        leaked.write_text("confidential scoring key and reference answer")
        errors = runner.isolated_fixture_errors(self.tree.fixture)
        self.assertTrue(any("anchor-like content" in error for error in errors))


class SurfaceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.expected = {
            "tools": ["query"],
            "resources": [],
            "resource_templates": [],
            "prompts": [],
            "capabilities": ["tools"],
            "instructions_sha256": None,
        }
        self.observed = dict(self.expected)

    def test_exact_surface_is_accepted(self) -> None:
        interface.attest_surface(self.expected, self.observed)

    def test_extra_tool_resource_prompt_or_capability_is_rejected(self) -> None:
        mutations = (
            ("tools", ["query", "unexpected"]),
            ("resources", ["graph://unexpected"]),
            ("prompts", ["unexpected"]),
            ("capabilities", ["tools", "resources"]),
        )
        for key, value in mutations:
            observed = dict(self.observed)
            observed[key] = value
            with self.assertRaisesRegex(ValueError, "surface mismatch"):
                interface.attest_surface(self.expected, observed)

    def test_unexpected_server_instructions_are_rejected(self) -> None:
        observed = dict(self.observed)
        observed["instructions_sha256"] = hashlib.sha256(b"surprise").hexdigest()
        with self.assertRaisesRegex(ValueError, "instructions"):
            interface.attest_surface(self.expected, observed)

    def test_arbitrary_native_methods_are_not_proxyable(self) -> None:
        allowed = set(
            [
                "initialize",
                "notifications/initialized",
                "ping",
                "tools/list",
                "tools/call",
            ]
        )
        self.assertTrue(interface.method_allowed("tools/call", allowed))
        self.assertFalse(interface.method_allowed("resources/read", allowed))
        self.assertFalse(interface.method_allowed("prompts/get", allowed))
        self.assertFalse(interface.method_allowed("roots/list", allowed))

    def test_native_startup_attestation_and_exposed_tool_filter(self) -> None:
        tree = SafeTree()
        try:
            write_fake_mcp(tree.executable)
            config = native_policy(tree)
            observed = interface.discover_native_surface(config)
            self.assertEqual(observed["tools"], ["delete_project", "query"])

            config_path = tree.scratch / "native.json"
            audit = tree.scratch / "native-audit.jsonl"
            config_path.write_text(json.dumps(config))
            process = subprocess.Popen(
                [
                    sys.executable,
                    str(ROOT / "evaluated-interface.py"),
                    "--config",
                    str(config_path),
                    "--audit-log",
                    str(audit),
                ],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            requests = (
                json.dumps(
                    {
                        "jsonrpc": "2.0",
                        "id": 1,
                        "method": "initialize",
                        "params": {"protocolVersion": "2025-06-18"},
                    }
                )
                + "\n"
                + json.dumps(
                    {"jsonrpc": "2.0", "id": 2, "method": "tools/list"}
                )
                + "\n"
                + json.dumps(
                    {
                        "jsonrpc": "2.0",
                        "id": 3,
                        "method": "tools/call",
                        "params": {
                            "name": "delete_project",
                            "arguments": {"project": "fixture"},
                        },
                    }
                )
                + "\n"
            )
            stdout, stderr = process.communicate(requests, timeout=10)
            self.assertEqual(process.returncode, 0, stderr)
            responses = [json.loads(line) for line in stdout.splitlines()]
            by_id = {response["id"]: response for response in responses}
            self.assertEqual(
                [tool["name"] for tool in by_id[2]["result"]["tools"]],
                ["query"],
            )
            self.assertTrue(by_id[3]["result"]["isError"])
            startup = runner.load_startup_record(audit)
            self.assertEqual(
                startup["observed_surface"]["tools"],
                ["delete_project", "query"],
            )
            self.assertEqual(startup["exposed_surface"]["tools"], ["query"])
            records, errors = runner.load_audit(audit, require_started=True)
            self.assertEqual(errors, [])
            self.assertEqual(records[0]["status"], "POLICY_REJECTED")

            write_fake_mcp(tree.executable, extra_tool=True)
            config = native_policy(tree)
            with self.assertRaisesRegex(ValueError, "tools surface mismatch"):
                interface.discover_native_surface(config)
        finally:
            tree.close()


class AuditTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tree = SafeTree()

    def tearDown(self) -> None:
        self.tree.close()

    def test_interface_started_record_is_mandatory_even_with_zero_calls(self) -> None:
        audit = self.tree.root / "audit.jsonl"
        interface.EvaluatedInterface(cli_policy(self.tree), audit)
        records, errors = runner.load_audit(audit, require_started=True)
        self.assertEqual(records, [])
        self.assertEqual(errors, [])
        startup = runner.load_startup_record(audit)
        self.assertEqual(startup["record_type"], "interface_started")
        self.assertEqual(startup["active_mcp_count"], 1)

    def test_missing_or_call_only_audit_fails(self) -> None:
        missing = self.tree.root / "missing.jsonl"
        records, errors = runner.load_audit(missing, require_started=True)
        self.assertEqual(records, [])
        self.assertIn("evaluated-interface audit missing", errors)

        call_only = self.tree.root / "call-only.jsonl"
        call_only.write_text(
            json.dumps(
                {
                    "record_type": "call",
                    "sequence": 1,
                    "name": "query",
                    "phase": "TERMINAL",
                    "status": "SUCCESS",
                    "input_bytes": 2,
                    "output_bytes": 2,
                    "exit_code": 0,
                }
            )
            + "\n"
        )
        _, errors = runner.load_audit(call_only, require_started=True)
        self.assertIn("first audit record is not interface_started", errors)

    def test_25th_cli_call_is_rejected_before_execution(self) -> None:
        counter = self.tree.scratch / "counter"
        self.tree.executable.write_text(
            "#!/usr/bin/python3\n"
            "from pathlib import Path\n"
            f"p=Path({str(counter)!r})\n"
            "p.write_text(str(int(p.read_text())+1) if p.exists() else '1')\n"
            "print('ok')\n"
        )
        config = cli_policy(self.tree)
        audit = self.tree.root / "audit.jsonl"
        adapter = interface.EvaluatedInterface(config, audit)
        for _ in range(24):
            self.assertFalse(adapter.call_tool("query", {"query": "safe"})["isError"])
        self.assertTrue(adapter.call_tool("query", {"query": "safe"})["isError"])
        self.assertEqual(counter.read_text(), "24")
        records, errors = runner.load_audit(audit, require_started=True)
        self.assertEqual(errors, [])
        self.assertEqual(records[-1]["status"], "CALL_LIMIT_REJECTED")

    def test_cli_timeout_is_audited_as_failed_no_response(self) -> None:
        audit = self.tree.root / "timeout-audit.jsonl"
        adapter = interface.EvaluatedInterface(cli_policy(self.tree), audit)
        with mock.patch.object(
            interface.subprocess,
            "run",
            side_effect=subprocess.TimeoutExpired(["query"], 120),
        ):
            result = adapter.call_tool("query", {"query": "safe"})
        self.assertTrue(result["isError"])
        records, errors = runner.load_audit(audit, require_started=True)
        self.assertEqual(errors, [])
        self.assertEqual(records[0]["status"], "FAILED_NO_RESPONSE")

    def test_native_pending_call_is_closed_as_failed_no_response(self) -> None:
        audit = self.tree.root / "native-unresolved-audit.jsonl"
        interface.EvaluatedInterface(cli_policy(self.tree), audit)
        interface.append_jsonl(
            audit,
            {
                "record_type": "call",
                "sequence": 1,
                "name": "query",
                "input_bytes": 2,
                "output_bytes": 0,
                "exit_code": None,
                "status": "ATTEMPTED",
                "phase": "ATTEMPT",
            },
        )
        pending = {"request-1": (1, "query", 2)}
        interface.audit_unresolved_calls(audit, pending, threading.Lock())
        self.assertEqual(pending, {})
        records, errors = runner.load_audit(audit, require_started=True)
        self.assertEqual(errors, [])
        self.assertEqual(records[0]["status"], "FAILED_NO_RESPONSE")


class RunnerTests(unittest.TestCase):
    def smoke_args(
        self, *, fixture: Path, run_dir: Path, tool_lane: str
    ) -> SimpleNamespace:
        return SimpleNamespace(
            fixture=fixture,
            run_dir=run_dir,
            tool_lane=tool_lane,
            run_id=None,
            interface_config=None,
            smoke=True,
            codex="codex",
        )

    def assert_smoke_preflight_rejected(
        self, *, fixture: Path, tool_lane: str, suffix: str
    ) -> None:
        target = runner.SESSION_RUN_ROOT / f"runner-test-rejected-{suffix}-{os.getpid()}"
        self.assertFalse(target.exists())
        with mock.patch.object(runner.sys, "stderr"):
            result = runner.run(
                self.smoke_args(
                    fixture=fixture,
                    run_dir=target,
                    tool_lane=tool_lane,
                )
            )
        self.assertEqual(result, 2)
        self.assertFalse(target.exists())

    def test_outside_run_directory_is_rejected_before_creation(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "must-not-exist"
            with mock.patch.object(runner.sys, "stderr"):
                result = runner.run(
                    self.smoke_args(
                        fixture=runner.FROZEN_FIXTURE_ROOT / "codegraph",
                        run_dir=target,
                        tool_lane="codegraph",
                    )
                )
            self.assertEqual(result, 2)
            self.assertFalse(target.exists())

    def test_smoke_lane_mismatch_is_rejected(self) -> None:
        self.assert_smoke_preflight_rejected(
            fixture=runner.FROZEN_FIXTURE_ROOT / "codegraph",
            tool_lane="cbm",
            suffix="lane-mismatch",
        )

    def test_smoke_noncanonical_fixture_is_rejected(self) -> None:
        tree = SafeTree("codegraph")
        try:
            self.assert_smoke_preflight_rejected(
                fixture=tree.fixture,
                tool_lane="codegraph",
                suffix="noncanonical",
            )
        finally:
            tree.close()

    def test_smoke_noncanonical_frozen_identity_is_rejected(self) -> None:
        with mock.patch.object(
            runner,
            "fixture_identity",
            return_value=(
                {
                    "fixture_manifest_sha256": "0" * 64,
                    "source_commit": "1" * 40,
                },
                [],
            ),
        ):
            self.assert_smoke_preflight_rejected(
                fixture=runner.FROZEN_FIXTURE_ROOT / "codegraph",
                tool_lane="codegraph",
                suffix="identity-drift",
            )

    def test_smoke_external_fixture_is_rejected(self) -> None:
        self.assert_smoke_preflight_rejected(
            fixture=runner.EXTERNAL_ROOT / "coding-agents" / "pi",
            tool_lane="codegraph",
            suffix="external",
        )

    def test_valid_output_passes_both_schemas_and_canonical_validator(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            tmp = Path(directory)
            target = tmp / "valid.json"
            target.write_text(json.dumps(valid_output()))
            self.assertEqual(
                runner.finalize_run(target, tmp, ROOT)["status"], "VALIDATED"
            )

    def test_malformed_output_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            tmp = Path(directory)
            target = tmp / "invalid.json"
            target.write_text("{")
            self.assertEqual(
                runner.finalize_run(target, tmp, ROOT)["status"],
                "INVALID_FINAL_OUTPUT",
            )

    def test_config_audit_is_derived_from_command_and_startup(self) -> None:
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
        startup = {
            "active_mcp_count": 1,
            "observed_surface": {
                "tools": ["query"],
                "resources": [],
                "prompts": [],
                "capabilities": ["tools"],
                "instructions_sha256": None,
            },
            "contamination_reasons": [],
        }
        audit = runner.derive_config_audit(
            command=command,
            fixture_errors=[],
            startup=startup,
            provider_environment={"PATH": "/safe"},
        )
        self.assertEqual(audit["active_mcp_count"], 1)
        self.assertEqual(audit["observed_tools"], ["query"])
        self.assertEqual(audit["learning_overlay_scan"], "clean")

    def test_all_lane_templates_materialize_and_validate(self) -> None:
        schema = json.loads(
            (ROOT / "adapter-policies" / "materialized-policy.schema.json").read_text()
        )
        for lane in ("codegraph", "cbm", "graphify"):
            tree = SafeTree(lane)
            try:
                template = json.loads(
                    (
                        ROOT / "adapter-policies" / f"{lane}.template.json"
                    ).read_text()
                )
                if template["mode"] == "native_mcp":
                    write_surface_mcp(tree.executable, template["expected_surface"])
                policy = interface.materialize_policy(
                    template,
                    tree.fixture,
                    tree.scratch,
                    tree.executable,
                    None,
                )
                runner.jsonschema.Draft202012Validator(schema).validate(policy)
                self.assertEqual(policy["tool_lane"], lane)
                self.assertRegex(policy["policy_digest"], r"^[0-9a-f]{64}$")
            finally:
                tree.close()

    def test_metrics_builder_conforms_to_metrics_schema(self) -> None:
        metrics = runner.build_metrics(
            run_id="regression-run",
            tool_lane="codegraph",
            classification="SMOKE_EXCLUDED",
            fixture_manifest_sha256="a" * 64,
            source_commit="b" * 40,
            runtime_version="codex-test",
            usage={
                "input_tokens": 10,
                "cached_input_tokens": 2,
                "output_tokens": 3,
                "reasoning_output_tokens": 1,
            },
            document=valid_output(),
            audit_records=[],
            elapsed_ms=25,
            contamination={
                "cross_tool_output_seen": False,
                "expected_anchors_seen": False,
                "subject_repo_seen": False,
                "independent_source_access": False,
                "unauthorized_operation": False,
                "notes": [],
            },
            schema_tokens="UNKNOWN",
            raw_output_tokens="UNKNOWN",
            raw_output_bytes=128,
        )
        schema = json.loads((ROOT / "metrics.schema.json").read_text())
        runner.jsonschema.Draft202012Validator(schema).validate(metrics)
        self.assertEqual(metrics["tool_lane"], "codegraph")

    def test_lane_mismatch_is_rejected_during_preflight(self) -> None:
        tree = SafeTree("codegraph")
        try:
            config_path = tree.root / "interface.json"
            config_path.write_text(json.dumps(cli_policy(tree)))
            errors = runner.interface_config_errors(
                config_path, tree.fixture, "cbm"
            )
            self.assertTrue(any("does not match requested lane" in item for item in errors))
        finally:
            tree.close()

    def test_unrelated_mcp_event_is_contamination(self) -> None:
        events = [
            {
                "item": {
                    "type": "mcp_tool_call",
                    "id": "call-1",
                    "server": "unexpected",
                    "tool": "query",
                }
            }
        ]
        errors, calls, unrelated = runner.mcp_event_errors(
            events, [{"name": "query"}], smoke=False
        )
        self.assertEqual(unrelated, 1)
        self.assertEqual(calls[0]["server"], "unexpected")
        self.assertTrue(any("unrelated MCP server" in item for item in errors))

    def test_evaluated_mcp_event_order_must_match_audit(self) -> None:
        events = [
            {
                "item": {
                    "type": "mcp_tool_call",
                    "id": "call-1",
                    "server": "evaluated",
                    "tool": "status",
                }
            },
            {
                "item": {
                    "type": "mcp_tool_call",
                    "id": "call-2",
                    "server": "evaluated",
                    "tool": "query",
                }
            },
        ]
        errors, _, unrelated = runner.mcp_event_errors(
            events,
            [{"name": "query"}, {"name": "status"}],
            smoke=False,
        )
        self.assertEqual(unrelated, 0)
        self.assertIn(
            "provider evaluated MCP calls do not match the interface audit",
            errors,
        )

    def test_structured_contamination_flags_fail_closed(self) -> None:
        document = valid_output()
        document["limitations"] = ["CBM cross-tool output was present."]
        record = runner.structured_contamination(
            events=[],
            document=document,
            unrelated_mcp_count=0,
            notes=["fixture contains anchor-like content"],
            tool_lane="codegraph",
        )
        errors = runner.contamination_record_errors(record)
        self.assertTrue(record["cross_tool_output_seen"])
        self.assertTrue(record["expected_anchors_seen"])
        self.assertTrue(any("cross_tool_output_seen" in item for item in errors))
        self.assertTrue(any("expected_anchors_seen" in item for item in errors))


if __name__ == "__main__":
    unittest.main(verbosity=2)
