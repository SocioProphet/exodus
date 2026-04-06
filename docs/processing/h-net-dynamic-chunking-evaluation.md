# h-net-dynamic-chunking evaluation for Exodus

## Verdict

`SocioProphet/h-net-dynamic-chunking` is a good fit for Exodus as an **optional adaptive chunking accelerator** in **Phase 4 (process and normalize)** and **Phase 5 (retrieval and guidance)**. It is **not** a substitute for the deterministic structural segmentation required in Phase 1 and Phase 2.

## Why it fits

The repository implements dynamic chunking for hierarchical sequence modeling and exposes a `DynamicSequenceChunker` plus an `HNet` wrapper for learned multiscale segmentation.

## Where it belongs in Exodus

Use it after we already have a canonical document representation with:
- extracted text
- layout blocks
- tables
- figures
- section boundaries
- page provenance
- ACL and source metadata

Then apply adaptive chunking to create:
- hierarchical retrieval chunks
- cross-section semantic windows
- compact multi-scale summaries
- salience-weighted review units

## Where it does **not** belong

Do not use learned chunking for:
- provider topology discovery
- size/budget estimation
- custody manifests
- canonical paragraph/table boundaries
- legal preservation outputs

Those stages must remain deterministic and explainable.

## Exodus benchmark policy

H-Net must compete against the deterministic canonical chunker on the same `DocumentIR`.

Required metrics:
- retrieval hit rate at K
- provenance retention rate
- rerun stability
- mean chunk count
- processing cost
- downstream enrichment delta (entity / relation / coreference quality)

Promotion criteria from experimental to supported should require:
- retrieval improvement without provenance regression
- rerun stability above the agreed threshold
- acceptable cost envelope for the target corpus size

## Recommendation

Add `h-net-dynamic-chunking` to Exodus as an optional processing plugin behind a feature flag and benchmark it continuously against deterministic baselines.
