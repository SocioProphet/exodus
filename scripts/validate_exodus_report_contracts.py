#!/usr/bin/env python3
"""Validate Exodus provider topology, source alias, and blocked object reports."""

from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
PAIRS = [
    (
        ROOT / "packages" / "contracts" / "provider-topology-snapshot.schema.json",
        ROOT / "examples" / "provider-topology-snapshot.example.json",
    ),
    (
        ROOT / "packages" / "contracts" / "source-alias-report.schema.json",
        ROOT / "examples" / "source-alias-report.example.json",
    ),
    (
        ROOT / "packages" / "contracts" / "blocked-object-report.schema.json",
        ROOT / "examples" / "blocked-object-report.example.json",
    ),
]


def validate_pair(schema_path: Path, example_path: Path) -> list[str]:
    schema = json.loads(schema_path.read_text())
    example = json.loads(example_path.read_text())
    validator = Draft202012Validator(schema)
    failures: list[str] = []
    for error in sorted(validator.iter_errors(example), key=lambda err: list(err.path)):
        path = ".".join(str(part) for part in error.path) or "<root>"
        failures.append(f"{example_path.relative_to(ROOT)} {path}: {error.message}")
    return failures


def main() -> int:
    failures: list[str] = []

    for schema_path, example_path in PAIRS:
        if not schema_path.exists():
            failures.append(f"missing schema: {schema_path.relative_to(ROOT)}")
            continue
        if not example_path.exists():
            failures.append(f"missing example: {example_path.relative_to(ROOT)}")
            continue
        failures.extend(validate_pair(schema_path, example_path))

    alias_example = json.loads((ROOT / "examples" / "source-alias-report.example.json").read_text())
    if alias_example.get("aliasCount") != len(alias_example.get("aliases", [])):
        failures.append("source alias report aliasCount must match aliases length")

    blocked_example = json.loads((ROOT / "examples" / "blocked-object-report.example.json").read_text())
    if blocked_example.get("blockedCount") != len(blocked_example.get("blockedObjects", [])):
        failures.append("blocked object report blockedCount must match blockedObjects length")

    if failures:
        for failure in failures:
            print(f"ERR: {failure}")
        return 1

    print("OK: Exodus report contract fixtures are valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
