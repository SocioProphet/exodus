# Scoring model

## Core scores

### Exit Readiness Index (ERI)
ERI is a 0-100 score summarizing how close a scope is to a viable exit or sovereignty posture.

### Provider Control Surface (PCS)
PCS is a 0-100 score summarizing how strongly a provider still controls identity, custody, workflow, policy, economics, and social dependencies for a scope.
Higher PCS means more provider control.

## Design rules

- scores must be explainable
- only evidenced actions can change scores materially
- archive-only progress must not be confused with cutover progress
- blocked or provider-limited states must reduce confidence
- every score should have a paired `ScoreExplanation` object

## ERI decomposition

Exodus should compute ERI from four explicit components:

- `archive_progress`
- `open_conversion_progress`
- `cutover_progress`
- `control_surface_reduction`

A useful conceptual shape is:

`ERI = weighted(archive_progress, open_conversion_progress, cutover_progress, control_surface_reduction) - blocker_penalty - uncertainty_penalty`

## PCS axes

PCS should aggregate provider control across the following axes:

- identity control
- data custody
- format control
- workflow control
- device control
- policy control
- economic control
- social / network control

## Scoring rules

- soft claims do not count as verified progress
- partial exports count less than full verified exports
- open-format conversion counts separately from raw extraction
- replacement cutover counts more than archive-only capture
- shared or collaborative assets retain control-surface penalties until collaboration dependence is actually reduced
- blocked assets reduce achievable score until the blocker is resolved or explicitly accepted

## Score explanation contract

Every displayed score should be accompanied by a machine-readable explanation that can answer:

- which factors increased the score
- which dependencies reduced the score
- which blockers are dominant
- what evidence supports the current state
- what next action would most improve the score

## Recommended implementation order

1. implement `PCS` by control-surface axis
2. implement `archive_progress`, `open_conversion_progress`, `cutover_progress`, `control_surface_reduction` separately
3. derive `ERI` from those components
4. emit `ScoreExplanation` alongside every computed score
