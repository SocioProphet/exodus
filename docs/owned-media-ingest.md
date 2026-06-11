# Owned Media Ingest and Linux Playback Plan

## Status

Planned Exodus / evidence-fabric integration surface.

## Purpose

Exodus must support user-owned music and video migration. Without owned media capture, export, metadata preservation, and Linux-ready conversion planning, Exodus will not cover the media libraries that keep many users tied to Apple, Google, and Microsoft ecosystems.

This document defines the first planning surface for owned media migration.

## Scope

Owned media includes user-controlled copies of:

- music files,
- music library exports,
- playlists,
- videos,
- home movies,
- downloaded media files,
- camera-roll videos,
- voice memos and audio recordings,
- podcast/audio archives where user-controlled,
- media metadata and artwork.

## Non-goal: bypassing DRM

Exodus should preserve metadata and exportability evidence for DRM-protected media, but it must not bypass DRM or access controls. DRM-locked assets become blocked or metadata-only records unless the user has an authorized export path.

## Provider and source surfaces

### Apple

Possible source surfaces:

- local Music app library files,
- iTunes/Music library XML exports where available,
- Finder/iCloud Drive media files,
- Photos library exports for user-created videos,
- Voice Memos exports,
- user-provided archive folders.

### Google

Possible source surfaces:

- Google Takeout exports,
- Google Drive media files,
- Google Photos exports for user-created videos,
- YouTube/YouTube Music export metadata where user-owned/exportable,
- user-provided archive folders.

### Microsoft

Possible source surfaces:

- OneDrive media files,
- Windows media library exports,
- Xbox/Microsoft media metadata where exportable,
- user-provided archive folders.

### Local / external storage

Possible source surfaces:

- USB disks,
- SD cards,
- local Music/Videos folders,
- phone/camera exports,
- NAS exports,
- existing Linux media directories.

## Custody-first rule

1. Raw source media is preserved as an `EvidenceBlob` before any conversion.
2. Source paths, library IDs, playlist IDs, provider IDs, and metadata are source aliases and evidence.
3. Derived Linux-ready files are new derivative records, not replacements for raw custody.
4. Conversion failures become blocked objects with explicit reasons.
5. DRM-protected or non-exportable assets remain blocked or metadata-only, not silently dropped.

## Linux-ready target formats

Preferred open or broadly Linux-compatible targets should be selected by media type and quality requirements.

First-pass targets:

- Audio archival: FLAC where lossless preservation is possible.
- Audio portable/playback: Opus or Ogg Vorbis where conversion is appropriate.
- Audio compatibility fallback: MP3 only when needed for device compatibility.
- Video container: Matroska (`.mkv`) for archival/open workflows.
- Video compatibility container: MP4 where broad playback compatibility is required.
- Video codecs: AV1, VP9, or H.264 depending on source, hardware support, and user policy.
- Subtitles: SRT or WebVTT where extractable.
- Metadata sidecars: JSON and/or MusicBrainz/Picard-compatible metadata where possible.

## Metadata preservation

Exodus should preserve:

- title,
- artist/creator,
- album/show/project,
- track number,
- disc number,
- genre,
- year/date,
- duration,
- bitrate,
- codec,
- container,
- sample rate,
- channels,
- resolution,
- frame rate,
- artwork/thumbnail refs,
- playlist membership,
- original path,
- provider/source ID,
- library export ID,
- checksum,
- conversion profile,
- conversion command digest.

## Dashboard behavior

Owned media should be a first-class Exodus migration panel.

Users should see:

- media discovered,
- raw media landed,
- unique media bytes landed,
- duplicate media eliminated,
- playlists preserved,
- metadata completeness,
- DRM/blocked assets,
- conversion queue status,
- Linux-ready derivatives created,
- proof packs generated.

## Conversion policy

Conversion should be policy-driven and opt-in per wave.

Default posture:

- preserve raw first,
- do not destructively transcode,
- prefer lossless extraction/remuxing before lossy conversion,
- create derivatives only after raw custody,
- record conversion tool/version/settings,
- keep conversion receipts and output hashes.

## Next design questions

The next discussion should decide:

- default audio archival target,
- default audio portable target,
- default video archival container,
- default video compatibility container,
- when to remux versus transcode,
- how to handle large video files and storage budgets,
- how to preserve playlists across providers,
- how to represent DRM-blocked media without unsafe bypass behavior,
- how to integrate MusicBrainz/Picard-style metadata enrichment.
