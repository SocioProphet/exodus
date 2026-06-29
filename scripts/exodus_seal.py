#!/usr/bin/env python3
"""Exodus forensic sealing — the cryptographic custody layer.

This is the TriTRPC BEACON_COMMIT binding for Exodus: it seals a CustodyEvent or
a ForensicBundle with a content frame-hash and a detached Ed25519 signature, so
that any party holding only the public key can independently verify that a
sealed record has not been altered — the "independently verifiable" requirement
of FRE 902(14). Ed25519 is deterministic (RFC 8032), and the canonical
serialization is byte-stable, so a sealed receipt replays bit-for-bit: this is
the legal replay harness, not a test convenience.

Design:
- Canonicalization: CANON-v0.1 = JSON with sorted keys, no whitespace, UTF-8
  (consistent with the shipped intake/gate hashing). The serializer-spec is
  versioned precisely so the encoding can evolve (e.g. deterministic CBOR)
  without breaking older receipts.
- Frame hash: BLAKE3-256 when the `blake3` package is available; otherwise
  SHA-256, always recorded explicitly in `frame_hash_algo`. (TriTRPC's wire
  frame hash is BLAKE3-256; the evidentiary primitive is the signature.)
- Signature: Ed25519 over a canonical "commit statement" that binds the content
  frame-hash to the signer identity and the sealing time, preventing re-binding
  of a signature to different metadata.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

CANONICALIZATION_SPEC = "CANON-v0.1"
RECEIPT_TYPE = "BEACON_COMMIT"


class SealError(RuntimeError):
    pass


def now_micros() -> int:
    return int(dt.datetime.now(dt.timezone.utc).timestamp() * 1_000_000)


# ── Canonicalization + frame hash ────────────────────────────────────────────
def canonical_bytes(obj: Any) -> bytes:
    """CANON-v0.1: sorted-key, whitespace-free, UTF-8 JSON. Byte-stable."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def frame_hash(data: bytes) -> tuple[str, str]:
    """Return (algo, hexdigest). Prefer BLAKE3-256; fall back to SHA-256, labeled."""
    try:
        import blake3  # type: ignore

        return "BLAKE3-256", blake3.blake3(data).hexdigest()
    except Exception:
        return "SHA-256", hashlib.sha256(data).hexdigest()


def content_frame_hash(payload: Any) -> tuple[str, str]:
    return frame_hash(canonical_bytes(payload))


# ── Ed25519 (lazy import so this module loads without `cryptography`) ─────────
def _ed25519():
    try:
        from cryptography.hazmat.primitives import serialization
        from cryptography.hazmat.primitives.asymmetric.ed25519 import (
            Ed25519PrivateKey,
            Ed25519PublicKey,
        )

        return serialization, Ed25519PrivateKey, Ed25519PublicKey
    except Exception as exc:  # pragma: no cover - exercised only without the dep
        raise SealError(
            "ed25519 signing requires the `cryptography` package (pip install cryptography)"
        ) from exc


def generate_keypair() -> tuple[str, str]:
    """Return (private_key_hex, public_key_hex) — raw 32-byte keys, hex-encoded."""
    serialization, Ed25519PrivateKey, _ = _ed25519()
    sk = Ed25519PrivateKey.generate()
    raw_priv = sk.private_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PrivateFormat.Raw,
        encryption_algorithm=serialization.NoEncryption(),
    )
    raw_pub = sk.public_key().public_bytes(
        encoding=serialization.Encoding.Raw, format=serialization.PublicFormat.Raw
    )
    return raw_priv.hex(), raw_pub.hex()


def public_key_for(private_key_hex: str) -> str:
    serialization, Ed25519PrivateKey, _ = _ed25519()
    sk = Ed25519PrivateKey.from_private_bytes(bytes.fromhex(private_key_hex))
    return sk.public_key().public_bytes(
        encoding=serialization.Encoding.Raw, format=serialization.PublicFormat.Raw
    ).hex()


def _sign(private_key_hex: str, data: bytes) -> str:
    _, Ed25519PrivateKey, _ = _ed25519()
    sk = Ed25519PrivateKey.from_private_bytes(bytes.fromhex(private_key_hex))
    return sk.sign(data).hex()


def _verify(public_key_hex: str, data: bytes, signature_hex: str) -> bool:
    _, _, Ed25519PublicKey = _ed25519()
    try:
        Ed25519PublicKey.from_public_bytes(bytes.fromhex(public_key_hex)).verify(
            bytes.fromhex(signature_hex), data
        )
        return True
    except Exception:
        return False


