#!/usr/bin/env python3
"""Validate Exodus AI chat export source and document fixtures."""

from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
SOURCE_SCHEMA = ROOT / "packages" / "contracts" / "ai-chat-source-profile.schema.json"
DOC_SCHEMA = ROOT / "packages" / "contracts" / "ai-chat-conversation-document.schema.json"
SOURCE_EXAMPLES = [
    ROOT / "examples" / "ai-chat-source-profile.chatgpt.example.json",
    ROOT / "examples" / "ai-chat-source-profile.claude.example.json",
]
DOC_EXAMPLE = ROOT / "examples" / "ai-chat-conversation-document.example.json"
REQUIRED_SURFACES = {"chatgpt", "claude"}


def validate(schema_path: Path, example_path: Path) -> list[str]:
    schema = json.loads(schema_path.read_text())
    example = json.loads(example_path.read_text())
    errors = sorted(Draft202012Validator(schema).iter_errors(example), key=lambda err: list(err.path))
    failures = []
    for error in errors:
        path = ".".join(str(part) for part in error.path) or "<root>"
        failures.append(f"{example_path.relative_to(ROOT)} {path}: {error.message}")
    return failures


def main() -> int:
    failures: list[str] = []
    seen_surfaces: set[str] = set()

    for example_path in SOURCE_EXAMPLES:
        if not example_path.exists():
            failures.append(f"missing source example: {example_path.relative_to(ROOT)}")
            continue
        example = json.loads(example_path.read_text())
        seen_surfaces.add(example.get("surface", ""))
        failures.extend(validate(SOURCE_SCHEMA, example_path))
        if example.get("preserveRawFirst") is not True:
            failures.append(f"{example_path.relative_to(ROOT)} preserveRawFirst must be true")
        if example.get("requiresRedactionReview") is not True:
            failures.append(f"{example_path.relative_to(ROOT)} requiresRedactionReview must be true")

    missing_surfaces = REQUIRED_SURFACES - seen_surfaces
    if missing_surfaces:
        failures.append(f"missing AI chat source surfaces: {sorted(missing_surfaces)}")

    failures.extend(validate(DOC_SCHEMA, DOC_EXAMPLE))
    doc = json.loads(DOC_EXAMPLE.read_text())
    formats = {item.get("format") for item in doc.get("documentDerivatives", [])}
    for required_format in ("markdown", "jsonl", "chunk-manifest"):
        if required_format not in formats:
            failures.append(f"conversation document missing derivative format: {required_format}")

    if failures:
        for failure in failures:
            print(f"ERR: {failure}")
        return 1

    print("OK: AI chat export contract fixtures are valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
