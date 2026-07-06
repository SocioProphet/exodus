#!/usr/bin/env python3
"""Exodus tokenization engine — Chameleon pseudonyms + key-evolving + FPE (reference impl).

Reference (stdlib-only) implementation of the desensitisation primitives for the masking
layer. The algebraic pseudonym is genuinely homomorphic under re-keying, which is what
lets domain re-tokenisation and key rotation happen without ever touching cleartext:

    token(value, domain, epoch) = H(value)^2 ^ k(domain, epoch)  (mod P)
    re-tokenise (d1,e1)->(d2,e2): tweak = k2 * k1^-1 (mod Q);  token2 = token1^tweak (mod P)

  * domain-scoped & deterministic: same (value,domain,epoch) -> same token.
  * cross-domain UNLINKABLE: token^kA and token^kB are unrelated without a tweak (DDH).
  * key-evolving: epoch rotation is an intra-domain tweak; stored tokens migrate
    consistency-preservingly (no re-tokenise from cleartext).

NOT production crypto: the group is a 256-bit reference safe prime (verified in
test_exodus_tokenize.py). Production must use a >=2048-bit MODP/EC group, constant-time
bigint, HSM-held scalars (KMIP/PKCS#11), and a vetted FPE (NIST FF1). The FPE below is a
reference balanced Feistel for even-length digit strings, not FF1-certified. BLAKE3 is
used opportunistically to match exodus_seal.py; the primitives here use HMAC-SHA256.
"""
from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import sys
from pathlib import Path
from typing import Any

# Reference group: 256-bit safe prime P = 2Q+1 (both verified prime in the test).
P = 73396095300908649847098500061455176300324139511807388997097590509833131762639
Q = (P - 1) // 2


def _h(*parts: bytes) -> bytes:
    m = hashlib.sha256()
    for p in parts:
        m.update(len(p).to_bytes(4, "big"))
        m.update(p)
    return m.digest()


def derive_scalar(master_key: bytes, domain: str, epoch: int) -> int:
    """Per-(domain,epoch) secret scalar k in [1, Q-1], derived from the master key."""
    tag = hmac.new(master_key, f"chameleon|{domain}|{epoch}".encode("utf-8"), hashlib.sha256).digest()
    return int.from_bytes(tag + _h(tag), "big") % (Q - 1) + 1


def _hash_to_group(value: str) -> int:
    """Map a value to a quadratic-residue element of the order-Q subgroup."""
    h = int.from_bytes(_h(b"htg", value.encode("utf-8")), "big") % P
    base = pow(h or 2, 2, P)
    return base if base not in (0, 1) else 4


def chameleon_token(value: str, domain: str, epoch: int, master_key: bytes) -> str:
    k = derive_scalar(master_key, domain, epoch)
    return format(pow(_hash_to_group(value), k, P), "x")


def domain_tweak(master_key: bytes, d_from: str, e_from: int, d_to: str, e_to: int) -> int:
    """Re-key tweak mapping tokens from (d_from,e_from) to (d_to,e_to); no cleartext needed."""
    k1 = derive_scalar(master_key, d_from, e_from)
    k2 = derive_scalar(master_key, d_to, e_to)
    return (k2 * pow(k1, -1, Q)) % Q


def retokenize(token_hex: str, tweak: int) -> str:
    return format(pow(int(token_hex, 16), tweak, P), "x")


# ── HMAC pseudonym + governed re-identification lookup (the deck's HMAC-lookup) ──
_B32 = "0123456789ABCDEFGHIJKLMNOPQRSTUV"


def hmac_pseudonym(value: str, domain: str, epoch: int, master_key: bytes, length: int = 16) -> str:
    raw = hmac.new(master_key, f"hmac|{domain}|{epoch}|{value}".encode("utf-8"), hashlib.sha256).digest()
    n = int.from_bytes(raw, "big")
    out = []
    for _ in range(length):
        out.append(_B32[n & 31])
        n >>= 5
    return "".join(out)


