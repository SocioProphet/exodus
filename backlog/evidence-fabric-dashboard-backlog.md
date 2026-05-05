# Evidence Fabric Dashboard Backlog

## Status

Planned Exodus Dashboard workstream.

## Purpose

This backlog maps the evidence-fabric contracts in this branch to user-facing dashboard panels and actions. The goal is to accelerate user exodus from closed vendor control surfaces by making migration state, blockers, proof, and next actions visible.

## Contract inputs

- `EvidenceDashboardState`
- `MigrationWavePlan`
- `ProofPackSummary`
- `NotesSourceProfile`

## Dashboard panels

### 1. Provider control overview

Shows Apple, Google, Microsoft, and later providers with:

- Provider Control Surface score
- Exit Readiness Index
- discovered assets
- migrated unique bytes
- duplicate bytes eliminated
- blocked objects
- proof packs generated

Primary actions:

- inspect provider topology
- start a migration wave
- view blockers
- export provider-status report

### 2. Migration wave planner

Shows one row per planned wave:

- provider
- source type
- selection
- estimated objects
- estimated bytes
- target object store
- parser routes
- delete-source policy
- mirror parity requirement
- cooling-off requirement

Primary actions:

- create wave
- pause wave
- resume wave
- mark wave blocked
- generate proof pack after validation

### 3. Evidence landing monitor

Shows broker-derived state:

- acquisition runs
- raw blobs landed
- unique bytes landed
- source aliases preserved
- parser success/failure counts
- validation status

Primary actions:

- inspect acquisition run
- inspect duplicate cluster
- inspect source alias report
- retry parser
- export manifest summary

### 4. Notes migration panel

Shows Google Keep, iCloud Notes, and OneNote as first-class note surfaces.

For each provider, show:

- notes discovered
- notes landed
- notes with attachments
- notes blocked or partially exported
- rich text derivatives created
- OCR/transcript derivatives created
- open-format conversions

Primary actions:

- inspect notes-source profile
- start notes wave
- review blocked notes
- export notes proof pack

### 5. Proof-pack center

Shows proof packs by migration wave:

- status
- manifest refs
- validation refs
- source alias report
- mirror parity report
- blocked object report
- open-format conversion report
- source deletion eligibility
- provider downgrade eligibility

Primary actions:

- generate proof pack
- validate proof pack
- export user-readable report
- export machine-readable report
- start cooling-off window

### 6. Blockers and next actions

Aggregates blockers across all providers and waves.

Primary categories:

- mirror parity pending
- manifest parity pending
- unsupported export format
- locked note or encrypted object
- API quota or provider limitation
- parser failure
- missing source alias metadata
- cooling-off not complete

Primary actions:

- filter by provider
- filter by severity
- assign remediation wave
- export blocker report

## User workflow

1. Connect a source account or select a local export.
2. Preview provider topology and estimated size.
3. Create a migration wave.
4. Land raw content into canonical evidence storage.
5. Review dedupe and source aliases.
6. Process text, log, document, note, media, and attachment derivatives.
7. Review blockers and next actions.
8. Generate proof pack.
9. Start cooling-off window.
10. Mark source provider retained, downgraded, or deletion-eligible.

## Non-goals

- No provider deletion by default.
- No raw provider API authority after custody is established.
- No graph projection as the canonical system of record.
- No silent dedupe that erases source aliases.

## Next implementation slices

1. Render static dashboard cards from the example fixtures.
2. Add fixture-backed tests for dashboard-state parsing.
3. Add proof-pack summary download surface.
4. Add notes-provider wave creation panel.
5. Connect to evidence broker state after broker repo exists.
