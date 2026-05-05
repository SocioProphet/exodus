#!/usr/bin/env python3
"""Validate Exodus deletion eligibility and provider downgrade fixtures."""

from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
PAIRS = [
    (
        ROOT / "packages" / "contracts" / "deletion-eligibility-record.schema.json",
        ROOT / "examples" / "deletion-eligibility-record.example.json",
    ),
    (
        ROOT / "packages" / "contracts" / "provider-downgrade-plan.schema.json",
        ROOT / "examples" / "provider-downgrade-plan.example.json",
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

    eligibility = json.loads((ROOT / "examples" / "deletion-eligibility-record.example.json").read_text())
    checks = eligibility.get("checks", {})
    all_checks_passed = all(bool(value) for value in checks.values())
    if eligibility.get("eligibilityStatus") == "eligible" and not all_checks_passed:
        failures.append("eligible deletion status requires every check to pass")
    if eligibility.get("eligibilityStatus") == "cooling-off" and checks.get("coolingOffComplete"):
        failures.append("cooling-off status should not have coolingOffComplete=true")

    downgrade = json.loads((ROOT / "examples" / "provider-downgrade-plan.example.json").read_text())
    steps = downgrade.get("steps", [])
    if downgrade.get("planStatus") == "ready" and not downgrade.get("proofPackRefs"):
        failures.append("ready downgrade plan requires proofPackRefs")
    if not any(step.get("stepId") == "verify-proof-pack" for step in steps):
        failures.append("provider downgrade plan must include verify-proof-pack step")
    if not any(step.get("stepId") == "complete-cooling-off" for step in steps):
        failures.append("provider downgrade plan must include complete-cooling-off step")

    if failures:
        for failure in failures:
            print(f"ERR: {failure}")
        return 1

    print("OK: exit readiness fixtures are valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
