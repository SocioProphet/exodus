# Makefile Complete Validation Follow-up

## Status

Follow-up required after the evidence-fabric contract tranche lands.

## Purpose

This branch now contains a complete evidence-fabric validation entrypoint:

```bash
python3 scripts/validate_complete_evidence_fabric_contracts.py
```

It includes:

- dashboard state validation,
- migration wave and proof-pack validation,
- notes provider validation,
- owned media source validation,
- owned media attestation validation.

## Current Makefile state

The current `Makefile` was added earlier in this tranche and points `validate-evidence-fabric-contracts` at the prior aggregate validator.

A follow-up should update that target to call:

```bash
python3 scripts/validate_complete_evidence_fabric_contracts.py
```

## Why this is a follow-up

The connector path in this session is reliable for additive files. It does not currently expose a safe high-level overwrite for existing files, and the low-level commit helpers did not expose enough tree metadata in the commit fetch output to justify mutating the existing `Makefile` blindly.

## Desired final target

```make
validate-evidence-fabric-contracts:
	python3 scripts/validate_complete_evidence_fabric_contracts.py
```
