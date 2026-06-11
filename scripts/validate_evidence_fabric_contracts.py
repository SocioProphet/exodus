#!/usr/bin/env python3
"""Run all Exodus evidence-fabric contract validators."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VALIDATORS = [
    ROOT / "scripts" / "validate_evidence_dashboard_state.py",
    ROOT / "scripts" / "validate_evidence_fabric_dashboard_contracts.py",
    ROOT / "scripts" / "validate_notes_source_profiles.py",
]


def main() -> int:
    failures: list[str] = []

    for validator in VALIDATORS:
        if not validator.exists():
            failures.append(f"missing validator: {validator.relative_to(ROOT)}")
            continue
        result = subprocess.run(
            [sys.executable, str(validator)],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
        print(result.stdout, end="")
        if result.returncode != 0:
            failures.append(f"validator failed: {validator.relative_to(ROOT)}")

    if failures:
        for failure in failures:
            print(f"ERR: {failure}")
        return 1

    print("OK: all Exodus evidence-fabric contract validators passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
