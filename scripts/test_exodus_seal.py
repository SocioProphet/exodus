#!/usr/bin/env python3
"""Tests for the forensic sealing layer — this IS the legal replay harness.

Run: python3 scripts/test_exodus_seal.py
Requires: cryptography, blake3.

Proves: (1) a committed sealed receipt replays byte-for-byte from its inputs,
(2) sealed records verify from the JSON + public key alone (FRE 902(14)),
(3) any tamper to payload, receipt metadata, or bundle is detected.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path

import exodus_seal as seal
import exodus_bundle as bundle

ROOT = Path(__file__).resolve().parents[1]
FX = ROOT / "tests/sealing-fixtures"
# The signing key is DERIVED from a committed seed at runtime — no private key is
# committed to the repo. Derivation: private_key_ed25519 = sha256(seed).
import hashlib
_SEED = json.loads((FX / "test-signing-seed.json").read_text())
KEY = {
    "private_key_ed25519": hashlib.sha256(_SEED["seed"].encode("utf-8")).hexdigest(),
    "public_key_ed25519": _SEED["public_key_ed25519"],
}
EVENT = json.loads((FX / "custody-event.input.json").read_text())
RECEIPT = json.loads((FX / "custody-event.receipt.json").read_text())
BUNDLE = json.loads((FX / "forensic-bundle.json").read_text())


def test_canonical_is_byte_stable() -> None:
    a = seal.canonical_bytes({"b": 1, "a": [3, 2]})
    b = seal.canonical_bytes({"a": [3, 2], "b": 1})
    assert a == b == b'{"a":[3,2],"b":1}'


def test_receipt_replays_byte_for_byte() -> None:
    # Re-seal the committed input with the committed key + timestamp -> identical receipt.
    replay = seal.seal(EVENT, private_key_hex=KEY["private_key_ed25519"],
                       key_id=RECEIPT["key_id"], signer_id=RECEIPT["signer_id"],
                       sealed_at_micros=RECEIPT["sealed_at_micros"])
    assert seal.canonical_bytes(replay) == seal.canonical_bytes(RECEIPT), "receipt did not replay byte-for-byte"


def test_committed_receipt_verifies_from_public_key_alone() -> None:
    ok, why = seal.verify_receipt(EVENT, RECEIPT)
    assert ok, why
    # The receipt carries its own public key; no private key needed to verify.
    assert RECEIPT["public_key_ed25519"] == KEY["public_key_ed25519"]


def test_payload_tamper_is_detected() -> None:
    bad = copy.deepcopy(EVENT)
    bad["zone_to"] = "Governed"  # silent custody escalation
    ok, why = seal.verify_receipt(bad, RECEIPT)
    assert not ok and "frame hash" in why


def test_receipt_metadata_tamper_is_detected() -> None:
    bad = copy.deepcopy(RECEIPT)
    bad["signer_id"] = "attacker"  # re-bind the signature to a different signer
    ok, why = seal.verify_receipt(EVENT, bad)
    assert not ok and "signature" in why


def test_signature_tamper_is_detected() -> None:
    bad = copy.deepcopy(RECEIPT)
    bad["signature_ed25519"] = "00" + bad["signature_ed25519"][2:]
    ok, _ = seal.verify_receipt(EVENT, bad)
    assert not ok


def test_bundle_verifies_independently() -> None:
    ok, reasons = bundle.verify_bundle(BUNDLE)
    assert ok, reasons


def test_bundle_manifest_hash_tamper_is_detected() -> None:
    bad = copy.deepcopy(BUNDLE)
    bad["bundle_manifest"][0]["hash_blake3"] = "c" * 64
    ok, reasons = bundle.verify_bundle(bad)
    assert not ok and reasons


def test_bundle_core_tamper_breaks_hash_and_signature() -> None:
    bad = copy.deepcopy(BUNDLE)
    bad["case_id"] = "TAMPERED"
    ok, reasons = bundle.verify_bundle(bad)
    assert not ok
    assert any("bundle_hash" in r for r in reasons) and any("BEACON_COMMIT" in r for r in reasons)


def test_bundle_signature_swap_is_detected() -> None:
    bad = copy.deepcopy(BUNDLE)
    bad["bundle_signature"] = "00" + bad["bundle_signature"][2:]
    ok, reasons = bundle.verify_bundle(bad)
    assert not ok and any("signature" in r for r in reasons)


def main() -> None:
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    for t in tests:
        t()
    print(f"OK: exodus_seal + exodus_bundle replay harness — {len(tests)} tests passed")


if __name__ == "__main__":
    main()
