# Owned Media Attestation Validation

## Status

Bootstrap validation note.

## Purpose

This note defines how Exodus validates owned-media attestation records for private migration and local Linux-ready derivatives.

## Validation intent

The validator should prove that:

1. the attestation record conforms to `packages/contracts/owned-media-attestation-record.schema.json`,
2. captured private-use attestations permit private use,
3. captured private-use attestations permit local derivative generation,
4. external/public use remains gated unless a separate capable scope is recorded,
5. raw custody and context references are preserved.

## Required fixture

- `examples/owned-media-attestation-record.example.json`

## Expected private migration posture

A normal personal-library record should have:

- `attestationStatus: captured`
- `attestationScope: personal-use`
- `privateUseAllowed: true`
- `localDerivativeAllowed: true`
- `publicDistributionStatus: separate-clearance-required`

## Why this matters

Exodus should not behave as a media police system for private libraries. The system records that the user attested ownership or authorization, captures supporting evidence and context, and allows private migration and local derivatives. Wider publication or marketplace use remains a separate gate.

## Follow-on

Add an executable validator and include it in the complete evidence-fabric validation command once the connector accepts the file write.
