# Phase 4 benchmarking

Exodus treats benchmarking as a first-class governance activity, not an afterthought.

## Benchmark families

1. Chunking
2. OCR and layout extraction
3. Mention / relation / coreference enrichment
4. Classification and policy labeling

## Required benchmark properties

- fixed input corpus manifest
- fixed normalizer version
- declared processing strategy IDs
- explicit metrics with formulas
- reproducible output locations
- provenance-preservation checks
- rerun-stability checks

## First benchmark

`deterministic_vs_hnet`

This benchmark compares:
- canonical deterministic chunker
- H-Net adaptive overlay

It does **not** change the underlying DocumentIR.
