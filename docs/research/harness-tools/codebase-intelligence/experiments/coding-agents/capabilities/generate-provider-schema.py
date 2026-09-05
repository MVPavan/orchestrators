#!/usr/bin/env python3
"""Generate the Codex structured-output schema from the canonical probe schema."""

from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
CANONICAL = HERE / "probe-output.schema.json"
PROVIDER = HERE / "probe-output.provider.schema.json"


def _const_type(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, int):
        return "integer"
    if isinstance(value, float):
        return "number"
    if isinstance(value, str):
        return "string"
    raise ValueError(f"unsupported const type: {type(value).__name__}")


def _add_const_types(node: Any) -> None:
    if isinstance(node, dict):
        if "const" in node and "type" not in node:
            node["type"] = _const_type(node["const"])
        for value in node.values():
            _add_const_types(value)
    elif isinstance(node, list):
        for value in node:
            _add_const_types(value)


def provider_schema(canonical: dict[str, Any]) -> dict[str, Any]:
    """Flatten only the canonical qXX wrappers rejected by Codex."""
    result = copy.deepcopy(canonical)
    base = result["$defs"]["answer"]
    for number in range(1, 12):
        question_id = f"Q{number:02d}"
        flattened = copy.deepcopy(base)
        flattened["properties"]["question_id"] = {
            "type": "string",
            "const": question_id,
        }
        result["$defs"][question_id.lower()] = flattened
    provider_answer = copy.deepcopy(base)
    provider_answer["properties"]["question_id"] = {
        "type": "string",
        "enum": [f"Q{number:02d}" for number in range(1, 12)],
    }
    result["$defs"]["provider_answer"] = provider_answer
    answers = result["properties"]["answers"]
    answers.pop("prefixItems")
    answers["items"] = {"$ref": "#/$defs/provider_answer"}
    _add_const_types(result)
    assert_semantic_equivalence(canonical, result)
    return result


def assert_semantic_equivalence(
    canonical: dict[str, Any], provider: dict[str, Any]
) -> None:
    """Check every frozen semantic field affected by adaptation."""
    for key in ("type", "additionalProperties", "required"):
        if canonical[key] != provider[key]:
            raise ValueError(f"root {key} changed")
    for key in ("schema_version", "fixture_id"):
        expected = copy.deepcopy(canonical["properties"][key])
        expected["type"] = _const_type(expected["const"])
        if expected != provider["properties"][key]:
            raise ValueError(f"root property {key} changed")
    for key in ("run_status", "operations", "limitations"):
        if canonical["properties"][key] != provider["properties"][key]:
            raise ValueError(f"root property {key} changed")

    canonical_answers = canonical["properties"]["answers"]
    provider_answers = provider["properties"]["answers"]
    for key in ("type", "minItems", "maxItems"):
        if canonical_answers[key] != provider_answers[key]:
            raise ValueError(f"answers.{key} changed")
    if provider_answers.get("items") != {"$ref": "#/$defs/provider_answer"}:
        raise ValueError("provider answer item changed")
    if "prefixItems" in provider_answers:
        raise ValueError("provider schema retains unsupported tuple items")

    canonical_answer = canonical["$defs"]["answer"]
    for number in range(1, 12):
        question_id = f"Q{number:02d}"
        candidate = provider["$defs"][question_id.lower()]
        for key in ("type", "additionalProperties", "required"):
            if candidate[key] != canonical_answer[key]:
                raise ValueError(f"{question_id}.{key} changed")
        for field in ("status", "answer", "evidence", "uncertainty"):
            if candidate["properties"][field] != canonical_answer["properties"][field]:
                raise ValueError(f"{question_id}.{field} changed")
        if candidate["properties"]["question_id"] != {
            "type": "string",
            "const": question_id,
        }:
            raise ValueError(f"{question_id} identity changed")
    provider_answer = provider["$defs"]["provider_answer"]
    for key in ("type", "additionalProperties", "required"):
        if provider_answer[key] != canonical_answer[key]:
            raise ValueError(f"provider_answer.{key} changed")
    for field in ("status", "answer", "evidence", "uncertainty"):
        if provider_answer["properties"][field] != canonical_answer["properties"][field]:
            raise ValueError(f"provider_answer.{field} changed")
    if provider_answer["properties"]["question_id"] != {
        "type": "string",
        "enum": [f"Q{number:02d}" for number in range(1, 12)],
    }:
        raise ValueError("provider answer question enum changed")

    for node in _walk(provider):
        if isinstance(node, dict) and "allOf" in node:
            raise ValueError("provider schema still contains unsupported allOf")
        if isinstance(node, dict) and "const" in node and "type" not in node:
            raise ValueError("provider schema contains an untyped const")


def _walk(node: Any):
    yield node
    if isinstance(node, dict):
        for value in node.values():
            yield from _walk(value)
    elif isinstance(node, list):
        for value in node:
            yield from _walk(value)


def render(schema: dict[str, Any]) -> str:
    return json.dumps(schema, indent=2, ensure_ascii=False) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--canonical", type=Path, default=CANONICAL)
    parser.add_argument("--output", type=Path, default=PROVIDER)
    args = parser.parse_args()
    generated = render(
        provider_schema(json.loads(args.canonical.read_text(encoding="utf-8")))
    )
    if args.check:
        if (
            not args.output.exists()
            or args.output.read_text(encoding="utf-8") != generated
        ):
            print(f"provider_schema=stale path={args.output}")
            return 1
        print("provider_schema=valid equivalent=true")
        return 0
    args.output.write_text(generated, encoding="utf-8")
    print(f"provider_schema=generated path={args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
