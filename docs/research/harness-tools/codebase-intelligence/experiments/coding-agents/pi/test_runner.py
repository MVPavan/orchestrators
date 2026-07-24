#!/usr/bin/env python3
"""Cost and contamination guardrails for the Pi tracer runner."""

from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

import jsonschema


HERE = Path(__file__).resolve().parent


def load_runner():
    path = HERE / "run-tracer-arm.py"
    spec = importlib.util.spec_from_file_location("pi_tracer_runner", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load Pi tracer runner")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class PiTracerRunnerTest(unittest.TestCase):
    def test_frozen_order_allows_only_the_next_arm(self) -> None:
        runner = load_runner()

        self.assertEqual(runner.next_arm([]), "graphify-assisted")
        self.assertEqual(runner.next_arm(["graphify-assisted"]), "source-only")
        with self.assertRaisesRegex(ValueError, "out of frozen order"):
            runner.next_arm(["source-only"])

    def test_source_only_command_is_one_turn_read_only_and_retry_free(self) -> None:
        runner = load_runner()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            command = runner.build_codex_command(
                codex="codex",
                arm="source-only",
                subject=root,
                output=root / "answer.json",
                events=root / "events.jsonl",
                interface_config=None,
                audit_log=None,
            )

        joined = "\n".join(command)
        self.assertEqual(command[:3], ["codex", "exec", "--ephemeral"])
        self.assertIn("--ignore-user-config", command)
        self.assertIn("--ignore-rules", command)
        self.assertIn("--strict-config", command)
        self.assertIn("--sandbox\nread-only", joined)
        self.assertIn("--model\ngpt-5.6-terra", joined)
        self.assertIn('model_reasoning_effort="medium"', command)
        self.assertIn("model_providers.openai.request_max_retries=0", command)
        self.assertIn("model_providers.openai.stream_max_retries=0", command)
        self.assertNotIn("mcp_servers.evaluated.command", joined)

    def test_event_summary_requires_one_completion_with_usage(self) -> None:
        runner = load_runner()
        events = [
            {"type": "thread.started", "thread_id": "thread-1"},
            {"type": "turn.started"},
            {
                "type": "turn.completed",
                "usage": {
                    "input_tokens": 100,
                    "cached_input_tokens": 20,
                    "output_tokens": 30,
                    "reasoning_output_tokens": 5,
                },
            },
        ]

        summary = runner.summarize_events(events)
        self.assertEqual(summary["answer_turns"], 1)
        self.assertEqual(summary["usage"]["input_tokens"], 100)
        with self.assertRaisesRegex(ValueError, "exactly one completed"):
            runner.summarize_events(events + [events[-1]])

    def test_assisted_arm_flags_source_access_before_graph(self) -> None:
        runner = load_runner()
        source_first = [
            {
                "type": "item.completed",
                "item": {
                    "id": "cmd-1",
                    "type": "command_execution",
                    "command": "rg AgentSession packages",
                    "aggregated_output": "packages/a.ts",
                },
            },
            {
                "type": "item.completed",
                "item": {
                    "id": "mcp-1",
                    "type": "mcp_tool_call",
                    "server": "evaluated",
                    "tool": "query",
                },
            },
        ]

        classified = runner.classify_operations(
            source_first, arm="graphify-assisted"
        )
        self.assertTrue(classified["contamination"]["pre_graph_source_access_seen"])
        graph_first = runner.classify_operations(
            list(reversed(source_first)), arm="graphify-assisted"
        )
        self.assertFalse(graph_first["contamination"]["pre_graph_source_access_seen"])

    def test_metrics_builder_matches_the_frozen_schema(self) -> None:
        runner = load_runner()
        classified = runner.classify_operations([], arm="source-only")
        metrics = runner.build_metrics(
            run_id="pi-t01-source-only",
            arm="source-only",
            elapsed_ms=123,
            event_summary={
                "answer_turns": 1,
                "usage": {
                    "input_tokens": 100,
                    "cached_input_tokens": 20,
                    "output_tokens": 30,
                    "reasoning_output_tokens": 5,
                },
            },
            classified=classified,
            result="COMPLETED",
        )
        schema = json.loads((HERE / "tracer-metrics.schema.json").read_text())

        jsonschema.Draft202012Validator(schema).validate(metrics)


if __name__ == "__main__":
    unittest.main()
