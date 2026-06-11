#!/usr/bin/env python3
"""Run all Exodus evidence-fabric validators staged in the contract bootstrap."""

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
    "validate_owned_media_conversion_profiles.py",
    "validate_playlist_migration_record.py",
    "validate_ai_chat_export_contracts.py",
    "validate_conversation_reuse_policy.py",
    "validate_exodus_report_contracts.py",
    "validate_conversion_and_redaction_records.py",
    "validate_exit_readiness_records.py",
]


def main() -> int:
    failures: list[str] = []

    for validator_name in VALIDATORS:
        validator_path = ROOT / "scripts" / validator_name
        if not validator_path.exists():
            failures.append(f"missing validator: scripts/{validator_name}")
            continue

        result = subprocess.run(
            [sys.executable, str(validator_path)],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
        print(result.stdout, end="")
        if result.returncode != 0:
            failures.append(f"validator failed: scripts/{validator_name}")

    if failures:
        for failure in failures:
            print(f"ERR: {failure}")
        return 1

    print("OK: all Exodus evidence-fabric validators passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
