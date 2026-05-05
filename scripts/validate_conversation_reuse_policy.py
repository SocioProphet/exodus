#!/usr/bin/env python3
"""Validate Exodus conversation reuse policy fixture."""

from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "packages" / "contracts" / "conversation-reuse-policy.schema.json"
EXAMPLE = ROOT / "examples" / "conversation-reuse-policy.example.json"


def main() -> int:
    schema = json.loads(SCHEMA.read_text())
    example = json.loads(EXAMPLE.read_text())
    validator = Draft202012Validator(schema)
    failures: list[str] = []

    for error in sorted(validator.iter_errors(example), key=lambda err: list(err.path)):
        path = ".".join(str(part) for part in error.path) or "<root>"
        failures.append(f"{EXAMPLE.relative_to(ROOT)} {path}: {error.message}")

    if example.get("reuseMode") != "blocked":
        if example.get("citationRequired") is not True:
            failures.append("non-blocked reuse must require citation")
        if example.get("treatModelOutputsAsHistorical") is not True:
            failures.append("model outputs must be treated as historical records")

    if "sourceos-chat" in set(example.get("allowedTargets", [])) and not example.get("redactionRequired"):
        failures.append("sourceos-chat reuse requires redaction review")

    if failures:
        for failure in failures:
            print(f"ERR: {failure}")
        return 1

    print("OK: conversation reuse policy fixture is valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
