#!/usr/bin/env python3
"""Dependency-free tests for the Exodus tokenization engine.

Run: python3 scripts/test_exodus_tokenize.py
Matches the repo's test_*.py idiom — plain asserts, exits non-zero on failure.
Proves the homomorphic re-keying identity, cross-domain unlinkability, key-rotation
consistency, FPE round-trip + format preservation, and re-identification lookup.
"""
from __future__ import annotations

import sys

from exodus_tokenize import (
    P, Q, apply_profile, build_reid_lookup, chameleon_token, domain_tweak,
    fpe_decrypt, fpe_encrypt, hmac_pseudonym, retokenize,
)

MK = b"unit-test-master-key"


def _is_prime(n: int, rounds: int = 24) -> bool:
    import random
    if n < 2:
        return False
    for p in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        if n % p == 0:
            return n == p
    d, s = n - 1, 0
    while d % 2 == 0:
        d //= 2
        s += 1
    rng = random.Random(1)
    for _ in range(rounds):
        a = rng.randrange(2, n - 1)
        x = pow(a, d, n)
        if x in (1, n - 1):
            continue
        for _ in range(s - 1):
            x = x * x % n
            if x == n - 1:
                break
        else:
            return False
    return True


def test_group_is_safe_prime():
    assert _is_prime(P), "P must be prime"
    assert _is_prime(Q), "Q=(P-1)/2 must be prime (safe prime)"
    assert P == 2 * Q + 1


def test_determinism():
    a = chameleon_token("MRN-12345", "CITIZEN_CLOUD", 0, MK)
    b = chameleon_token("MRN-12345", "CITIZEN_CLOUD", 0, MK)
    assert a == b


def test_cross_domain_unlinkable():
    a = chameleon_token("MRN-12345", "CITIZEN_CLOUD", 0, MK)
    b = chameleon_token("MRN-12345", "INSTITUTION", 0, MK)
    assert a != b, "same value in different domains must not be linkable by equality"


def test_homomorphic_retokenization():
    # token in domain1, re-keyed with a tweak, equals a native token in domain2 — no cleartext.
    v = "MRN-12345"
    t1 = chameleon_token(v, "CITIZEN_CLOUD", 0, MK)
    tweak = domain_tweak(MK, "CITIZEN_CLOUD", 0, "INSTITUTION", 0)
    t2_via_tweak = retokenize(t1, tweak)
    t2_native = chameleon_token(v, "INSTITUTION", 0, MK)
    assert t2_via_tweak == t2_native, "homomorphic re-tokenisation must match native token"


def test_key_rotation_consistency():
    v = "MRN-12345"
    t_e0 = chameleon_token(v, "INSTITUTION", 0, MK)
    tweak = domain_tweak(MK, "INSTITUTION", 0, "INSTITUTION", 1)
    t_e1_via = retokenize(t_e0, tweak)
    t_e1_native = chameleon_token(v, "INSTITUTION", 1, MK)
    assert t_e1_via == t_e1_native, "epoch rotation must migrate tokens consistency-preservingly"


def test_fpe_roundtrip_and_format():
    pt = "4485360000000005"  # 16 digits (even)
    ct = fpe_encrypt(pt, MK)
    assert ct.isdigit() and len(ct) == len(pt), "FPE must preserve digit format and length"
    assert ct != pt
    assert fpe_decrypt(ct, MK) == pt, "FPE must round-trip"


def test_reidentification_lookup():
    vals = ["alice@example.org", "bob@example.org"]
    lut = build_reid_lookup(vals, "INSTITUTION", 0, MK)
    tok = hmac_pseudonym("alice@example.org", "INSTITUTION", 0, MK)
    assert lut[tok] == "alice@example.org", "governed re-id lookup must recover the original"


def test_apply_profile_dispatch():
    r = apply_profile("MRN-12345", {"scheme": "chameleon_token", "domain_scope": "HSM", "key": {"key_epoch": 2}}, MK)
    assert r["scheme"] == "chameleon_token" and r["reversibility"] == "lookup" and r["output"]
    r = apply_profile("secret", {"scheme": "redact"}, MK)
    assert r["output"] == "[REDACTED]" and r["reversibility"] == "one_way"
    r = apply_profile("secret", {"scheme": "suppress"}, MK)
    assert r["output"] is None


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
        print(f"tokenization: FAIL ({failed}/{len(tests)})")
        return 1
    print(f"tokenization: PASS ({len(tests)} tests)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
