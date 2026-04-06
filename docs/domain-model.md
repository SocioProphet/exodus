# Domain model

Exodus models **exit claims**, not just exports.

The domain is organized around six layers:

1. **Provider and account topology**
2. **Assets, collections, and migration units**
3. **Dependencies, control surfaces, and trust boundaries**
4. **Evidence, verification, and progress claims**
5. **Processing, normalization, enrichment, and chunk overlays**
6. **Recommendations, targets, and cutover events**

## Core entities

### Provider
A vendor or platform family.
Examples: Apple, Google, Microsoft.

### Account
A provider-scoped identity, tenant, or administrative boundary.
Examples: Apple ID, Google account, Google Workspace tenant, Microsoft 365 tenant.

### CapabilityDomain
A major domain of lock-in or migration work.
Examples:
- identity
- mail
- storage
- photos
- notes
- office docs
- calendar
- chat
- contacts
- AI assistants
- device sync
- payments / subscriptions

### ProviderCapability
A provider-specific capability surface within a domain.
Examples:
- Google Drive shared drives
- iCloud Photos shared albums
- Microsoft Teams meetings
- Google Docs native documents

### AssetCollection
A bounded collection of user or tenant assets.
Examples:
- iCloud Photos account 1
- Google Drive personal account
- OneDrive family tenant
- Exchange shared mailbox set

### MigrationUnit
The smallest unit that can be moved, preserved, replaced, or decommissioned.
Examples:
- single mailbox
- photo library
- notes corpus
- calendar set
- collaborative document workspace

### Dependency
A concrete lock-in edge.
Examples:
- proprietary file format
- provider-only identity federation
- proprietary photo sidecar metadata
- vendor AI workflow dependency
- shared-folder collaboration lock-in

### TrustBoundary
A boundary that constrains access, exportability, or verification.
Examples:
- Apple trusted-device boundary
- Google Workspace admin boundary
- encrypted vault boundary
- family-sharing boundary

### ExportRun
A collection or export attempt with manifests, hashes, outputs, and status.

### EvidenceArtifact
A raw or derived artifact used to support a claim.
Examples:
- archive bundle
- manifest row
- hash file
- exported note
- permission report
- parsed metadata JSON

### VerificationResult
A proof-bearing result stating whether a claim is verified and how.
Examples:
- export verified complete
- hash matches manifest
- local copy incomplete
- provider limitation prevents verification

### ProgressSnapshot
A scored and explainable summary of scope state at a point in time.

### ScoreExplanation
A decomposed explanation of why a score has a given value.
It should always answer: what helped, what hurt, what remains blocked.

### Blocker
A condition that prevents or delays progress.
Examples:
- ADP enabled and web access off
- external collaborator dependence
- no export path for native object
- replacement target not selected

### Recommendation
A ranked next action with expected sovereignty gain and effort.

### OpenTarget
The desired open or reduced-dependence replacement state.
Examples:
- local-first archive
- self-hosted groupware
- open cloud + open format
- standards-based identity replacement

### CutoverEvent
A recorded move from provider-dependent operation to a new target state.
Examples:
- mailbox switched
- photo sync disabled
- identity provider replaced
- Teams workflow retired

## Processing entities

### CorpusSlice
A bounded set of artifacts selected for Phase 4 processing.
Examples:
- all PDFs from a single mailbox export
- a photo library subset for OCR and metadata extraction
- a note corpus for normalization and entity extraction

### DocumentIR
The canonical normalized representation of a document or semi-structured object.
It must preserve:
- source artifact references
- stable block identifiers
- page and span provenance
- layout-aware structures such as sections, tables, figures, and attachments

### CanonicalChunk
A deterministic chunk derived from DocumentIR.
Canonical chunks are the baseline retrieval and review units. They must be reproducible and stable across reruns unless the source or normalizer version changes.

### ChunkOverlay
An optional alternative chunk view over the same DocumentIR.
Examples:
- H-Net adaptive chunks
- semantic merge windows
- table-aware retrieval windows

Chunk overlays are **not** custody boundaries and do not replace canonical chunks.

### EnrichmentRun
A bounded execution of one or more enrichment passes over a CorpusSlice.
Examples:
- entity extraction
- relation extraction
- coreference resolution
- sensitivity classification
- ontology mapping
- adaptive chunking

### EnrichmentOutput
A normalized output from an enrichment pass with confidence and provenance.
Examples:
- mention span
- linked entity
- relation triple
- coreference cluster
- sensitivity label
- chunk salience score

### BenchmarkRun
A reproducible comparison across processing strategies.
Examples:
- deterministic chunking vs H-Net overlay
- OCR engine A vs engine B
- baseline entity linker vs domain-adapted linker

## Core relationships

- Provider `has_many` Accounts
- Provider `has_many` ProviderCapabilities
- Account `has_many` AssetCollections
- AssetCollection `contains` MigrationUnits
- AssetCollection `has_many` Dependencies
- AssetCollection `has_many` ExportRuns
- ExportRun `produces` EvidenceArtifacts
- EvidenceArtifact `supports` VerificationResults
- VerificationResult `supports` ProgressSnapshots and ScoreExplanations
- Dependency `reduces` ERI and raises PCS
- Blocker `prevents` Recommendations and CutoverEvents from completing
- OpenTarget `addresses` Dependencies
- Recommendation `targets` Dependencies, Blockers, or MigrationUnits
- CutoverEvent `advances` MigrationUnit state
- ProgressSnapshot `summarizes` Account / Provider / Domain scopes
- CorpusSlice `selects` EvidenceArtifacts and MigrationUnits for processing
- DocumentIR `normalizes` one or more EvidenceArtifacts
- CanonicalChunk `derives_from` DocumentIR
- ChunkOverlay `references` DocumentIR and CanonicalChunks
- EnrichmentRun `consumes` CorpusSlice, DocumentIR, and/or chunks
- EnrichmentOutput `supports` VerificationResults, Recommendations, and ScoreExplanations
- BenchmarkRun `compares` ChunkOverlay or EnrichmentRun strategies

## State model alignment

Migration units progress through the canonical state machine:

`Discovered -> Scoped -> Preserved -> Exported -> Verified -> Normalized -> MappedToOpenTarget -> Replaced -> CutOver -> Decommissioned`

Side states:
- Blocked
- PartiallyExported
- VerificationFailed
- ProviderLimited
- NeedsHumanReview

Processing state overlays:
- NotSelectedForProcessing
- NormalizationPending
- Normalized
- EnrichmentPending
- Enriched
- BenchmarkPending
- Benchmarked

## Important design rule

Exodus should never confuse these four ideas:

1. **bytes copied**
2. **claim verified**
3. **document normalized**
4. **dependence reduced**

Archive completion is not the same as normalization, normalization is not the same as open conversion, and open conversion is not the same as cutover.
