# packages/processing

Open processing layer for Exodus.

This package area is responsible for the Phase 3 / Phase 4 ingestion, normalization, enrichment, and benchmarking pipeline:
- document transformation
- layout-aware parsing
- canonical document IR
- deterministic canonical chunking
- enrichment passes (entity, relation, coreference, classification)
- optional adaptive chunking overlays
- benchmark harnesses for comparing processing strategies

## Design rules

1. Deterministic preservation first.
2. Deterministic normalization second.
3. Canonical chunking third.
4. Model-driven enrichment fourth.
5. Adaptive chunking is optional and must never replace canonical document boundaries.
6. Every derived output must retain provenance back to source artifacts and spans.
7. Benchmarking must compare quality, provenance retention, and rerun stability together.

## Initial benchmark lane

The first benchmark lane is:
- deterministic chunk baseline
- H-Net dynamic chunk overlay

Measured on:
- retrieval utility
- provenance retention
- chunk stability across reruns
- downstream enrichment impact
- processing cost
