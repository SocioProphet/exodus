#!/usr/bin/env python3
"""Validate Exodus owned-media source profile fixtures."""

from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "packages" / "contracts" / "owned-media-source-profile.schema.json"
EXAMPLE = ROOT / "examples" / "owned-media-source-profile.example.json"

REQUIRED_MEDIA_KINDS = {"music", "video"}
REQUIRED_TARGETS = {
    "audioArchival",
    "audioPortable",
    "videoArchivalContainer",
    "videoCompatibilityContainer",
    "metadataSidecar",
}


def main() -> int:
    schema = json.loads(SCHEMA.read_text())
    example = json.loads(EXAMPLE.read_text())
    validator = Draft202012Validator(schema)
    failures: list[str] = []

    for error in sorted(validator.iter_errors(example), key=lambda err: list(err.path)):
        path = ".".join(str(part) for part in error.path) or "<root>"
        failures.append(f"{EXAMPLE.relative_to(ROOT)} {path}: {error.message}")

    media_kinds = set(example.get("mediaKinds", []))
    missing_media = REQUIRED_MEDIA_KINDS - media_kinds
    if missing_media:
        failures.append(f"missing required media kinds: {sorted(missing_media)}")

    preferred_targets = set((example.get("preferredTargets") or {}).keys())
    missing_targets = REQUIRED_TARGETS - preferred_targets
    if missing_targets:
        failures.append(f"missing required conversion targets: {sorted(missing_targets)}")

    if example.get("preserveRawFirst") is not True:
        failures.append("preserveRawFirst must be true")

    if example.get("drmPolicy") not in {"blocked-or-metadata-only", "authorized-export-only"}:
        failures.append("drmPolicy must block bypass behavior")

    if failures:
        for failure in failures:
            print(f"ERR: {failure}")
        return 1

    print("OK: owned media source profile fixture is valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