# ── The commit statement (what the signature actually covers) ─────────────────
def _commit_statement(frame_hash_algo: str, fh: str, signer_id: str, key_id: str, sealed_at: int) -> dict[str, Any]:
    """The canonical object the signature binds: content hash ↔ signer ↔ time."""
    return {
        "canonicalization_spec": CANONICALIZATION_SPEC,
        "frame_hash": fh,
        "frame_hash_algo": frame_hash_algo,
        "key_id": key_id,
        "receipt_type": RECEIPT_TYPE,
        "sealed_at_micros": sealed_at,
        "signer_id": signer_id,
    }


def seal(
    payload: dict[str, Any],
    *,
    private_key_hex: str,
    key_id: str,
    signer_id: str,
    sealed_at_micros: int | None = None,
) -> dict[str, Any]:
    """Produce a BEACON_COMMIT receipt sealing `payload`. Deterministic for fixed
    inputs (incl. sealed_at_micros), so receipts replay byte-for-byte."""
    algo, fh = content_frame_hash(payload)
    sealed_at = sealed_at_micros if sealed_at_micros is not None else now_micros()
    statement = _commit_statement(algo, fh, signer_id, key_id, sealed_at)
    signature = _sign(private_key_hex, canonical_bytes(statement))
    return {
        **statement,
        "public_key_ed25519": public_key_for(private_key_hex),
        "signature_ed25519": signature,
    }


def verify_receipt(payload: dict[str, Any], receipt: dict[str, Any]) -> tuple[bool, str]:
    """Independent verification: recompute the content frame hash, rebuild the
    commit statement from the receipt's own fields, and check the Ed25519
    signature with the receipt's embedded public key. Fail-closed."""
    if receipt.get("receipt_type") != RECEIPT_TYPE:
        return False, "not a BEACON_COMMIT receipt"
    algo = receipt.get("frame_hash_algo")
    # Recompute the content hash using the receipt's declared algorithm.
    if algo == "BLAKE3-256":
        try:
            import blake3  # type: ignore

            recomputed = blake3.blake3(canonical_bytes(payload)).hexdigest()
        except Exception:
            return False, "receipt is BLAKE3-sealed but blake3 is unavailable to verify"
    elif algo == "SHA-256":
        recomputed = hashlib.sha256(canonical_bytes(payload)).hexdigest()
    else:
        return False, f"unknown frame_hash_algo {algo!r}"
    if recomputed != receipt.get("frame_hash"):
        return False, "content frame hash does not match receipt (payload altered)"
    statement = _commit_statement(
        algo, receipt["frame_hash"], receipt.get("signer_id"), receipt.get("key_id"),
        receipt.get("sealed_at_micros"),
    )
    if not _verify(receipt.get("public_key_ed25519", ""), canonical_bytes(statement), receipt.get("signature_ed25519", "")):
        return False, "Ed25519 signature does not verify (receipt metadata or signature altered)"
    return True, "sealed and verified"


# ── CLI ──────────────────────────────────────────────────────────────────────
def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Exodus forensic sealing (BEACON_COMMIT).")
    sub = p.add_subparsers(dest="cmd", required=True)
    kg = sub.add_parser("keygen", help="generate an Ed25519 keypair (hex)")
    s = sub.add_parser("seal", help="seal a JSON payload, emit a BEACON_COMMIT receipt")
    s.add_argument("--payload", required=True)
    s.add_argument("--private-key", required=True, help="hex private key (or @path)")
    s.add_argument("--key-id", required=True)
    s.add_argument("--signer-id", required=True)
    s.add_argument("--sealed-at-micros", type=int, default=None)
    s.add_argument("--out", default=None)
    v = sub.add_parser("verify", help="verify a payload against a receipt")
    v.add_argument("--payload", required=True)
    v.add_argument("--receipt", required=True)
    args = p.parse_args(argv if argv is not None else sys.argv[1:])

    if args.cmd == "keygen":
        priv, pub = generate_keypair()
        print(json.dumps({"private_key_ed25519": priv, "public_key_ed25519": pub}, indent=2))
        return 0
    if args.cmd == "seal":
        pk = args.private_key
        if pk.startswith("@"):
            pk = Path(pk[1:]).read_text().strip()
        payload = json.loads(Path(args.payload).read_text(encoding="utf-8"))
        receipt = seal(payload, private_key_hex=pk, key_id=args.key_id,
                       signer_id=args.signer_id, sealed_at_micros=args.sealed_at_micros)
        out = json.dumps(receipt, indent=2, sort_keys=True)
        if args.out:
            Path(args.out).write_text(out + "\n", encoding="utf-8")
        print(out)
        return 0
    if args.cmd == "verify":
        payload = json.loads(Path(args.payload).read_text(encoding="utf-8"))
        receipt = json.loads(Path(args.receipt).read_text(encoding="utf-8"))
        ok, reason = verify_receipt(payload, receipt)
        print(json.dumps({"verified": ok, "reason": reason}, indent=2))
        return 0 if ok else 1
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
