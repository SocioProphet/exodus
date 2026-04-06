# Architecture

## Canonical architecture

Edge Collectors -> Object Lake -> Kafka -> Beam -> Derived Lake -> Drill -> Sovereignty Dashboard

## Principle

- binaries do **not** go through Kafka
- Kafka carries registration, orchestration, state transition, and detection events
- raw objects remain immutable
- derived objects are versioned
- dashboard reads scored and normalized state, not ad hoc file trees

## Planes

### Ingest plane
Trusted-device export tools, API collectors, archive uploaders.

### Event plane
Kafka topics for intake, extraction, detection, timeline, and deadletter events.

### Processing plane
Beam jobs on an open runner (prefer Flink first).

### Query plane
Drill over JSONL / Parquet / Iceberg.

### UX plane
The Sovereignty Dashboard embedded in the broader platform.

## Product integration

This repository should remain logically separate from the main platform until the core contracts stabilize.
After that, the dashboard can be imported or mounted into the main platform as a dedicated product surface.
