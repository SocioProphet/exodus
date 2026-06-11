#!/usr/bin/env python3
"""Validate Exodus conversion receipt and redaction review fixtures."""

from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
PAIRS = [
    (
        ROOT / "packages" / "contracts" / "conversion-receipt.schema.json",
        ROOT / "examples" / "conversion-receipt.example.json",
    ),
    (
        ROOT / "packages" / "contracts" / "redaction-review-record.schema.json",
        ROOT / "examples" / "redaction-review-record.example.json",
    ),
]


def validate_pair(schema_path: Path, example_path: Path) -> list[str]:
    schema = json.loads(schema_path.read_text())
    example = json.loads(example_path.read_text())
    validator = Draft202012Validator(schema)
    failures = []
    for error in sorted(validator.iter_errors(example), key=lambda err: list(err.path)):
        path = ".".join(str(part) for part in error.path) or "<root>"
        failures.append(f"{example_path.relative_to(ROOT)} {path}: {error.message}")
    return failures


def main() -> int:
    failures: list[str] = []

    for schema_path, example_path in PAIRS:
        failures.extend(validate_pair(schema_path, example_path))

    conversion = json.loads((ROOT / "examples" / "conversion-receipt.example.json").read_text())
    if conversion.get("status") == "succeeded":
        if not conversion.get("outputBlobRef"):
            failures.append("successful conversion must include outputBlobRef")
        if conversion.get("rawCustodyPreserved") is not True:
            failures.append("successful conversion must preserve raw custody")

    redaction = json.loads((ROOT / "examples" / "redaction-review-record.example.json").read_text())
    if redaction.get("reviewStatus") in {"review-required", "blocked"} and redaction.get("exportAllowed"):
        failures.append("review-required or blocked redaction state must not allow export")
    if redaction.get("rawPreserved") is not True:
        failures.append("redaction review must preserve raw source")

    if failures:
        for failure in failures:
            print(f"ERR: {failure}")
        return 1

    print("OK: conversion and redaction fixtures are valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
