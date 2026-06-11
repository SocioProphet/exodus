#!/usr/bin/env python3
"""Run all Exodus evidence-fabric validators including owned-media attestation."""

from __future__ import annotations

from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
VALIDATORS = [
    "validate_evidence_dashboard_state.py",
    "validate_evidence_fabric_dashboard_contracts.py",
    "validate_notes_source_profiles.py",
    "validate_owned_media_source_profile.py",
    "validate_owned_media_attestation_record.py",
]


def main() -> int:
    failures: list[str] = []

    for name in VALIDATORS:
        path = ROOT / "scripts" / name
        if not path.exists():
            failures.append(f"missing validator: scripts/{name}")
            continue
        result = subprocess.run(
            [sys.executable, str(path)],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
        print(result.stdout, end="")
        if result.returncode != 0:
            failures.append(f"validator failed: scripts/{name}")

    if failures:
        for failure in failures:
            print(f"ERR: {failure}")
        return 1

    print("OK: complete Exodus evidence-fabric validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
