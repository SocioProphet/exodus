#!/usr/bin/env python3
"""Synthetic-safe Exodus artifact intake command.

This command creates an EvidenceArtifact-compatible metadata record and an
initial CustodyEvent-compatible record for a local file. It intentionally avoids
real evidence assumptions: callers must provide source metadata explicitly and
BLAKE3 is only used when the optional dependency is available.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import mimetypes
import sys
import time
import uuid
from pathlib import Path
from typing import Any

ZERO_HASH_32 = "0" * 64
VERSION = "exodus-intake-v0.1.0"

ARTIFACT_CLASSES = [
    "RawLog",
    "ConsolePaste",
    "Spindump",
    "BinaryPlist",
    "EmailThread",
    "LegalFiling",
    "AnalysisReport",
    "DerivedReport",
    "AuditRecord",
    "NetworkCapture",
    "FirmwareDump",
    "AppleDataArchive",
    "Other",
]

SOURCE_PLATFORMS = [
    "GoogleDrive",
    "GmailThread",
    "iCloudDrive",
    "LocalFilesystem",
    "AppleDataArchive",
    "TerminalSession",
    "BrowserConsole",
    "NetworkCapture",
    "Other",
]

CAPTURE_METHODS = ["LiveCapture", "PanicSave", "ScheduledExport", "ManualCopy", "AgentExport", "Unknown"]


def now_micros() -> int:
    return time.time_ns() // 1_000


def read_bytes(path: Path) -> bytes:
    if not path.exists():
        raise SystemExit(f"input path does not exist: {path}")
    if not path.is_file():
        raise SystemExit(f"input path is not a file: {path}")
    return path.read_bytes()


def compute_blake3(raw: bytes) -> tuple[str, str]:
    try:
        import blake3  # type: ignore
    except Exception:
        return ZERO_HASH_32, "unavailable"
    return blake3.blake3(raw).hexdigest(), "computed"


def guess_mime(path: Path) -> str:
    guessed, _ = mimetypes.guess_type(path.name)
    return guessed or "application/octet-stream"


def write_json(path: Path, obj: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_records(args: argparse.Namespace) -> tuple[dict[str, Any], dict[str, Any]]:
    input_path = Path(args.input).resolve()
    raw = read_bytes(input_path)
    timestamp = args.timestamp_micros or now_micros()
    uploaded_at = args.uploaded_at_micros or timestamp
    artifact_id = args.artifact_id or str(uuid.uuid4())
    event_id = args.event_id or str(uuid.uuid4())

    sha256 = hashlib.sha256(raw).hexdigest()
    blake3_hash, blake3_status = compute_blake3(raw)
    if blake3_status == "unavailable" and not args.allow_pending_blake3:
        raise SystemExit(
            "BLAKE3 dependency unavailable. Re-run with --allow-pending-blake3 to write "
            "a PendingVerification record with a zero-hash sentinel."
        )

    integrity_status = "PendingVerification" if blake3_status == "unavailable" else "Verified"
    custody_status = "PendingVerification" if blake3_status == "unavailable" else "Intact"
    hash_tool = args.hash_computed_by or VERSION

    artifact = {
        "artifact_id": artifact_id,
        "artifact_class": args.artifact_class,
        "canonicalization_spec": args.canonicalization_spec,
        "capture_method": args.capture_method,
        "chain_of_trust": [],
        "containing_folder": args.containing_folder,
        "corpus_id": args.corpus_id,
        "counter_explanations": [],
        "custody_status": custody_status,
        "evidence_class": args.evidence_class,
        "evidence_grade": "E3" if integrity_status == "Verified" else "E2",
        "exhibit_id": args.exhibit_id,
        "file_size_bytes": len(raw),
        "hash_blake3": blake3_hash,
        "hash_computed_at_micros": timestamp,
        "hash_computed_by": f"{hash_tool}; blake3={blake3_status}",
        "hash_md5": None,
        "hash_sha256": sha256,
        "hypothesis_ids": [],
        "incident_date_range": None,
        "integrity_status": integrity_status,
        "layer_citations": [],
        "mime_type": args.mime_type or guess_mime(input_path),
        "null_hypothesis_ids": [],
        "observed_at_micros": timestamp,
        "original_filename": input_path.name,
        "owning_zone": "Landing",
        "parent_artifact_id": None,
        "producing_tool": args.producing_tool,
        "security_label": args.security_label,
        "serializer_version": args.serializer_version,
        "signer_atom": None,
        "source_account": args.source_account,
        "source_path_or_id": args.source_path_or_id,
        "source_platform": args.source_platform,
        "txn_created": f"txn-local-{timestamp}",
        "uploaded_at_micros": uploaded_at,
        "valid_from_micros": None,
        "valid_to_micros": None,
        "witness_retention": args.witness_retention,
    }

    event = {
        "actor_id": args.actor_id,
        "actor_type": "IntakeProcess",
        "artifact_id": artifact_id,
        "custody_status": custody_status,
        "event_id": event_id,
        "event_type": "Intake",
        "hash_at_event": blake3_hash,
        "hypothesis_ids": [],
        "note": None if blake3_status == "computed" else "BLAKE3 unavailable; zero hash sentinel; do not treat as verified.",
        "recipient_id": None,
        "timestamp_micros": timestamp,
        "tool_name": VERSION,
        "trpc_commit_receipt": None,
        "zone_from": None,
        "zone_to": "Landing",
    }

    return artifact, event


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create Exodus intake metadata for a local artifact.")
    parser.add_argument("input", help="Local artifact path. Use only synthetic fixtures in repo tests.")
    parser.add_argument("--out-dir", required=True, help="Output directory for metadata records.")
    parser.add_argument("--corpus-id", required=True)
    parser.add_argument("--exhibit-id", required=True)
    parser.add_argument("--source-account", required=True)
    parser.add_argument("--source-platform", required=True, choices=SOURCE_PLATFORMS)
    parser.add_argument("--source-path-or-id", required=True)
    parser.add_argument("--artifact-class", default="Other", choices=ARTIFACT_CLASSES)
    parser.add_argument("--capture-method", default="ManualCopy", choices=CAPTURE_METHODS)
    parser.add_argument("--artifact-id")
    parser.add_argument("--event-id")
    parser.add_argument("--timestamp-micros", type=int)
    parser.add_argument("--uploaded-at-micros", type=int)
    parser.add_argument("--mime-type")
    parser.add_argument("--containing-folder")
    parser.add_argument("--producing-tool")
    parser.add_argument("--evidence-class", default="Primary", choices=["Primary", "Derived", "Duplicate", "Reference", "Unknown"])
    parser.add_argument("--security-label", default="Internal", choices=["Public", "Internal", "Confidential", "Restricted", "LocalOnly"])
    parser.add_argument("--witness-retention", default="LocalOnly", choices=["LocalOnly", "ExportableToLegalCounsel", "ExportableUnderProtectiveOrder", "PublicRecord"])
    parser.add_argument("--canonicalization-spec", default="CANON-v0.1")
    parser.add_argument("--serializer-version", default="serializer-v0.1.0")
    parser.add_argument("--hash-computed-by", default=VERSION)
    parser.add_argument("--actor-id", default=VERSION)
    parser.add_argument("--allow-pending-blake3", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    artifact, event = build_records(args)
    out_dir = Path(args.out_dir)
    write_json(out_dir / f"{args.exhibit_id}.evidence-artifact.json", artifact)
    write_json(out_dir / f"{args.exhibit_id}.custody-event.intake.json", event)
    print(json.dumps({"artifact": artifact["artifact_id"], "evidence_grade": artifact["evidence_grade"], "integrity_status": artifact["integrity_status"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
