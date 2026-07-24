#!/usr/bin/env python3
"""Validate probe invariants that JSON Schema cannot express conveniently."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, TextIO


EXPECTED_QUESTIONS = [f"Q{number:02d}" for number in range(1, 12)]
MAX_OPERATIONS = 24


def load_document(argument: str) -> Any:
    source: TextIO
    if argument == "-":
        source = sys.stdin
    else:
        source = Path(argument).open(encoding="utf-8")
    try:
        return json.load(source)
    finally:
        if source is not sys.stdin:
            source.close()


def validate(document: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(document, dict):
        return ["root must be a JSON object"]

    answers = document.get("answers")
    if not isinstance(answers, list):
        errors.append("answers must be an array")
    else:
        question_ids = [
            answer.get("question_id") if isinstance(answer, dict) else None
            for answer in answers
        ]
        if question_ids != EXPECTED_QUESTIONS:
            errors.append("answers must contain Q01 through Q11 exactly once in order")

    operations = document.get("operations")
    if not isinstance(operations, list):
        errors.append("operations must be an array")
    else:
        if len(operations) > MAX_OPERATIONS:
            errors.append(f"operations must contain at most {MAX_OPERATIONS} items")
        sequences = [
            operation.get("sequence") if isinstance(operation, dict) else None
            for operation in operations
        ]
        if any(type(sequence) is not int for sequence in sequences):
            errors.append("every operation sequence must be an integer")
        elif sequences != list(range(1, len(operations) + 1)):
            errors.append(
                "operation sequences must be unique, contiguous, ordered, and start at 1"
            )

    return errors


def main() -> int:
    if len(sys.argv) != 2:
        print(f"usage: {Path(sys.argv[0]).name} <probe-output.json|->", file=sys.stderr)
        return 64

    try:
        document = load_document(sys.argv[1])
    except (OSError, json.JSONDecodeError) as error:
        print(f"invalid input: {error}", file=sys.stderr)
        return 2

    errors = validate(document)
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1

    print("probe_output_invariants=valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
