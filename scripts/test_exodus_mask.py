#!/usr/bin/env python3
"""Dependency-free tests for the Exodus masking PDP.

Run: python3 scripts/test_exodus_mask.py
Proves: the no_health_adtech veto, allow_masked tokenization, reason-gated
re-identification, and that the emitted decision carries a verifiable BEACON_COMMIT
receipt when a signing key is supplied.
"""
from __future__ import annotations

import json
import sys

import exodus_seal
from exodus_mask import evaluate_masking

POLICY = {
    "policy_id": "GATE-mask-v1",
    "policy_version": "regis.identity.polytope.core@0.1.0",
    "forbidden_mixtures": [["patient", "ad_tech"]],
}
MK = b"unit-test-master-key"


def test_health_adtech_veto():
    rec = {"mrn": "MRN-1", "primes": ["patient"]}
    masked, d = evaluate_masking(rec, subject_ref="ce_patient_1", requesting_realm="ADTECH",
                                 policy=POLICY, master_key=MK)
    assert d["verdict"] == "deny", d["verdict"]
    assert d["forbidden_mixture"] == ["patient", "ad_tech"]
    assert masked is None, "denied access must not return a record"


def test_allow_masked_tokenizes_field():
    rec = {"mrn": "MRN-12345", "primes": ["learning"]}
    profiles = {"mrn": {"profile_id": "tp_mrn", "scheme": "chameleon_token", "domain_scope": "CITIZEN_CLOUD", "key": {"key_epoch": 0}}}
    masked, d = evaluate_masking(rec, subject_ref="ce_1", requesting_realm="CITIZEN_CLOUD",
                                 profiles=profiles, policy=POLICY, master_key=MK)
    assert d["verdict"] == "allow_masked", d["verdict"]
    assert masked["mrn"] != "MRN-12345", "field must be tokenized"
    assert d["applied_transforms"][0]["scheme"] == "chameleon_token"
    assert d["receipt"]["certificate_hash"], "decision must carry a certificate hash"


def test_reidentify_requires_reason_and_authz():
    rec = {"mrn": "tok_abc", "primes": ["patient"]}
    # missing reason + authz -> review_required (note: patient alone, INSTITUTION realm, no forbidden mix)
    _, d = evaluate_masking(rec, subject_ref="s", requesting_realm="INSTITUTION",
                            requested_op="re_identify", policy={"forbidden_mixtures": []}, master_key=MK)
    assert d["verdict"] == "review_required", d["verdict"]
    # authorized + reason -> allow
    aud = {"role": "legal_counsel", "openid_profile_attr": "can_reidentify=true", "authorized_by": "custodian"}
    _, d2 = evaluate_masking(rec, subject_ref="s", requesting_realm="INSTITUTION", audience=aud,
                             requested_op="re_identify", reason_for_action="subpoena AF-0007",
                             policy={"forbidden_mixtures": []}, master_key=MK)
    assert d2["verdict"] == "allow", d2["verdict"]
    assert d2["re_identification"]["permitted"] is True
    assert d2["re_identification"]["reason_for_action"] == "subpoena AF-0007"


def test_signed_receipt_verifies():
    priv, _pub = exodus_seal.generate_keypair()
    rec = {"mrn": "MRN-9", "primes": ["learning"]}
    profiles = {"mrn": {"scheme": "one_way_hash"}}
    _, d = evaluate_masking(rec, subject_ref="ce_9", requesting_realm="CITIZEN_CLOUD", profiles=profiles,
                            policy=POLICY, master_key=MK, signing_key_hex=priv, now_micros=1780000000000000)
    receipt = json.loads(d["receipt"]["beacon_commit_receipt"])
    core = {k: d[k] for k in ("decision_id", "subject_ref", "requesting_realm", "requested_op", "verdict", "forbidden_mixture", "applied_transforms")}
    ok, msg = exodus_seal.verify_receipt(core, receipt)
    assert ok, f"BEACON_COMMIT receipt must verify: {msg}"


def test_decision_shape():
    rec = {"x": "1234567890", "primes": []}
    _, d = evaluate_masking(rec, subject_ref="s", requesting_realm="CITIZEN_CLOUD", policy=POLICY, master_key=MK)
    for key in ("schema_version", "decision_id", "subject_ref", "requesting_realm", "requested_op",
                "verdict", "applied_transforms", "receipt", "policy_version", "decided_by", "created_at"):
        assert key in d, f"missing {key}"
    assert d["schema_version"] == "identity-prime.masking-decision.v1"
    assert d["decision_id"].startswith("md_")


def main() -> int:
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    failed = 0
    for t in tests:
        try:
            t()
            print(f"  PASS  {t.__name__}")
        except AssertionError as e:
            failed += 1
            print(f"  FAIL  {t.__name__}: {e}")
    if failed:
        print(f"masking PDP: FAIL ({failed}/{len(tests)})")
        return 1
    print(f"masking PDP: PASS ({len(tests)} tests)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