def build_reid_lookup(values: list[str], domain: str, epoch: int, master_key: bytes) -> dict[str, str]:
    """Secure keyed reverse dictionary pseudonym->value for governed re-identification."""
    return {hmac_pseudonym(v, domain, epoch, master_key): v for v in values}


# ── Format-preserving encryption (reference balanced Feistel, even-length digits) ─
def _prf(master_key: bytes, rnd: int, x: int, modulus: int) -> int:
    raw = hmac.new(master_key, f"fpe|{rnd}|{x}".encode("utf-8"), hashlib.sha256).digest()
    return int.from_bytes(raw, "big") % modulus


def fpe_encrypt(digits: str, master_key: bytes, rounds: int = 8) -> str:
    if not digits.isdigit() or len(digits) % 2 != 0:
        raise ValueError("reference FPE requires an even-length digit string")
    h = len(digits) // 2
    mod = 10 ** h
    L, R = int(digits[:h]), int(digits[h:])
    for i in range(rounds):
        L, R = R, (L + _prf(master_key, i, R, mod)) % mod
    return str(L).zfill(h) + str(R).zfill(h)


def fpe_decrypt(digits: str, master_key: bytes, rounds: int = 8) -> str:
    h = len(digits) // 2
    mod = 10 ** h
    L, R = int(digits[:h]), int(digits[h:])
    for i in reversed(range(rounds)):
        R, L = L, (R - _prf(master_key, i, L, mod)) % mod
    return str(L).zfill(h) + str(R).zfill(h)


# ── Irreversible schemes ─────────────────────────────────────────────────────────
def one_way_hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def redact(_value: str) -> str:
    return "[REDACTED]"


def generalize(value: str, keep_prefix: int = 1) -> str:
    return value[:keep_prefix] + "*" * max(0, len(value) - keep_prefix)


# ── Dispatch by tokenization-profile.v1 scheme ────────────────────────────────────
def apply_profile(value: str, profile: dict[str, Any], master_key: bytes) -> dict[str, Any]:
    """Apply a tokenization-profile.v1 to a value. Returns {scheme, reversibility, output}."""
    scheme = profile.get("scheme")
    domain = profile.get("domain_scope", "CITIZEN_CLOUD")
    epoch = int((profile.get("key") or {}).get("key_epoch", 0))
    if scheme == "chameleon_token":
        out, rev = chameleon_token(value, domain, epoch, master_key), "lookup"
    elif scheme in ("hmac_pseudonym", "legacy_token_an10"):
        out = hmac_pseudonym(value, domain, epoch, master_key, 10 if scheme == "legacy_token_an10" else 16)
        rev = "lookup"
    elif scheme in ("format_preserving_encryption", "length_preserving_encryption"):
        out, rev = fpe_encrypt(value, master_key), "reversible"
    elif scheme == "one_way_hash":
        out, rev = one_way_hash(value), "one_way"
    elif scheme == "redact":
        out, rev = redact(value), "one_way"
    elif scheme == "suppress":
        out, rev = None, "one_way"
    elif scheme == "generalize":
        out, rev = generalize(value), "one_way"
    else:
        raise ValueError(f"unsupported scheme: {scheme!r}")
    return {"scheme": scheme, "reversibility": rev, "output": out, "domain": domain, "epoch": epoch}


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Apply a tokenization profile to a value.")
    p.add_argument("--value", required=True)
    p.add_argument("--profile", required=True, help="Path to a tokenization-profile.v1 JSON file.")
    p.add_argument("--master-key", default="reference-master-key", help="Demo only; production uses an HSM.")
    args = p.parse_args(argv)
    profile = json.loads(Path(args.profile).read_text(encoding="utf-8"))
    print(json.dumps(apply_profile(args.value, profile, args.master_key.encode("utf-8")), indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
