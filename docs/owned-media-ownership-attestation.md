# Owned Media Ownership Attestation Policy

## Status

Planned Exodus / evidence-fabric policy for user-owned media migration.

## Purpose

Exodus should help users migrate their own media libraries without becoming a media-policing system.

For private migration, backup, indexing, Linux playback, and local library conversion, Exodus should require and preserve an ownership/use attestation plus supporting context. Exodus should not attempt to adjudicate every third-party intellectual-property question for personal imports.

Marketplace, public sharing, resale, redistribution, publishing, or commercial distribution are different surfaces. Those require an explicit distribution-clearance gate and are out of scope for the private migration default.

## Core rule

For owned media ingestion:

1. ask the user to attest that they own, created, purchased, licensed, or are otherwise authorized to migrate the media for personal use,
2. capture available supporting evidence and context,
3. preserve raw media first,
4. record the attestation as evidence,
5. permit private migration and Linux-ready derivative generation when the attestation gate passes,
6. block marketplace/public distribution unless a separate distribution-clearance gate passes.

## What Exodus records

The evidence fabric should capture:

- user attestation text,
- attestation time,
- attesting user/account reference,
- media object reference,
- source profile reference,
- acquisition run reference,
- evidence refs such as receipts, library exports, provider metadata, local file paths, sidecars, or device export manifests,
- source alias refs,
- conversion-policy refs,
- distribution clearance status.

## What Exodus does not do by default

Exodus does not:

- bypass DRM,
- remove access controls,
- infer redistribution rights from possession,
- police private libraries beyond recording the attestation gate,
- delete or alter raw source files,
- grant marketplace/public distribution clearance by default.

## Private-use default

The default owned-media state is:

- `personal-use-attested`,
- `private-library-allowed`,
- `local-conversion-allowed`,
- `marketplace-distribution-blocked`.

This gives users a practical migration path while keeping distribution-sensitive workflows gated.

## Distribution boundary

Marketplace or public distribution requires a separate policy decision and should not rely only on personal-use attestation.

Distribution clearance may require additional evidence such as:

- explicit license grant,
- creator/original-work attestation,
- public-domain or open-license evidence,
- marketplace-specific rights record,
- review/approval receipt.

## Compliance posture

The compliance objective is evidence capture, not omniscient enforcement.

Exodus records that:

- the user attested ownership or authorization,
- available evidence/context was captured,
- raw custody was preserved,
- conversion was performed only after the attestation gate,
- public distribution was blocked unless separately cleared.

## Dashboard behavior

The Exodus Dashboard should show owned media attestation state:

- attestation required,
- attestation captured,
- evidence captured,
- conversion allowed,
- distribution blocked,
- distribution clearance required,
- blocked due to DRM/access control,
- metadata-only record.

## Relationship to owned media ingest

This policy complements `docs/owned-media-ingest.md`.

Owned-media ingest defines source surfaces, formats, and conversion planning. This document defines the ownership/use attestation gate that controls whether private migration and derivative conversion may proceed.
