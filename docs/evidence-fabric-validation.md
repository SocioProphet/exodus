# Evidence Fabric Contract Validation

## Status

Bootstrap validation runbook.

## Purpose

This document records the validation entrypoints for the Exodus evidence-fabric dashboard, migration, notes, and owned-media contracts.

## Preferred complete validation command

Run from the repository root:

```bash
python3 scripts/validate_all_evidence_fabric_contracts.py
```

This runs:

- `scripts/validate_evidence_dashboard_state.py`
- `scripts/validate_evidence_fabric_dashboard_contracts.py`
- `scripts/validate_notes_source_profiles.py`
- `scripts/validate_owned_media_source_profile.py`

## Makefile status

The current `Makefile` target `validate-evidence-fabric-contracts` points at the earlier aggregate validator. A follow-up should update it to call `scripts/validate_all_evidence_fabric_contracts.py` so owned-media validation is included in the default evidence-fabric validation path.

## Expected output

```text
OK: all Exodus evidence-fabric contract validators passed
```

## Coverage

The complete validator covers:

- dashboard state,
- migration wave planning,
- proof-pack summaries,
- Google Keep / iCloud Notes / OneNote source profiles,
- owned music and video source profiles.
