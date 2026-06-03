# Phase 1 Exodus Intake Acquisition Path

Status: initial synthetic-safe implementation
Issue: #16

This document records the first operational intake path for Exodus metadata standards.

## What exists

`scripts/exodus_intake.py` accepts a local artifact path and explicit source metadata, then writes:

- an EvidenceArtifact-compatible JSON record;
- an initial CustodyEvent-compatible JSON record with `event_type=Intake`.

The command computes SHA-256 over raw file bytes using the Python standard library. BLAKE3 is computed only when the optional `blake3` Python package is available. If BLAKE3 is unavailable, callers must explicitly pass `--allow-pending-blake3`; the command writes a zero-hash sentinel, marks the record `PendingVerification`, and records that BLAKE3 is unavailable in `hash_computed_by`.

## Discipline boundary

A `PendingVerification` record is not an authenticated legal-custody artifact. It is an intake metadata draft preserving raw-byte SHA-256 and source metadata until full BLAKE3 tooling and custody sealing are available.

No real forensic evidence is committed to the repository. The test fixture under `examples/intake/` is synthetic.

## Smoke test

Run:

```bash
python3 scripts/validate_intake_fixture.py
```

The smoke test verifies that the command:

- preserves the original filename;
- computes SHA-256 from raw bytes;
- writes an initial Landing-zone EvidenceArtifact record;
- writes a matching Intake CustodyEvent;
- uses only synthetic fixture data.

## Remaining work

- Add approved BLAKE3 dependency/tooling.
- Add stronger JSON Schema validation after dependency policy is set.
- Add account registry integration for CHK-09.
- Add TriTRPC BEACON_COMMIT receipts.
- Add immutable object storage backing and explicit hash manifests.
- Keep real evidence outside the public repo.
