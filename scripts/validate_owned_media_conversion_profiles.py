#!/usr/bin/env python3
"""Validate owned-media conversion profile fixtures."""

from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "packages" / "contracts" / "owned-media-conversion-profile.schema.json"
EXAMPLES = sorted((ROOT / "examples").glob("owned-media-conversion-profile.*.example.json"))

REQUIRED_PROFILES = {
    "audio-archive-flac",
    "audio-portable-opus",
    "video-archive-mkv",
    "video-compatible-mp4",
}


def main() -> int:
    schema = json.loads(SCHEMA.read_text())
    validator = Draft202012Validator(schema)
    failures: list[str] = []
    seen_profiles: set[str] = set()

    if not EXAMPLES:
        failures.append("no owned-media conversion profile examples found")

    for example_path in EXAMPLES:
        example = json.loads(example_path.read_text())
        seen_profiles.add(example.get("profileName", ""))
        for error in sorted(validator.iter_errors(example), key=lambda err: list(err.path)):
            path = ".".join(str(part) for part in error.path) or "<root>"
            failures.append(f"{example_path.relative_to(ROOT)} {path}: {error.message}")
        if example.get("rawCustodyRequired") is not True:
            failures.append(f"{example_path.relative_to(ROOT)} rawCustodyRequired must be true")
        if example.get("attestationRequired") is not True:
            failures.append(f"{example_path.relative_to(ROOT)} attestationRequired must be true")
        if example.get("distributionClearanceRequired") is not False:
            failures.append(f"{example_path.relative_to(ROOT)} private conversion profiles must not require distribution clearance")

    missing_profiles = REQUIRED_PROFILES - seen_profiles
    if missing_profiles:
        failures.append(f"missing required profiles: {sorted(missing_profiles)}")

    if failures:
        for failure in failures:
            print(f"ERR: {failure}")
        return 1

    print("OK: owned media conversion profile fixtures are valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
