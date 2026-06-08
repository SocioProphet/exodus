# Synthetic Exodus Migration Workroom demo

Status: synthetic v0 fixture.

This document describes the Exodus-side fixture for the governed Exodus Migration Workroom demo tracked from `SocioProphet/sociosphere#478`.

## Boundary

This is not a real-provider extraction demo.

The fixture:

- uses no Apple, Google, or Microsoft credentials;
- performs no live provider API calls;
- performs no destructive actions;
- performs no provider-side writes;
- uses deterministic synthetic data only.

## Files

- `schemas/exodus-run.v0.schema.json` — canonical schema for the synthetic Exodus run object.
- `examples/synthetic-tenant-a/exodus-run.json` — synthetic Apple/Google/Microsoft exit-readiness run.
- `scripts/validate_exodus_demo.py` — offline validator and cross-reference checker.

## What the fixture proves

The fixture proves that Exodus can represent a synthetic migration run with:

- provider topology for Apple, Google, and Microsoft;
- account/root inventory;
- asset census by provider and domain;
- export ledger and evidence references;
- ERI score and PCS-by-provider score explanations;
- blockers;
- recommendations;
- Phase 2 budget proposal waves.

## What the fixture does not prove

The fixture does not prove:

- real provider ingestion;
- credentialed connector operation;
- export automation;
- chain-of-custody sealing for real evidence;
- migration execution;
- UI readiness.

## Validation

Run:

```bash
python3 scripts/validate_exodus_demo.py
```

The validator checks:

- schema shape when `jsonschema` is available;
- synthetic boundary flags;
- Apple/Google/Microsoft provider presence;
- account/provider references;
- asset/provider references;
- evidence/provider references;
- score/evidence references;
- blocker/evidence references;
- recommendation dependencies and evidence references;
- budget wave/provider/evidence references.

## Workspace bridge

The next repository in the demo sequence is `SocioProphet/prophet-workspace`.

The workspace bridge should wrap this Exodus run in a Professional Workroom with references to:

- the Exodus run fixture;
- provider topology;
- asset census;
- export ledger;
- ERI/PCS score explanations;
- blockers;
- recommendations;
- Phase 2 budget proposal;
- generated report/dashboard artifacts through the Office Plane.

## Sociosphere bridge

The final repository in the v0 sequence is `SocioProphet/sociosphere`.

Sociosphere should record how the Exodus fixture and Workspace workroom map into the control-plane state model:

- declared state;
- observed state;
- disposition state;
- summary state;
- controlled mutation boundaries.
