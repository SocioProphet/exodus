# Phase 1 crawl specification

Phase 1 is metadata-first.

It must avoid indiscriminate blob ingestion unless required to establish confidence or verify a specific claim.

## Required inventories

### Provider topology inventory
- providers
- accounts / tenants
- administrative control surfaces
- identity surfaces
- shared structures
- sync endpoints
- collaboration edges

### Asset census
- object counts
- byte counts
- type distributions
- native vs open format distributions
- age buckets
- hot / warm / cold / archive classification proposal

### Dependency graph
- workflow dependencies
- collaboration dependencies
- identity dependencies
- automation / AI dependencies
- device dependencies
- social/network dependencies

### Confidence / completeness inventory
- discovered directly
- inferred
- blocked
- requires human review
- unverifiable in current phase

## Discovery principles
- prioritize APIs and inventories over bulk export
- preserve provider-native identifiers where possible
- emit evidence-backed confidence labels for all inferred facts
- separate exportability from openness
- distinguish archive-only viability from true replacement viability

## Expected outputs
- provider-topology-snapshot.v1.json
- asset-census.v1.json
- dependency-graph.v1.json
- size-temperature-profile.v1.json
- exportability-report.v1.json
