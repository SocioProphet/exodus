#!/usr/bin/env python3
"""Exodus zone-gate engine — executable enforcement of the WNZL Dirt-to-Diamond
promotion gates (Metadata Standards v0.1 Section 7).

The policy-gate schema describes CHK-01..CHK-10; this module *runs* them and
returns a fail-closed promotion decision plus the CustodyEvent that must be
written (ZonePromotion when admitted, PolicyException when blocked, and a
custody_status of IntegrityViolation when the acquisition hash no longer
verifies). Dependency-free so it runs in CI without extra packages.

Doctrine encoded here (the adversarial-evidence rule): an artifact cannot reach
an analysis-bearing zone without counter-explanations and, at E3+, a declared
null hypothesis. Observation is preserved separately from interpretation.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

ZERO_HASH_64 = "0" * 64
_UNSET_ENUMS = {None, "", "Unknown"}
_GRADE_RANK = {"E1": 1, "E2": 2, "E3": 3, "E4": 4, "E5": 5}


def now_micros() -> int:
    return int(dt.datetime.now(dt.timezone.utc).timestamp() * 1_000_000)


@dataclass
class GateContext:
    """Out-of-band facts the checks need (kept explicit + injectable for replay)."""
    recomputed_blake3: str | None = None          # CHK-01: hash recomputed from bytes now
    other_exhibit_ids: set[str] = field(default_factory=set)   # CHK-03: exhibit_ids already in corpus
    hash_to_exhibit: dict[str, str] = field(default_factory=dict)  # CHK-08: hash -> exhibit_id (other artifacts)
    registered_accounts: set[str] = field(default_factory=set)  # CHK-09
    now_micros: int | None = None


@dataclass
class CheckResult:
    check_id: str
    name: str
    passed: bool
    blocking: bool
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return {"check_id": self.check_id, "name": self.name, "passed": self.passed, "blocking": self.blocking, "reason": self.reason}


@dataclass
class GateDecision:
    checks_passed: bool          # all blocking checks + required fields satisfied
    auto_promote: bool           # checks_passed AND no human/legal review outstanding
    requires_human_review: bool
    requires_legal_review: bool
    custody_event_type: str      # ZonePromotion | PolicyException
    custody_status: str          # Intact | IntegrityViolation | PendingVerification
    results: list[CheckResult]
    reasons: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "checks_passed": self.checks_passed,
            "auto_promote": self.auto_promote,
            "requires_human_review": self.requires_human_review,
            "requires_legal_review": self.requires_legal_review,
            "custody_event_type": self.custody_event_type,
            "custody_status": self.custody_status,
            "results": [r.to_dict() for r in self.results],
            "reasons": self.reasons,
        }


# ── Individual checks (artifact, ctx) -> (passed, reason) ─────────────────────
def _grade_rank(artifact: dict[str, Any]) -> int:
    return _GRADE_RANK.get(str(artifact.get("evidence_grade", "")), 0)


def _chk01(a, ctx):  # IntegrityVerification
    if ctx.recomputed_blake3 is None:
        return False, "cannot verify: artifact bytes not recomputed (fail-closed)"
    if str(ctx.recomputed_blake3).lower() != str(a.get("hash_blake3", "")).lower():
        return False, "recomputed BLAKE3 does not match stored hash"
    return True, "hash verified"


def _chk02(a, ctx):  # TemporalConsistency
    vf, vt = a.get("valid_from_micros"), a.get("valid_to_micros")
    if vf is not None and vt is not None and vf > vt:
        return False, f"valid_from ({vf}) > valid_to ({vt})"
    now = ctx.now_micros if ctx.now_micros is not None else now_micros()
    obs = a.get("observed_at_micros")
    if obs is not None and obs > now:
        return False, "observed_at_micros is in the future"
    return True, "temporal ordering consistent"


def _chk03(a, ctx):  # ExhibitIdUniqueness
    if a.get("exhibit_id") in ctx.other_exhibit_ids:
        return False, f"exhibit_id {a.get('exhibit_id')} already used in corpus"
    return True, "exhibit_id unique"


def _chk04(a, ctx):  # CounterExplanationPresent
    ce = a.get("counter_explanations")
    if not isinstance(ce, list) or not ce:
        return False, "counter_explanations empty — adversarial review required before analysis"
    return True, f"{len(ce)} counter-explanation(s) present"


def _chk05(a, ctx):  # NullHypothesisDefined (only E3+)
    if _grade_rank(a) >= 3:
        nh = a.get("null_hypothesis_ids")
        if not isinstance(nh, list) or not nh:
            return False, "evidence_grade >= E3 requires a declared null hypothesis"
    return True, "null hypothesis present or not yet required"


def _chk06(a, ctx):  # SecurityLabelSet
    if a.get("security_label") in _UNSET_ENUMS:
        return False, "security_label unset"
    return True, "security_label set"


def _chk07(a, ctx):  # WitnessRetentionSet
    if a.get("witness_retention") in _UNSET_ENUMS:
        return False, "witness_retention unset"
    return True, "witness_retention set"


def _chk08(a, ctx):  # DuplicateDetection (non-blocking flag by default)
    h = str(a.get("hash_blake3", "")).lower()
    other = ctx.hash_to_exhibit.get(h)
    if other and other != a.get("exhibit_id"):
        return False, f"byte-identical to exhibit {other} — classify as Duplicate; analyst ack required"
    return True, "no duplicate detected"


def _chk09(a, ctx):  # SourceAccountRegistered
    if a.get("source_account") not in ctx.registered_accounts:
        return False, f"source_account {a.get('source_account')!r} not in account registry"
    return True, "source account registered"


def _chk10(a, ctx):  # HashAlgorithmCompliance
    for fld in ("hash_blake3", "hash_sha256"):
        v = str(a.get(fld, ""))
        if len(v) != 64 or v == ZERO_HASH_64:
            return False, f"{fld} missing/zero/wrong-length"
    return True, "blake3 + sha256 present and non-zero"


_CHECKS: dict[str, tuple[str, Callable[[dict, GateContext], tuple[bool, str]]]] = {
    "CHK-01": ("IntegrityVerification", _chk01),
    "CHK-02": ("TemporalConsistency", _chk02),
    "CHK-03": ("ExhibitIdUniqueness", _chk03),
    "CHK-04": ("CounterExplanationPresent", _chk04),
    "CHK-05": ("NullHypothesisDefined", _chk05),
    "CHK-06": ("SecurityLabelSet", _chk06),
    "CHK-07": ("WitnessRetentionSet", _chk07),
    "CHK-08": ("DuplicateDetection", _chk08),
    "CHK-09": ("SourceAccountRegistered", _chk09),
    "CHK-10": ("HashAlgorithmCompliance", _chk10),
}
# CHK-08 is a flag, not a hard block, per the spec (failure_action = "flag").
_DEFAULT_NONBLOCKING = {"CHK-08"}


def _missing_required_fields(artifact: dict[str, Any], required: list[str]) -> list[str]:
    return [f for f in required if artifact.get(f) in (None, "")]


def evaluate_gate(artifact: dict[str, Any], policy: dict[str, Any], ctx: GateContext) -> GateDecision:
    """Run a zone-gate policy against an artifact. Fail-closed: any blocking check
    failure or missing required field denies promotion."""
    reasons: list[str] = []
    results: list[CheckResult] = []

    # Class scoping: a policy with applies_to_classes not matching this artifact is a no-op pass-through.
    classes = policy.get("applies_to_classes") or []
    if "*" not in classes and artifact.get("artifact_class") not in classes:
        reasons.append(f"policy does not apply to class {artifact.get('artifact_class')}")
        return GateDecision(False, False, bool(policy.get("human_review_required")),
                            bool(policy.get("legal_review_required")), "PolicyException",
                            "PendingVerification", results, reasons)

    missing = _missing_required_fields(artifact, policy.get("required_fields") or [])
    if missing:
        reasons.append("missing required fields: " + ", ".join(missing))

    integrity_violation = False
    for spec in policy.get("required_checks") or []:
        cid = spec.get("check_id")
        name, fn = _CHECKS.get(cid, (spec.get("name", cid), None))
        blocking = spec.get("blocking", cid not in _DEFAULT_NONBLOCKING)
        if fn is None:
            results.append(CheckResult(cid, name, False, blocking, "unknown check id"))
            reasons.append(f"{cid}: unknown check id")
            continue
        passed, why = fn(artifact, ctx)
        results.append(CheckResult(cid, name, passed, blocking, why))
        if not passed:
            if cid == "CHK-01":
                integrity_violation = True
            if blocking:
                reasons.append(f"{cid} {name}: {why}")

    blocking_failures = [r for r in results if not r.passed and r.blocking]
    checks_passed = not missing and not blocking_failures

    requires_human = bool(policy.get("human_review_required"))
    requires_legal = bool(policy.get("legal_review_required"))
    auto_promote = checks_passed and not requires_human and not requires_legal
    if checks_passed and (requires_human or requires_legal):
        reasons.append("checks passed; awaiting human/legal review before promotion")

    custody_status = "IntegrityViolation" if integrity_violation else ("Intact" if checks_passed else "PendingVerification")
    custody_event_type = "ZonePromotion" if checks_passed else "PolicyException"

    return GateDecision(checks_passed, auto_promote, requires_human, requires_legal,
                        custody_event_type, custody_status, results, reasons)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Evaluate an Exodus zone-gate policy against an artifact.")
    p.add_argument("--artifact", required=True)
    p.add_argument("--policy", required=True)
    p.add_argument("--recomputed-blake3", default=None, help="BLAKE3 recomputed from bytes now (for CHK-01)")
    p.add_argument("--registered-account", action="append", default=[], help="repeatable; accounts in the registry")
    args = p.parse_args(argv if argv is not None else sys.argv[1:])

    artifact = json.loads(Path(args.artifact).read_text(encoding="utf-8"))
    policy = json.loads(Path(args.policy).read_text(encoding="utf-8"))
    ctx = GateContext(
        recomputed_blake3=args.recomputed_blake3,
        registered_accounts=set(args.registered_account) or {artifact.get("source_account")},
    )
    decision = evaluate_gate(artifact, policy, ctx)
    print(json.dumps(decision.to_dict(), indent=2, sort_keys=True))
    return 0 if decision.checks_passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
