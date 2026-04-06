# packages/adapters

Provider-specific adapter and capability models for Exodus.

Adapters are responsible for discovery, inventory, exportability assessment, and execution hints.
They should not directly own global scoring.

## Responsibilities

- map provider APIs and export surfaces into Exodus contracts
- enumerate provider capability domains
- produce topology and asset census records
- record export paths, blockers, and verification constraints
- expose provider-specific planning hints for Phase 2

## Initial providers

- Apple
- Google
- Microsoft

## Important rule

Adapters must model provider limitations explicitly.
A missing export path, collaboration dependency, or trusted-device requirement is a first-class output, not an implementation note.
