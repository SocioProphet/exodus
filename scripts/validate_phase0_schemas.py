#!/usr/bin/env python3
"""Validate Phase 0 metadata-standard schema artifacts.

This intentionally uses only the Python standard library so CI can run without
network access or dependency installation. It performs structural checks for
invalid JSON, missing schema files, missing registry classes, missing route
checks, and invalid fixture shape. Full JSON Schema validation can be added once
repo dependency policy is set.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_JSON_FILES = [
    "schemas/evidence-artifact.json",
    "schemas/custody-event.json",
    "schemas/policy-gate.json",
    "schemas/document-type-registry.schema.json",
    "schemas/document-type-registry.json",
    "schemas/forensic-bundle.json",
    "schemas/serializer-spec.json",
    "examples/valid-evidence-artifact.json",
]

REQUIRED_ARTIFACT_CLASSES = {
    "AC-01": "RawLog",
    "AC-02": "ConsolePaste",
    "AC-03": "Spindump",
    "AC-04": "BinaryPlist",
    "AC-05": "EmailThread",
    "AC-06": "LegalFiling",
    "AC-07": "AnalysisReport",
    "AC-08": "DerivedReport",
    "AC-09": "AuditRecord",
    "AC-10": "NetworkCapture",
    "AC-11": "FirmwareDump",
    "AC-12": "AppleDataArchive",
}

REQUIRED_CHECKS = {f"CHK-{i:02d}" for i in range(1, 11)}


def load_json(path: str) -> Any:
    full = ROOT / path
    if not full.exists():
        raise SystemExit(f"missing required file: {path}")
    with full.open("r", encoding="utf-8") as handle:
        try:
            return json.load(handle)
        except json.JSONDecodeError as exc:
            raise SystemExit(f"invalid JSON in {path}: {exc}") from exc


def assert_has_required_keys(name: str, obj: dict[str, Any], keys: set[str]) -> None:
    missing = keys.difference(obj)
    if missing:
        raise SystemExit(f"{name} missing required keys: {sorted(missing)}")


def validate_registry(registry: dict[str, Any]) -> None:
    assert_has_required_keys(
        "document-type registry",
        registry,
        {"registry_version", "source_spec", "artifact_classes", "document_routes"},
    )

    by_id = {entry.get("class_id"): entry.get("name") for entry in registry["artifact_classes"]}
    for class_id, class_name in REQUIRED_ARTIFACT_CLASSES.items():
        if by_id.get(class_id) != class_name:
            raise SystemExit(f"registry missing {class_id} => {class_name}")

    for route in registry["document_routes"]:
        gates = set(route.get("landing_gate", []))
        unknown = gates.difference(REQUIRED_CHECKS)
        if unknown:
            raise SystemExit(f"route {route.get('document_type')} uses unknown checks: {sorted(unknown)}")


def validate_fixture(fixture: dict[str, Any]) -> None:
    required = {
        "artifact_id",
        "corpus_id",
        "exhibit_id",
        "original_filename",
        "hash_blake3",
        "hash_sha256",
        "source_account",
        "source_platform",
        "artifact_class",
        "evidence_class",
        "evidence_grade",
        "owning_zone",
    }
    assert_has_required_keys("valid-evidence-artifact fixture", fixture, required)
    if len(fixture["hash_blake3"]) != 64:
        raise SystemExit("fixture hash_blake3 must be 64 hex characters")
    if len(fixture["hash_sha256"]) != 64:
        raise SystemExit("fixture hash_sha256 must be 64 hex characters")


def main() -> None:
    loaded = {path: load_json(path) for path in REQUIRED_JSON_FILES}
    validate_registry(loaded["schemas/document-type-registry.json"])
    validate_fixture(loaded["examples/valid-evidence-artifact.json"])
    print("validated Phase 0 metadata-standard schema pack")


if __name__ == "__main__":
    main()
