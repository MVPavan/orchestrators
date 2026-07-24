#!/usr/bin/env python3
"""Deterministic checks for the frozen Pi tracer protocol."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent


class PiProtocolPreflightTest(unittest.TestCase):
    def test_all_four_arms_pass_without_launching_a_model(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                str(HERE / "preflight.py"),
                "--config",
                str(HERE / "tracer-arms.json"),
            ],
            cwd=HERE,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("PASS: 4 Pi tracer arms", completed.stdout)
        self.assertIn("provider calls: 0", completed.stdout)

    def test_changed_tool_surface_fails_closed(self) -> None:
        config = json.loads((HERE / "tracer-arms.json").read_text())
        cbm = next(arm for arm in config["arms"] if arm["id"] == "cbm-assisted")
        cbm["allowed_graph_operations"].append("detect_changes")
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json") as stream:
            json.dump(config, stream)
            stream.flush()
            completed = subprocess.run(
                [
                    sys.executable,
                    str(HERE / "preflight.py"),
                    "--config",
                    stream.name,
                ],
                cwd=HERE,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("does not match the exact frozen list", completed.stderr)


if __name__ == "__main__":
    unittest.main()
