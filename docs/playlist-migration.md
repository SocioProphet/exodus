# Playlist Migration Plan

## Status

Planned Exodus / evidence-fabric media migration surface.

## Purpose

Music and video migration is not credible without playlist preservation. Users do not only own files; they own organization, order, context, library structure, and curated collections.

This document defines the first playlist migration plan for Exodus.

## Scope

Playlist migration covers:

- music playlists,
- video playlists,
- mixed media playlists,
- album/project queues,
- user-created ordered collections,
- provider/library playlist IDs,
- playlist membership and ordering,
- unresolved entries,
- duplicate entries,
- source aliases and canonical blob links,
- Linux-compatible playlist derivatives.

## Provider surfaces

Initial provider/library surfaces include:

- Apple Music / iTunes library playlists,
- local M3U/M3U8/PLS playlists,
- Google Takeout media playlist metadata where available,
- YouTube/YouTube Music export metadata where user-owned/exportable,
- OneDrive/local Windows media playlists,
- folder-order derived playlists for user-selected media folders.

## Custody rules

1. Preserve the raw playlist or source library record first.
2. Preserve provider/library playlist IDs as source aliases.
3. Preserve original order.
4. Preserve unresolved entries as blockers, not silent drops.
5. Resolve entries to canonical media blobs where possible.
6. Emit Linux-compatible playlist derivatives only after source mapping is recorded.
7. Never erase duplicate entries unless the user explicitly requests playlist normalization.

## Canonical playlist model

A playlist migration record should capture:

- provider or local source,
- playlist ID,
- playlist title,
- playlist type,
- source locator,
- raw evidence ref,
- ordered entries,
- per-entry original locator,
- per-entry canonical blob ref where resolved,
- per-entry status,
- output playlist refs,
- unresolved entry count,
- duplicate entry count,
- generated-at timestamp.

## Entry states

Playlist entries may be:

- `resolved`,
- `missing-source`,
- `duplicate-preserved`,
- `blocked-access-control`,
- `metadata-only`,
- `unsupported`,
- `pending`.

## Output derivatives

First-pass Linux-compatible derivatives:

- M3U8 for stable UTF-8 path playlists,
- M3U where legacy compatibility is required,
- JSON sidecar with canonical refs and source aliases,
- CSV only for human review/export, not canonical state.

## Path policy

Playlist derivatives should use stable relative paths where possible.

Absolute source-provider paths should remain evidence aliases, not derivative playback paths.

## Dashboard behavior

Exodus Dashboard should show:

- playlists discovered,
- playlists landed,
- entries resolved,
- entries unresolved,
- duplicate entries preserved,
- derivative playlists generated,
- blockers by provider/source,
- proof-pack refs.

## Relationship to owned media

Playlist migration depends on owned media raw custody and ownership/use attestation where entries point to media files.

Public distribution remains separately gated. Playlist preservation for a private local library does not imply public distribution rights.
