# Forensic sealing, ForensicBundle export, and intake adapters

This slice closes the cryptographic and operational gaps that stood between the
Phase-0 metadata schema pack and a court-presentable evidence corpus
(Metadata Standards §6, §8, §10; GAP-06/07/08/09/10).

## 1. Cryptographic custody sealing — `scripts/exodus_seal.py`

Seals a CustodyEvent (or any record) with a content frame-hash + a detached
**Ed25519** signature, producing a TriTRPC-shaped `BEACON_COMMIT` receipt.

- **Independently verifiable (FRE 902(14)).** `verify_receipt(payload, receipt)`
  needs only the receipt JSON — the public key is embedded. An opposing expert
  can confirm integrity without the platform.
- **Deterministic replay harness.** Ed25519 is deterministic (RFC 8032) and
  CANON-v0.1 serialization is byte-stable, so a committed receipt re-seals
  bit-for-bit. `scripts/test_exodus_seal.py` asserts byte-exact replay — this is
  the legal replay harness, not a test convenience.
- **Frame hash:** BLAKE3-256 when `blake3` is installed, else SHA-256, always
  labeled in `frame_hash_algo`. The signature binds content-hash ↔ signer ↔
  sealing-time, so receipt metadata cannot be re-bound to a different signer.
- **Canonicalization:** CANON-v0.1 = sorted-key, whitespace-free, UTF-8 JSON,
  pinned in `examples/serializer-spec.canon-v0_1.json` (the serializer-spec is
  versioned so the encoding can later move to deterministic CBOR without
  breaking older receipts).

## 2. ForensicBundle export — `scripts/exodus_bundle.py`

`build_bundle(...)` assembles a §10 ForensicBundle: a manifest of artifacts with
their hashes, a compact custody-chain snapshot, a replay manifest, BLAKE3-256 +
SHA-256 master hashes over the canonical bundle core, and an Ed25519
`BEACON_COMMIT` seal. `verify_bundle(bundle)` re-derives every hash and verifies
the signature **from the JSON alone** — the independent-verification path an
opposing party runs. Conforms to `schemas/forensic-bundle.json`.

## 3. Account registry — `scripts/account_registry.py` (GAP-08)

Backs **CHK-09 (SourceAccountRegistered)**: only accounts present and `active` in
`examples/account-registry.json` may enter intake.

## 4. BSM audit adapter — `scripts/bsm_intake.py` (AC-09, GAP-10)

Parses `praudit -xn` XML into Examination-zone enrichments: syscall sequence,
uid/pid map, file-access timeline, and a privilege-escalation flag list
(identity-changing syscalls + effective-root-with-non-root-ruid). `ingest_bsm_file`
shells to `praudit` for real `/var/audit` files; the parser is tested against a
synthetic fixture so no real audit data is required. The remaining work is
**operational** — running it against the target Mac — not implementation.

## Dependencies

Sealing/bundle require `cryptography` (Ed25519) and `blake3`; CI installs both.
The registry, BSM adapter, schema validators, and gate engine remain stdlib-only.

## What still requires the physical machine / external authority

- Running `praudit` against the live `/var/audit` (operational ingest).
- Binding a **production** signing key (the committed key is a synthetic test
  key) and its chain-of-trust / HSM custody.
- HellGraph atom persistence/signing for atoms beyond the receipt layer.
