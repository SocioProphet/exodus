#!/usr/bin/env python3
"""Dependency-free tests for the Exodus zone-gate engine (CHK-01..CHK-10).

Run: python3 scripts/test_exodus_gate.py
Matches the repo's validate_*.py idiom — plain asserts, exits non-zero on failure.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path

from exodus_gate import GateContext, evaluate_gate, now_micros

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = json.loads((ROOT / "examples/valid-evidence-artifact.json").read_text())
GP = ROOT / "examples/gate-policies"
LANDING = json.loads((GP / "GATE-Landing-Examination-v1.json").read_text())
EXAM = json.loads((GP / "GATE-Examination-Integration-v1.json").read_text())
GOVERNED = json.loads((GP / "GATE-Integration-Governed-v1.json").read_text())

ACCT = ARTIFACT["source_account"]
GOODHASH = ARTIFACT["hash_blake3"]


def ctx(**kw) -> GateContext:
    base = dict(recomputed_blake3=GOODHASH, registered_accounts={ACCT}, now_micros=now_micros())
    base.update(kw)
    return GateContext(**base)


def run() -> None:
    # Landing -> Examination on a clean artifact: passes + auto-promotes.
    d = evaluate_gate(ARTIFACT, LANDING, ctx())
    assert d.checks_passed and d.auto_promote, d.reasons
    assert d.custody_event_type == "ZonePromotion" and d.custody_status == "Intact"

    # CHK-01 integrity failure -> blocked + IntegrityViolation custody status.
    d = evaluate_gate(ARTIFACT, LANDING, ctx(recomputed_blake3="f" * 64))
    assert not d.checks_passed and d.custody_status == "IntegrityViolation"
    assert d.custody_event_type == "PolicyException"

    # CHK-01 cannot verify when bytes not recomputed -> fail-closed.
    d = evaluate_gate(ARTIFACT, LANDING, ctx(recomputed_blake3=None))
    assert not d.checks_passed

    # CHK-09 unregistered account -> blocked.
    d = evaluate_gate(ARTIFACT, LANDING, ctx(registered_accounts=set()))
    assert not d.checks_passed and any("CHK-09" in r for r in d.reasons)

    # CHK-10 zero/short hash -> blocked.
    bad = copy.deepcopy(ARTIFACT); bad["hash_sha256"] = "0" * 64
    d = evaluate_gate(bad, LANDING, ctx(recomputed_blake3=bad["hash_blake3"]))
    assert not d.checks_passed and any("CHK-10" in r for r in d.reasons)

    # CHK-03 exhibit collision -> blocked.
    d = evaluate_gate(ARTIFACT, LANDING, ctx(other_exhibit_ids={ARTIFACT["exhibit_id"]}))
    assert not d.checks_passed and any("CHK-03" in r for r in d.reasons)

    # CHK-08 duplicate is a non-blocking FLAG: failed check present, but still passes.
    d = evaluate_gate(ARTIFACT, LANDING, ctx(hash_to_exhibit={GOODHASH: "AF-9999"}))
    assert d.checks_passed, d.reasons
    chk08 = next(r for r in d.results if r.check_id == "CHK-08")
    assert not chk08.passed and not chk08.blocking

    # Examination -> Integration: missing counter_explanations -> CHK-04 blocks.
    no_ce = copy.deepcopy(ARTIFACT); no_ce["counter_explanations"] = []
    d = evaluate_gate(no_ce, EXAM, ctx())
    assert not d.checks_passed and any("CHK-04" in r for r in d.reasons)

    # Examination -> Integration: E3 without null hypothesis -> CHK-05 blocks.
    no_null = copy.deepcopy(ARTIFACT); no_null["null_hypothesis_ids"] = []
    d = evaluate_gate(no_null, EXAM, ctx())
    assert not d.checks_passed and any("CHK-05" in r for r in d.reasons)

    # Examination -> Integration clean -> passes.
    d = evaluate_gate(ARTIFACT, EXAM, ctx())
    assert d.checks_passed and d.auto_promote, d.reasons

    # CHK-02 temporal inversion -> blocked.
    inv = copy.deepcopy(ARTIFACT); inv["valid_from_micros"] = 200; inv["valid_to_micros"] = 100
    d = evaluate_gate(inv, EXAM, ctx())
    assert not d.checks_passed and any("CHK-02" in r for r in d.reasons)

    # Integration -> Governed: checks pass but human+legal review gate auto-promotion.
    d = evaluate_gate(ARTIFACT, GOVERNED, ctx())
    assert d.checks_passed and not d.auto_promote
    assert d.requires_human_review and d.requires_legal_review

    # Integration -> Governed: missing security_label -> blocked (CHK-06 + required field).
    no_label = copy.deepcopy(ARTIFACT); no_label["security_label"] = "Unknown"
    d = evaluate_gate(no_label, GOVERNED, ctx())
    assert not d.checks_passed and any("CHK-06" in r for r in d.reasons)

    print("OK: exodus_gate CHK-01..CHK-10 + policy enforcement — all assertions passed")


def validate_policy_shapes() -> None:
    required_top = {"policy_id", "from_zone", "to_zone", "applies_to_classes", "required_fields",
                    "required_checks", "human_review_required", "legal_review_required",
                    "policy_version", "effective_from_txn"}
    for pol in (LANDING, EXAM, GOVERNED):
        missing = required_top - set(pol)
        assert not missing, f"{pol.get('policy_id')} missing {missing}"
        for c in pol["required_checks"]:
            assert {"check_id", "name", "failure_action"} <= set(c), f"bad check_spec in {pol['policy_id']}"
    print("OK: 3 gate policies are schema-shaped")


if __name__ == "__main__":
    validate_policy_shapes()
    run()
