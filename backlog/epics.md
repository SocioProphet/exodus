# Epic backlog

## Epic 1 — Repository bootstrap
Create the initial monorepo, license, docs, and schemas.

## Epic 2 — Provider abstraction layer
Model providers, accounts, domains, dependencies, and migration units.

## Epic 3 — Sovereignty scoring
Implement ERI and Provider Control Surface scoring.

## Epic 4 — Dashboard MVP
Build overview, provider estate map, and domain progress.

## Epic 5 — Export ledger
Track export runs, manifests, hashes, and validation state.

## Epic 6 — Recommendation engine
Rank next actions by expected sovereignty gain and effort.

## Epic 7 — Platform integration
Embed the dashboard into the broader platform.

## New epics
- Phase 1 topology and census pipeline
- Phase 2 budget and archival planner
- Recommendation engine with explainable score deltas
- Proof and verification ledger
- Provider capability matrix and open-target catalog

## Processing and enrichment
- Add canonical Document IR and chunk schemas.
- Implement deterministic document transformation and normalization before learned enrichment.
- Evaluate `SocioProphet/h-net-dynamic-chunking` as an optional adaptive chunking overlay.
- Implement mention / relation / coreference enrichment inspired by IBM SIRE lineage on open models and open runtimes.
- Add Phase 4 synthetic fixtures and acceptance tests.
