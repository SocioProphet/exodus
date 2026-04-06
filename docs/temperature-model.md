# Temperature model

Temperature is an operational classification used for staging, retrieval expectations, and budget planning.

## Classes
- hot: active discovery, validation, review, or processing
- warm: verified and occasionally accessed
- cold: verified, low-touch, retained for evidence or fallback
- archive: very low expected retrieval and long retention horizon

## Inputs
- recent access likelihood
- verification state
- processing state
- legal / forensic relevance
- estimated future retrieval frequency

## Rules
- raw artifacts remain hot until verified
- derived analytics remain hot until stable materialization exists
- unresolved blockers keep linked artifacts warmer longer
