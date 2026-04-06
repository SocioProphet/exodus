# Exodus

**Exodus** is the open-source migration, evidence, and sovereignty platform for measuring, planning, and executing movement out of closed vendor control surfaces.

It is not just a one-time export tool.

It is a governed product capability with five connected functions:

1. **Discover** provider topology, assets, dependencies, control surfaces, and confidence gaps.
2. **Plan** ingestion, archival, processing, and budget waves before moving bulk data.
3. **Preserve and ingest** raw evidence, manifests, and validation signals.
4. **Process and normalize** documents, media, metadata, and derived analytical records.
5. **Score and guide** progress and the next highest-value steps to reduce control-surface dependence.

## Quick publish

```bash
python3 scripts/validate_examples.py && ./scripts/publish_to_github.sh SocioProphet exodus public
```


## Canonical product language

- **Program / repo / product name:** Exodus
- **User-facing UI:** Exodus Dashboard
- **Core score:** Exit Readiness Index (ERI)
- **Secondary score:** Provider Control Surface (PCS)
- **Execution plane:** Exodus Engine

## Why this exists

Most migration tooling is file-centric and event-blind. It can copy objects but cannot answer:

- How dependent are we, really?
- What is still trapped behind provider-specific APIs, identities, formats, workflows, and AI services?
- What is the next highest-value move to reduce dependence?
- Can we prove progress with evidence rather than anecdotes?
- What should we ingest now, what should stay metadata-only, and what should be archived later?

Exodus answers those questions.

## Initial scope

Providers in scope first:
- Apple
- Google
- Microsoft

Possible later expansion:
- Dropbox
- Slack
- Notion
- Adobe
- GitHub
- Zoom
- Salesforce
- Atlassian

## Phase model

- **Phase 0** — scope, trust boundaries, target open states
- **Phase 1** — crawl, topology, index, metadata, size/temperature, exportability
- **Phase 2** — ingestion, archival, processing, and budget proposal
- **Phase 3** — preservation and intake execution
- **Phase 4** — normalization, extraction, token/entity/timeline processing
- **Phase 5** — dashboard governance, recommendations, continuous monitoring

## Platform shape

- **Open execution primitives:** Kafka + Beam + Drill
- **Canonical storage model:** raw lake + derived lake + immutable manifests
- **Dashboard role:** map, plan, prove, score, guide, and report
- **Source adapters:** export/archive tools, API collectors, local trusted-device collectors, notes/media/document adapters

## Monorepo layout

- `apps/console/` — Exodus Dashboard
- `packages/contracts/` — canonical contracts, schemas, and typed object grammar
- `packages/scoring/` — ERI, PCS, recommendation scoring, and explanation logic
- `packages/adapters/` — provider adapters and collector capability models
- `schemas/` — persisted-record JSON Schemas
- `docs/` — product, architecture, phase specs, domain, roadmap
- `examples/` — synthetic tenants and worked examples
- `backlog/` — epics and milestone backlog

## Open-source posture

- License: MIT
- Open-first formats: JSONL, Parquet, Iceberg
- Open execution: Beam on Flink/Spark, Drill query plane
- Cloud use is allowed as infrastructure, but open primitives remain canonical

## First milestone

Deliver a working dashboard that can:

1. ingest Apple, Google, and Microsoft metadata and export state,
2. build a provider topology snapshot and asset census,
3. compute an explainable initial ERI and PCS,
4. surface blockers and recommendations,
5. produce a machine-readable Phase 2 budget proposal.

## 2026 ingestion and enrichment architecture

Exodus now includes an explicit Phase 3 / Phase 4 document pipeline inspired by IBM's staged unstructured-data processing model, but implemented on open primitives. See `docs/processing/sire-inspired-pipeline-2026.md` and `docs/processing/h-net-dynamic-chunking-evaluation.md`.

## Phase 4 processing

Exodus now treats `DocumentIR`, deterministic canonical chunking, enrichment outputs, and benchmark runs as first-class objects. The first benchmark lane compares the deterministic baseline against an H-Net adaptive overlay on the same normalized corpus.
