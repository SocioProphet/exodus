# Implementation spine

This document freezes the implementation direction enough to reduce churn.
It does not yet finalize every runtime choice.

## Repository posture

Exodus should begin as a single monorepo.

Reasons:
- contracts, scoring, adapters, and dashboard will evolve together at first
- phase grammar must stay synchronized
- score explanations and provider adapters will otherwise drift quickly

## Package boundaries

- `packages/contracts` — canonical contract source of truth
- `packages/scoring` — executable scoring and recommendation logic
- `packages/adapters` — provider-specific capability and exportability adapters
- `apps/console` — Exodus Dashboard

## Source-of-truth rule

Schemas and contracts should be treated as the semantic source of truth.
Runtime-specific code should conform to them, not invent parallel shapes.

## Runtime direction

Preferred early direction:
- TypeScript for dashboard and contract-adjacent packages
- Python for Beam pipelines and heavy processing where appropriate
- shared schema generation only after the contract layer stabilizes

## Execution plane

- Kafka for orchestration and workflow events
- Beam on Flink/Spark for processing
- Drill for query
- raw and derived lake for storage

## Immediate next hardening tasks

1. choose monorepo toolchain
2. add real schema validation in CI
3. add typed bindings from contracts
4. add synthetic fixtures to contract tests
