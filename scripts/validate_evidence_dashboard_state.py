#!/usr/bin/env python3
"""Validate the Exodus EvidenceDashboardState example."""

from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "packages" / "contracts" / "evidence-dashboard-state.schema.json"
EXAMPLE = ROOT / "examples" / "evidence-dashboard-state.example.json"


def main() -> int:
    schema = json.loads(SCHEMA.read_text())
    example = json.loads(EXAMPLE.read_text())
    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(example), key=lambda err: list(err.path))
    if errors:
        for error in errors:
            path = ".".join(str(part) for part in error.path) or "<root>"
            print(f"ERR {path}: {error.message}")
        return 1
    print("OK: evidence dashboard state example is valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
