#!/usr/bin/env python3
"""ForensicBundle export + independent verification (Metadata Standards §10).

A ForensicBundle is the court-presentable package: a signed, hash-sealed,
self-describing record that lets an independent party verify every included
artifact's integrity and the bundle's own integrity **without access to the
platform** — only the embedded public key. Build it with `build_bundle`; verify
it with `verify_bundle` (which an opposing expert can run from the JSON alone).

Primary hash is BLAKE3-256 (with SHA-256 alongside for NIST-standard court
copies), sealed by an Ed25519 BEACON_COMMIT receipt over the canonical bundle
core. Conforms to schemas/forensic-bundle.json.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import sys
import uuid
from pathlib import Path
from typing import Any

import exodus_seal as seal

# fields computed FROM the core; excluded when (re)hashing/sealing.
_DERIVED = {"bundle_hash_blake3", "bundle_hash_sha256", "bundle_signature", "trpc_commit_receipt"}
TOOL_NAME = "exodus-bundle"
TOOL_VERSION = "0.1.0"


def _blake3_hex(data: bytes) -> str:
    try:
        import blake3  # type: ignore
    except Exception as exc:
        raise seal.SealError(
            "ForensicBundle requires the `blake3` package for the primary hash (pip install blake3)"
        ) from exc
    return blake3.blake3(data).hexdigest()


def _snapshot_event(e: dict[str, Any]) -> dict[str, Any]:
    """Project a CustodyEvent into the compact snapshot the bundle schema allows."""
    if not e.get("hash_at_event"):
        raise seal.SealError(f"custody event {e.get('event_id')} lacks hash_at_event (required in a bundle snapshot)")
    snap = {
        "event_id": e["event_id"],
        "artifact_id": e["artifact_id"],
        "hash_at_event": e["hash_at_event"],
        "timestamp_micros": e["timestamp_micros"],
    }
    if e.get("trpc_commit_receipt") is not None:
        snap["trpc_commit_receipt"] = e["trpc_commit_receipt"]
    return snap


def _member(artifact: dict[str, Any]) -> dict[str, Any]:
    m = {
        "artifact_id": artifact["artifact_id"],
        "exhibit_id": artifact["exhibit_id"],
        "hash_blake3": artifact["hash_blake3"],
    }
    if artifact.get("hash_sha256"):
        m["hash_sha256"] = artifact["hash_sha256"]
    if artifact.get("original_filename"):
        m["original_filename"] = artifact["original_filename"]
    return m


def build_bundle(
    *,
    case_id: str,
    artifacts: list[dict[str, Any]],
    custody_events: list[dict[str, Any]],
    private_key_hex: str,
    key_id: str,
    signer_id: str,
    serializer_spec: str,
    bundle_id: str | None = None,
    bundle_version: int = 1,
    generated_by: str,
    generated_at_micros: int | None = None,
    disclosure_authorization: str | None = None,
    tool_versions: list[str] | None = None,
    fixture_paths: list[str] | None = None,
) -> dict[str, Any]:
    members = [_member(a) for a in artifacts]
    core: dict[str, Any] = {
        "bundle_id": bundle_id or str(uuid.uuid4()),
        "case_id": case_id,
        "bundle_version": bundle_version,
        "serializer_spec": serializer_spec,
        "hash_algorithm": "BLAKE3-256+SHA-256",
        "bundle_manifest": members,
        "custody_chain_snapshot": [_snapshot_event(e) for e in custody_events],
        "replay_manifest": {
            "serializer_version": serializer_spec,
            "tool_versions": tool_versions or [f"{TOOL_NAME} {TOOL_VERSION}", "ed25519", "blake3-256"],
            "fixture_paths": fixture_paths or [],
            "expected_hashes": [m["hash_blake3"] for m in members],
        },
        "signing_key_ref": f"{key_id}; alg=Ed25519",
        "generated_at_micros": generated_at_micros if generated_at_micros is not None else seal.now_micros(),
        "generated_by": generated_by,
    }
    if disclosure_authorization is not None:
        core["disclosure_authorization"] = disclosure_authorization

    core_bytes = seal.canonical_bytes(core)
    receipt = seal.seal(core, private_key_hex=private_key_hex, key_id=key_id,
                        signer_id=signer_id, sealed_at_micros=core["generated_at_micros"])
    return {
        **core,
        "bundle_hash_blake3": _blake3_hex(core_bytes),
        "bundle_hash_sha256": hashlib.sha256(core_bytes).hexdigest(),
        "bundle_signature": receipt["signature_ed25519"],
        "trpc_commit_receipt": seal.canonical_bytes(receipt).hex(),
    }


def verify_bundle(bundle: dict[str, Any]) -> tuple[bool, list[str]]:
    """Independent verification from the JSON alone. Fail-closed."""
    reasons: list[str] = []
    core = {k: v for k, v in bundle.items() if k not in _DERIVED}
    core_bytes = seal.canonical_bytes(core)

    if hashlib.sha256(core_bytes).hexdigest() != bundle.get("bundle_hash_sha256"):
        reasons.append("bundle_hash_sha256 does not match recomputed core hash")
    try:
        if _blake3_hex(core_bytes) != bundle.get("bundle_hash_blake3"):
            reasons.append("bundle_hash_blake3 does not match recomputed core hash")
    except seal.SealError:
        reasons.append("blake3 unavailable: cannot verify primary bundle hash")

    # Re-derive and verify the BEACON_COMMIT receipt over the core.
    try:
        receipt = json.loads(bytes.fromhex(bundle.get("trpc_commit_receipt", "")).decode("utf-8"))
    except Exception:
        reasons.append("trpc_commit_receipt is not decodable")
        receipt = None
    if receipt is not None:
        ok, why = seal.verify_receipt(core, receipt)
        if not ok:
            reasons.append(f"BEACON_COMMIT receipt failed: {why}")
        if receipt.get("signature_ed25519") != bundle.get("bundle_signature"):
            reasons.append("bundle_signature does not match the sealed receipt signature")

    # Internal consistency: every manifest member hash is declared for replay.
    expected = set(bundle.get("replay_manifest", {}).get("expected_hashes", []))
    for m in bundle.get("bundle_manifest", []):
        if m.get("hash_blake3") not in expected:
            reasons.append(f"manifest member {m.get('exhibit_id')} hash absent from replay expected_hashes")

    return (not reasons), reasons


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Build or verify an Exodus ForensicBundle.")
    sub = p.add_subparsers(dest="cmd", required=True)
    v = sub.add_parser("verify", help="independently verify a bundle from its JSON")
    v.add_argument("--bundle", required=True)
    args = p.parse_args(argv if argv is not None else sys.argv[1:])
    if args.cmd == "verify":
        bundle = json.loads(Path(args.bundle).read_text(encoding="utf-8"))
        ok, reasons = verify_bundle(bundle)
        print(json.dumps({"verified": ok, "reasons": reasons}, indent=2))
        return 0 if ok else 1
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
