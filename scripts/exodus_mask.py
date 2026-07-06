#!/usr/bin/env python3
"""Exodus masking Policy Decision Point (PDP).

Composes the shipped pieces into one enforcement step, evaluated at read / export /
activate / re-identify time:

    policy veto  (forbidden identity mixtures, e.g. no_health_adtech)
      +  exodus_tokenize  (Chameleon / FPE / hash / redact per field profile)
      +  exodus_seal      (BEACON_COMMIT receipt over the decision)
      ->  a masking-decision.v1 record  (the decision is itself verifiable evidence)

Unlike a passive masking rule, every decision carries a policy-decision ref and an
(optional) signed BEACON_COMMIT receipt — the property WKC-style dynamic masking does
not produce. Re-identification is a governed, reason-gated, audited release.

stdlib-only; depends on exodus_tokenize (PR #24) and exodus_seal (on main).
"""
from __future__ import annotations

import argparse
import json
import sys
import uuid
from pathlib import Path
from typing import Any

import exodus_seal
import exodus_tokenize


def _realm_topic(realm: str) -> str | None:
    """Map a requesting realm to the identity topic it implies (for mixture checks)."""
    r = (realm or "").upper()
    if r.startswith("ADTECH"):
        return "ad_tech"
    if r.startswith("INSTITUTION"):
        return "institution"
    return None


def _forbidden_hit(active: set[str], policy: dict[str, Any]) -> list[str] | None:
    for mixture in policy.get("forbidden_mixtures", []):
        if set(mixture) <= active:
            return list(mixture)
    return None


def evaluate_masking(
    record: dict[str, Any],
    *,
    subject_ref: str,
    requesting_realm: str,
    audience: dict[str, Any] | None = None,
    profiles: dict[str, dict[str, Any]] | None = None,
    policy: dict[str, Any] | None = None,
    master_key: bytes = b"reference-master-key",
    requested_op: str = "read",
    reason_for_action: str | None = None,
    signing_key_hex: str | None = None,
    now_micros: int | None = None,
) -> tuple[dict[str, Any] | None, dict[str, Any]]:
    """Evaluate the PDP. Returns (masked_record | None, masking_decision).

    masked_record is None when the verdict denies access.
    """
    audience = audience or {}
    profiles = profiles or {}
    policy = policy or {}
    ts = now_micros if now_micros is not None else exodus_seal.now_micros()

    # active identity topics = record's prime topics + the realm-implied topic
    active = set(record.get("primes") or record.get("prime_topics") or [])
    rt = _realm_topic(requesting_realm)
    if rt:
        active.add(rt)

    reason_codes: list[str] = []
    forbidden = _forbidden_hit(active, policy)
    verdict = "allow"
    masked: dict[str, Any] | None = dict(record)
    applied: list[dict[str, Any]] = []
    reident: dict[str, Any] | None = None

    if forbidden:
        verdict, masked = "deny", None
        reason_codes = ["FORBIDDEN_IDENTITY_MIXTURE"]
    elif requested_op == "re_identify":
        authorized = "reidentif" in str(audience.get("openid_profile_attr", "")).lower() or \
            audience.get("can_reidentify") is True
        if not (authorized and reason_for_action):
            verdict, masked = "review_required", None
            reason_codes = ["REIDENTIFY_NOT_AUTHORIZED"] if not authorized else ["REASON_FOR_ACTION_REQUIRED"]
        else:
            verdict = "allow"
            reason_codes = ["PROFILE_ATTR_AUTHORIZED", "REASON_RECORDED"]
            reident = {
                "permitted": True,
                "reason_for_action": reason_for_action,
                "authorized_by": audience.get("authorized_by"),
                "separation_of_duty": bool(audience.get("separation_of_duty", False)),
                "release_pack_ref": None,
            }
    else:
        # apply field transforms
        for field_path, profile in profiles.items():
            if field_path not in record or record[field_path] is None:
                continue
            res = exodus_tokenize.apply_profile(str(record[field_path]), profile, master_key)
            masked[field_path] = res["output"]
            applied.append({
                "field_path": field_path,
                "profile_ref": profile.get("profile_id"),
                "scheme": res["scheme"],
                "reversibility": "reversible" if res["reversibility"] == "reversible" else ("one_way" if res["reversibility"] == "one_way" else "reversible"),
                "key_epoch": res.get("epoch"),
                "target_domain": None,
            })
        verdict = "allow_masked" if applied else "allow"
        reason_codes = ["NO_FORBIDDEN_MIXTURE"]

    decision: dict[str, Any] = {
        "schema_version": "identity-prime.masking-decision.v1",
        "decision_id": "md_" + uuid.uuid4().hex[:16],
        "subject_ref": subject_ref,
        "requesting_realm": requesting_realm,
        "audience": {"role": audience.get("role"), "openid_profile_attr": audience.get("openid_profile_attr")},
        "requested_op": requested_op,
        "verdict": verdict,
        "reason_codes": reason_codes,
        "forbidden_mixture": forbidden,
        "applied_transforms": applied,
        "re_identification": reident,
        "side_channel_mitigations": policy.get("side_channel_mitigations", ["policy", "unlinkable_identifiers", "monitoring"]),
        "policy_version": policy.get("policy_version", "regis.identity.polytope.core@0.1.0"),
        "scheme_version": "identity-prime.tokenization-profile.v1",
        "decided_by": "masking-pdp-agent",
        "created_at": _iso(ts),
    }

    # Seal the decision: real BEACON_COMMIT receipt if a key is supplied, else a content frame hash.
    core = {k: decision[k] for k in ("decision_id", "subject_ref", "requesting_realm", "requested_op", "verdict", "forbidden_mixture", "applied_transforms")}
    if signing_key_hex:
        receipt = exodus_seal.seal(core, private_key_hex=signing_key_hex, key_id="pdp-key", signer_id="masking-pdp", sealed_at_micros=ts)
        decision["receipt"] = {
            "policy_decision_ref": "pd_" + decision["decision_id"][3:],
            "beacon_commit_receipt": json.dumps(receipt, sort_keys=True),
            "certificate_hash": f"{receipt.get('frame_hash_algo')}:{receipt.get('frame_hash')}",
        }
    else:
        algo, fh = exodus_seal.content_frame_hash(core)
        decision["receipt"] = {
            "policy_decision_ref": "pd_" + decision["decision_id"][3:],
            "beacon_commit_receipt": None,
            "certificate_hash": f"{algo}:{fh}",
        }
    return masked, decision


def _iso(micros: int) -> str:
    import datetime as dt
    return dt.datetime.fromtimestamp(micros / 1_000_000, dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Evaluate the masking PDP for a record.")
    p.add_argument("--record", required=True)
    p.add_argument("--policy", required=True)
    p.add_argument("--profiles", help="JSON object field_path -> tokenization-profile.")
    p.add_argument("--realm", required=True)
    p.add_argument("--subject-ref", default="subject:unknown")
    p.add_argument("--op", default="read")
    args = p.parse_args(argv)
    record = json.loads(Path(args.record).read_text())
    policy = json.loads(Path(args.policy).read_text())
    profiles = json.loads(Path(args.profiles).read_text()) if args.profiles else {}
    masked, decision = evaluate_masking(record, subject_ref=args.subject_ref, requesting_realm=args.realm,
                                        profiles=profiles, policy=policy, requested_op=args.op)
    print(json.dumps({"verdict": decision["verdict"], "decision": decision, "masked_record": masked}, indent=2))
    return 0 if decision["verdict"] in ("allow", "allow_masked", "review_required") else 2


if __name__ == "__main__":
    sys.exit(main())
