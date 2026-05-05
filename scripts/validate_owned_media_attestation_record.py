#!/usr/bin/env python3
"""Validate the owned-media attestation example."""

from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "packages" / "contracts" / "owned-media-attestation-record.schema.json"
EXAMPLE = ROOT / "examples" / "owned-media-attestation-record.example.json"


def main() -> int:
    schema = json.loads(SCHEMA.read_text())
    example = json.loads(EXAMPLE.read_text())
    errors = sorted(
        Draft202012Validator(schema).iter_errors(example),
        key=lambda err: list(err.path),
    )
    failures = []
    for error in errors:
        path = ".".join(str(part) for part in error.path) or "<root>"
        failures.append(f"{path}: {error.message}")

    if example.get("attestationStatus") == "captured" and not example.get("privateUseAllowed"):
        failures.append("captured attestation must allow private use")
    if example.get("publicDistributionStatus") == "cleared" and example.get("attestationScope") == "personal-use":
        failures.append("personal-use attestation must not clear public distribution")

    if failures:
        for failure in failures:
            print(f"ERR: {failure}")
        return 1

    print("OK: owned media attestation example is valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
