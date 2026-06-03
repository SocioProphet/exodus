#!/usr/bin/env python3
"""Run a synthetic exodus-intake smoke test.

This test intentionally operates only on a synthetic fixture committed under
examples/intake. It verifies that the intake command computes SHA-256 over raw
bytes, preserves the original filename, and writes initial metadata/custody
records before any examination output exists.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "examples" / "intake" / "sample-console.txt"
EXPECTED_SHA256 = hashlib.sha256(SOURCE.read_bytes()).hexdigest()


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def main() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        out_dir = Path(tmp)
        cmd = [
            sys.executable,
            str(ROOT / "scripts" / "exodus_intake.py"),
            str(SOURCE),
            "--out-dir",
            str(out_dir),
            "--corpus-id",
            "SP-SYNTHETIC-TESTS",
            "--exhibit-id",
            "AF-9001",
            "--source-account",
            "synthetic@socioprophet.invalid",
            "--source-platform",
            "LocalFilesystem",
            "--source-path-or-id",
            "examples/intake/sample-console.txt",
            "--artifact-class",
            "ConsolePaste",
            "--capture-method",
            "ManualCopy",
            "--artifact-id",
            "018f3f72-6b79-7c35-8f7d-4a3a7d2d9001",
            "--event-id",
            "018f3f72-6b79-7c35-8f7d-4a3a7d2d9002",
            "--timestamp-micros",
            "1780000000000000",
            "--allow-pending-blake3",
        ]
        subprocess.run(cmd, cwd=ROOT, check=True)

        artifact = load_json(out_dir / "AF-9001.evidence-artifact.json")
        event = load_json(out_dir / "AF-9001.custody-event.intake.json")

    assert artifact["original_filename"] == "sample-console.txt"
    assert artifact["hash_sha256"] == EXPECTED_SHA256
    assert len(artifact["hash_blake3"]) == 64
    assert artifact["integrity_status"] in {"Verified", "PendingVerification"}
    assert artifact["owning_zone"] == "Landing"
    assert artifact["source_path_or_id"] == "examples/intake/sample-console.txt"
    assert event["event_type"] == "Intake"
    assert event["artifact_id"] == artifact["artifact_id"]
    assert event["zone_to"] == "Landing"
    assert event["hash_at_event"] == artifact["hash_blake3"]

    print("validated synthetic exodus-intake acquisition path")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
