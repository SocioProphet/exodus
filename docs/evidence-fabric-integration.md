# Evidence Fabric Dashboard Integration

## Status

Planned consumer contract for Exodus Dashboard and Exodus Engine.

## Purpose

Exodus is the user-facing migration, evidence, and sovereignty surface for moving out of closed vendor control surfaces. The evidence fabric provides the custody, hashing, dedupe, source alias, parsing, validation, and proof-pack substrate behind that experience.

This document defines how Exodus consumes evidence-fabric state without becoming the raw custody system itself.

## Core user promise

Exodus should help users answer:

- what is trapped in Apple, Google, Microsoft, or another provider,
- what has been safely landed into our own repository,
- what is duplicated,
- what is blocked,
- what has been normalized into open formats,
- what is eligible for provider downgrade or deletion after validation,
- and what proof exists for every migration wave.

## Integration surfaces

### 1. Provider topology and source census

Exodus consumes connector and acquisition summaries to display:

- provider accounts,
- source drives,
- folders and major asset families,
- estimated object counts,
- estimated byte sizes,
- source API/export limitations,
- confidence gaps.

### 2. Migration wave planner

Exodus groups source material into migration waves:

- local files,
- Google Drive,
- iCloud Drive,
- email,
- notes and mobile exports,
- browser and terminal captures,
- office documents,
- media.

Each wave records scope, expected size, target storage, planned parser/chunker routes, and rollback/cooling-off rules.

### 3. Evidence landing progress

Exodus displays broker state:

- acquisition runs,
- raw blobs landed,
- unique bytes landed,
- duplicate bytes eliminated,
- source aliases preserved,
- parser successes and failures,
- validation status.

### 4. Dedupe and source alias review

Exodus must show dedupe as proof, not as destructive cleanup.

If five source paths point to one SHA-256 blob, Exodus should display one canonical blob and five preserved source aliases.

### 5. Processing and enrichment queue

Exodus tracks derived processing state:

- parsed text,
- chunk windows,
- OCR/transcript derivatives,
- entity and timeline extraction,
- format conversion,
- rejected or unsupported objects.

### 6. Proof-pack export

Exodus consumes validation and manifest records to export:

- migration wave proof packs,
- source alias reports,
- mirror parity reports,
- source deletion eligibility reports,
- blocked-object reports,
- open-format conversion summaries.

## Provider posture

Apple, Google, Microsoft, and similar providers are ingress surfaces only. They are not canonical authority after raw custody has been established in the evidence repository.

No source-system deletion or account downgrade should be recommended until mirror parity, manifest parity, and cooling-off checks pass.

## Required dashboard states

Exodus Dashboard should expose these states:

- discovered
- planned
- landing
- landed
- deduped
- processing
- validated
- blocked
- proof-ready
- cooling-off
- deletion-eligible

## Required metrics

- Exit Readiness Index
- Provider Control Surface score
- migrated blob count
- migrated unique bytes
- duplicate bytes eliminated
- source aliases preserved
- blocked objects
- open-format conversions
- proof packs generated
- deletion-eligible source objects

## Boundary

Exodus owns user experience, planning, scoring, and guidance.

The evidence fabric owns raw custody, hash identity, source alias preservation, manifests, parser runs, and validation records.

Semantic projection into SHIR, Knowledge Context, and graph surfaces is later-phase work and must not replace raw custody.
