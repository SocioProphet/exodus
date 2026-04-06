# packages/scoring

Scoring engine for Exodus.

This package should implement:

- Exit Readiness Index (ERI)
- Provider Control Surface (PCS)
- archive progress
- open conversion progress
- cutover progress
- control-surface reduction
- expected-gain estimates for recommendations
- score explanation generation

## Inputs

- dependency graph
- blockers
- verification results
- exportability report
- budget proposal
- open target mapping
- cutover events

## Outputs

- scoped ERI values (provider, account, domain, migration unit)
- scoped PCS values
- score explanations
- recommendation priority signals

## Non-goals

This package should not own collection logic.
It should consume normalized contracts and produce explainable decisions.
