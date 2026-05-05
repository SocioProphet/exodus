# Owned Media Export and Conversion Architecture

## Status

Planned Exodus / evidence-fabric media pipeline.

## Purpose

Owned media must be a first-class Exodus migration surface. Music, videos, home movies, voice memos, playlists, artwork, sidecars, and metadata often bind users to closed Apple, Google, and Microsoft surfaces as strongly as documents and email.

This document defines the first Linux-ready export and conversion architecture for user-owned media.

## Core posture

1. Preserve raw media first.
2. Record ownership or authorization attestation before local derivative generation.
3. Treat source paths, library IDs, provider IDs, playlists, and sidecars as evidence aliases.
4. Prefer remuxing over transcoding when streams are already Linux-compatible.
5. Create Linux-ready derivatives only after raw custody and attestation gates.
6. Preserve conversion commands, tool versions, profiles, output hashes, and failure reasons.
7. Treat locked, DRM-bound, or non-exportable media as blocked or metadata-only.
8. Public or marketplace distribution remains separately gated.

## Pipeline

### 1. Source discovery

Discover source libraries and exports:

- local Music/Videos folders,
- Apple Music/iTunes library files and XML where available,
- Apple Photos exports for user-created videos,
- Voice Memos exports,
- Google Takeout exports,
- Google Drive media,
- Google Photos exports,
- Microsoft OneDrive media,
- Windows media library exports,
- USB disks,
- SD cards,
- NAS folders,
- phone/camera exports.

### 2. Raw custody

Every source media object lands as an immutable raw blob before conversion.

Record:

- SHA-256,
- byte length,
- original path,
- source provider or local source,
- source alias set,
- file timestamps,
- provider metadata,
- sidecar metadata,
- playlist membership,
- attestation refs.

### 3. Probe and classify

Use a media probe step to inspect:

- container,
- audio codec,
- video codec,
- subtitle streams,
- chapters,
- attachments,
- duration,
- bitrate,
- sample rate,
- channel layout,
- resolution,
- frame rate,
- color metadata,
- embedded artwork,
- metadata tags.

### 4. Decide: copy, remux, transcode, or block

Decision order:

1. If the source is locked or access-controlled beyond authorized export, emit blocked or metadata-only.
2. If the container is inconvenient but streams are compatible, remux.
3. If the stream codec is lossless or already suitable, preserve and optionally create portable derivative.
4. If the stream codec is unsupported or too large for target use, transcode to policy-selected Linux-ready derivative.
5. If conversion fails, preserve raw and emit blocked conversion status.

## Default target policy

### Audio

#### Archival target

- FLAC for lossless archival when the source is lossless or can be preserved without lossy re-encoding.

#### Portable target

- Opus for efficient open playback derivatives.

#### Compatibility fallback

- MP3 only when required for legacy device compatibility.

### Video

#### Archival container

- Matroska (`.mkv`) as the preferred open archival container.

#### Compatibility container

- MP4 for broad device and browser compatibility when needed.

#### Codec policy

Preferred order depends on source, hardware, and user policy:

1. remux/copy existing streams when compatible,
2. AV1 for open long-term video derivatives when encoding time is acceptable,
3. VP9 for open web-compatible derivatives where AV1 is not practical,
4. H.264 for broad compatibility where open-codec purity is less important than playback reach,
5. preserve HEVC/H.265 by remux where already present and user policy accepts compatibility limitations.

### Subtitles and chapters

- Preserve embedded subtitle streams where possible.
- Extract text subtitles to SRT or WebVTT derivatives where appropriate.
- Preserve chapters and chapter titles as sidecar metadata.

### Metadata and artwork

- Preserve original embedded metadata.
- Emit JSON sidecar metadata for every derivative.
- Preserve artwork/thumbnail refs as evidence blobs or sidecars.
- Use MusicBrainz/Picard-style metadata enrichment only as a derivative enrichment step, not as a replacement for source metadata.

## Conversion profiles

### Profile: `audio-archive-flac`

Use for owned lossless music and high-value audio.

- raw preserved: required
- output: FLAC
- metadata sidecar: required
- artwork preservation: required
- lossy source handling: do not up-convert to pretend lossless; preserve original and optionally create portable derivative

### Profile: `audio-portable-opus`

Use for portable Linux/mobile playback.

- raw preserved: required
- output: Opus
- metadata sidecar: required
- default use: derivative playback copy

### Profile: `video-archive-mkv`

Use for archival videos and home movies.

- raw preserved: required
- output container: MKV
- stream copy preferred when possible
- subtitles and chapters preserved when possible
- conversion receipt required

### Profile: `video-compatible-mp4`

Use for broad playback compatibility.

- raw preserved: required
- output container: MP4
- codec policy: copy compatible streams first; otherwise transcode according to user policy
- subtitles may require conversion or sidecar export

## Playlists and libraries

Preserve playlists as first-class migration objects.

Required playlist handling:

- original playlist file or library record preserved as raw evidence,
- canonical playlist object records ordered entries,
- each entry links to source alias and canonical blob where known,
- unresolved entries become blockers,
- emit Linux-compatible playlist derivatives such as M3U/M3U8 where path mapping is stable,
- retain provider/library playlist IDs as source aliases.

## Storage budget policy

### Budget class: `custody-only`

- raw preserved,
- no derivatives unless required for metadata extraction,
- lowest immediate storage expansion.

### Budget class: `playback-ready`

- raw preserved,
- one Linux-ready derivative per selected object,
- balances migration usability and storage growth.

### Budget class: `archive-plus-portable`

- raw preserved,
- archival derivative where useful,
- portable derivative where useful,
- highest storage growth and should be explicit.

## Attestation and distribution gates

Private migration and local Linux playback derivatives require captured ownership/use attestation.

Public distribution, marketplace listing, publishing, resale, or sharing requires a separate distribution clearance gate.

Personal-use attestation is sufficient for private library migration and local derivatives, but not for public distribution.

## Failure and blocked states

Conversion jobs may end in:

- `succeeded`,
- `remuxed`,
- `transcoded`,
- `metadata-only`,
- `blocked-access-control`,
- `blocked-unsupported-format`,
- `blocked-storage-budget`,
- `failed-tool-error`.

Blocked media must remain visible in Exodus Dashboard with a reason and next action.

## Linux library targets

Initial Linux library targets:

- filesystem library with stable path policy,
- Jellyfin-style media server library,
- Kodi-style local library and playlists,
- MusicBrainz/Picard-compatible tagging workflow,
- generic M3U/M3U8 playlist export.

## Non-goals

- no DRM bypass,
- no public distribution clearance from private-use attestation alone,
- no destructive transcode over raw source,
- no silent dedupe that erases playlist or source alias evidence,
- no graph projection as canonical custody.

## Next implementation slices

1. Add `OwnedMediaConversionProfile` contract.
2. Add conversion profile examples.
3. Add conversion receipt contract.
4. Add playlist migration contract.
5. Add dashboard cards for owned-media landing, conversion, blockers, and proof packs.
