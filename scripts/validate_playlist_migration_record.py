#!/usr/bin/env python3
"""Validate Exodus playlist migration record fixture."""

from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "packages" / "contracts" / "playlist-migration-record.schema.json"
EXAMPLE = ROOT / "examples" / "playlist-migration-record.example.json"


def main() -> int:
    schema = json.loads(SCHEMA.read_text())
    example = json.loads(EXAMPLE.read_text())
    validator = Draft202012Validator(schema)
    failures: list[str] = []

    for error in sorted(validator.iter_errors(example), key=lambda err: list(err.path)):
        path = ".".join(str(part) for part in error.path) or "<root>"
        failures.append(f"{EXAMPLE.relative_to(ROOT)} {path}: {error.message}")

    positions = [entry.get("position") for entry in example.get("entries", [])]
    if positions != sorted(positions):
        failures.append("playlist entry positions must remain sorted")

    unresolved = sum(1 for entry in example.get("entries", []) if entry.get("entryStatus") != "resolved")
    if example.get("unresolvedEntryCount") != unresolved:
        failures.append("unresolvedEntryCount must match unresolved entries")

    if not example.get("rawEvidenceRef"):
        failures.append("rawEvidenceRef is required for playlist custody")

    if failures:
        for failure in failures:
            print(f"ERR: {failure}")
        return 1

    print("OK: playlist migration record fixture is valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
