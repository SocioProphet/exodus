#!/usr/bin/env python3
"""Validate Exodus notes-source profile fixtures."""

from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "packages" / "contracts" / "notes-source-profile.schema.json"
EXAMPLES = [
    ROOT / "examples" / "notes-source-profile.example.json",
    ROOT / "examples" / "notes-source-profile.icloud-notes.example.json",
    ROOT / "examples" / "notes-source-profile.onenote.example.json",
]
REQUIRED_SURFACES = {"google-keep", "icloud-notes", "onenote"}


def main() -> int:
    schema = json.loads(SCHEMA.read_text())
    validator = Draft202012Validator(schema)
    failures: list[str] = []
    seen_surfaces: set[str] = set()

    for example_path in EXAMPLES:
        if not example_path.exists():
            failures.append(f"missing example: {example_path.relative_to(ROOT)}")
            continue
        example = json.loads(example_path.read_text())
        seen_surfaces.add(example.get("surface", ""))
        for error in sorted(validator.iter_errors(example), key=lambda err: list(err.path)):
            path = ".".join(str(part) for part in error.path) or "<root>"
            failures.append(f"{example_path.relative_to(ROOT)} {path}: {error.message}")

    missing = REQUIRED_SURFACES - seen_surfaces
    if missing:
        failures.append(f"missing required notes surfaces: {sorted(missing)}")

    if failures:
        for failure in failures:
            print(f"ERR: {failure}")
        return 1

    print("OK: notes source profile fixtures are valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
