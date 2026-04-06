# apps/console

This app is the **Exodus Dashboard**.

It is phase-aware.
The dashboard should not pretend the full migration engine exists before the earlier phases produce enough evidence.

## Phase-aware MVP behavior

### Phase 1 — discovery
- overview
- provider topology
- asset census
- dependency graph
- exportability
- size / temperature

### Phase 2 — planning
- ingestion plan
- archival plan
- processing plan
- budget proposal

### Later phases
- preservation ledger
- evidence and verification
- blockers
- recommendations
- score explanations
- cutover progress

## Suggested stack

Keep this open and portable.

Preferred direction:
- TypeScript web UI
- shared contracts from `packages/contracts`
- scoring service or library from `packages/scoring`
- graph / panel views suitable for later platform embedding

## Key rule

The UI should always show why a score or recommendation exists.
Opaque status pills are not sufficient.
