# Phase 2 budget and archival specification

Phase 2 converts the discovery output into an execution plan.

## Plans produced

### Ingestion plan
- wave order
- metadata-only vs full-ingest decision
- human-led export requirements
- verification requirements

### Archival plan
- hot / warm / cold / archive placement
- retention expectations
- retrieval expectations
- verification-before-cooling rules

### Processing plan
- metadata-only extraction
- OCR eligibility
- token/entity/timeline eligibility
- deferral rules

### Budget proposal
- crawl budget envelope
- ingest budget envelope
- processing budget envelope
- retention budget envelope

## Decision rules
- favor metadata-first discovery when sovereignty gain is uncertain
- prioritize high-lock-in / high-centrality / high-unlock domains first
- treat archive-only wins separately from replacement wins
- do not cool evidence that is still under validation or active review
