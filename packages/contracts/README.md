# packages/contracts

Canonical contracts for Exodus.

This package should become the single source of truth for:

- provider topology objects
- asset census objects
- dependency and blocker objects
- export and evidence records
- verification results and proofs
- processing and chunking objects
- budget and planning objects
- score explanations and dashboard payloads

## Contract groups

### Discovery and planning
- provider topology snapshot
- asset census
- dependency graph
- size / temperature profile
- exportability report
- budget proposal

### Execution and evidence
- export run
- evidence artifact
- verification result
- cutover event

### Processing and enrichment
- document IR
- canonical chunk
- chunk overlay
- enrichment output
- benchmark run

### Guidance and scoring
- progress snapshot
- score explanation
- blocker
- recommendation
- open target
- provider capability

## Contract rules

- schemas and type definitions must stay phase-aware
- contracts must distinguish archive progress from cutover progress
- processing contracts must preserve provenance back to evidence artifacts and source spans
- chunk overlays must never replace canonical custody boundaries
- every score-facing object must be explainable and evidence-linkable
- dashboard payloads should derive from contracts, not invent parallel shapes

## Near-term implementation order

1. discovery and planning contracts
2. execution and evidence contracts
3. document IR and canonical chunk contracts
4. enrichment and benchmark contracts
5. executable typed bindings and validation
