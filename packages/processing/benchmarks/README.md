# packages/processing/benchmarks

Benchmark harnesses for Phase 4 processing strategies.

## Initial benchmark lane

`deterministic_vs_hnet`

Compare:
- deterministic canonical chunking baseline
- H-Net dynamic chunk overlay

## Required metrics

- retrieval_hit_rate_at_k
- provenance_retention_rate
- rerun_stability
- mean_chunk_count
- processing_cost_seconds

## Design rules

- benchmarks must never mutate DocumentIR
- chunk overlays compete on top of the same normalized corpus
- every metric result must be traceable to a fixed corpus manifest and query set
