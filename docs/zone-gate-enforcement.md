# Zone-gate enforcement (CHK-01..CHK-10)

Metadata Standards v0.1 §7 defines the WNZL Dirt-to-Diamond promotion gates as a
schema (`schemas/policy-gate.json`). This slice makes them **executable**: the
gates are now run and enforced, not merely described.

## What this adds

- `scripts/exodus_gate.py` — the gate engine. `evaluate_gate(artifact, policy, ctx)`
  runs the policy's required fields + checks and returns a **fail-closed**
  `GateDecision` plus the CustodyEvent that must be written:
  - `ZonePromotion` when admitted, `PolicyException` when blocked;
  - `custody_status = IntegrityViolation` whenever CHK-01 fails (recomputed
    BLAKE3 ≠ stored hash);
  - `auto_promote` is only true when checks pass **and** no human/legal review is
    outstanding (promotions to Governed/Diamond never auto-promote).
- `examples/gate-policies/` — the first concrete gate policies (previously the
  schema had zero instances):
  - `GATE-Landing-Examination-v1` — CHK-01/03/09/10 + CHK-08 (non-blocking flag).
  - `GATE-Examination-Integration-v1` — CHK-01/02 + the adversarial-evidence
    gate: CHK-04 (counter-explanations) and CHK-05 (null hypothesis at E3+).
  - `GATE-Integration-Governed-v1` — CHK-01/06/07 + human + legal review.
- `scripts/test_exodus_gate.py` — dependency-free CHK matrix (pass/fail for each
  check, integrity-violation custody status, non-blocking duplicate flag, and the
  review-gated Governed promotion). Wired into CI.

## Check semantics

| Check | Enforces | Blocking |
|---|---|---|
| CHK-01 IntegrityVerification | recomputed BLAKE3 == stored; fail-closed if bytes not recomputed | yes (→ IntegrityViolation) |
| CHK-02 TemporalConsistency | valid_from ≤ valid_to; observed_at not in the future | yes |
| CHK-03 ExhibitIdUniqueness | exhibit_id unused in corpus | yes |
| CHK-04 CounterExplanationPresent | ≥1 benign alternative before analysis | yes |
| CHK-05 NullHypothesisDefined | null hypothesis declared at evidence_grade ≥ E3 | yes |
| CHK-06 SecurityLabelSet / CHK-07 WitnessRetentionSet | disclosure controls set before Governed | yes |
| CHK-08 DuplicateDetection | byte-identical to another exhibit | no (flag + analyst ack) |
| CHK-09 SourceAccountRegistered | source_account in the registry | yes |
| CHK-10 HashAlgorithmCompliance | blake3 + sha256 present, non-zero, 64 hex | yes |

## Still open (unchanged by this slice)

TriTRPC `BEACON_COMMIT` sealing of CustodyEvents, HellGraph atom signing, the
working ForensicBundle export command, account-registry population, and BSM
ingest. The engine emits the CustodyEvent *shape*; cryptographic sealing is the
next dependency.
