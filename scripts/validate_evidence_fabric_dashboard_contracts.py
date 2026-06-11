#!/usr/bin/env python3
"""Validate Exodus evidence-fabric dashboard contract examples."""

from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]

CONTRACTS = [
    (
        ROOT / "packages" / "contracts" / "evidence-dashboard-state.schema.json",
        ROOT / "examples" / "evidence-dashboard-state.example.json",
    ),
    (
        ROOT / "packages" / "contracts" / "migration-wave-plan.schema.json",
        ROOT / "examples" / "migration-wave-plan.example.json",
    ),
    (
        ROOT / "packages" / "contracts" / "proof-pack-summary.schema.json",
        ROOT / "examples" / "proof-pack-summary.example.json",
    ),
]


def validate_pair(schema_path: Path, example_path: Path) -> list[str]:
    schema = json.loads(schema_path.read_text())
    example = json.loads(example_path.read_text())
    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(example), key=lambda err: list(err.path))
    messages: list[str] = []
    for error in errors:
        path = ".".join(str(part) for part in error.path) or "<root>"
        messages.append(f"{example_path.relative_to(ROOT)} {path}: {error.message}")
    return messages


def main() -> int:
    failures: list[str] = []
    for schema_path, example_path in CONTRACTS:
        if not schema_path.exists():
            failures.append(f"missing schema: {schema_path.relative_to(ROOT)}")
            continue
        if not example_path.exists():
            failures.append(f"missing example: {example_path.relative_to(ROOT)}")
            continue
        failures.extend(validate_pair(schema_path, example_path))

    if failures:
        for failure in failures:
            print(f"ERR: {failure}")
        return 1

    print("OK: Exodus evidence-fabric dashboard contracts are valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
