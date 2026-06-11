# Notes Provider Ingest Plan

## Status

Planned Exodus / evidence-fabric integration surface.

## Purpose

This document adds first-class notes migration coverage for Apple/iCloud Notes, Microsoft OneNote, and Google Keep.

Notes are not just small text files. They may include rich text, checklists, embedded images, attachments, links, drawings, audio, OCR-relevant images, collaboration metadata, folders, labels, and provider-specific sync state. Exodus must preserve raw exports first, then normalize into open derived records.

## Provider families

### Apple / iCloud Notes

Apple Notes and iCloud Notes are treated as Apple-provider ingress surfaces.

Expected source paths:

- iCloud Notes web/export capture
- Apple Notes app export where available
- local trusted-device collection
- user-provided archive bundles
- screenshot or PDF exports for locked or difficult notes

Important metadata:

- folder path
- note title
- created and modified times where available
- attachment references
- locked-note status if known
- collaboration/share status if known
- source account and device context

### Microsoft OneNote

OneNote is treated as a Microsoft-provider ingress surface.

Expected source paths:

- OneNote notebook exports
- Microsoft Graph or OneDrive-backed notebook metadata later
- local app export where available
- PDF/HTML/package exports
- user-provided notebook archive bundles

Important metadata:

- notebook
- section
- page
- page title
- page creation and modification times where available
- embedded files
- ink/drawing presence
- audio/transcription presence
- collaboration/share status if known

### Google Keep

Google Keep is treated as the Google notes equivalent for first-pass Exodus support.

Expected source paths:

- Google Takeout Keep export
- Keep HTML/JSON export payloads
- labels
- archived/pinned/trash state where available
- image and audio attachments where available

Important metadata:

- note title or synthetic title
- text body
- labels
- color/category if available
- pinned/archived/trash flags
- created and modified times where available
- attachment references
- source Takeout bundle reference

## Custody rules

1. Raw note exports are preserved as `EvidenceBlob` objects before parsing.
2. Provider-specific filenames and IDs are source aliases, not canonical identity.
3. Attachments are separate blobs linked back to the note record.
4. Rich-text, OCR, transcript, markdown, and plain-text views are derived records.
5. Locked, unsupported, or partially exported notes become blocked objects, not silent drops.
6. No provider-side deletion is recommended until proof-pack, mirror parity, and cooling-off gates pass.

## Normalized note object expectations

A normalized note should expose:

- provider
- source export method
- source locator
- title
- container path
- note body text or derived text ref
- attachment blob refs
- labels/tags/folders
- created and modified timestamps where available
- raw evidence refs
- parser run refs
- validation refs
- blocked reason if processing failed

## Dashboard behavior

The Exodus Dashboard should show notes as a distinct migration wave type. Users should be able to see:

- notes discovered
- notes landed
- notes deduped
- notes with attachments
- notes blocked or partially exported
- notes converted to open formats
- notes eligible for source-provider downgrade/deletion after validation

## Boundary

Exodus owns note migration planning, dashboard state, recommendations, and proof-pack summaries.

The evidence fabric owns raw note custody, hash identity, source alias preservation, parser runs, validation, and object-store/Postgres registration.
