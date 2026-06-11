# AI Chat Export Ingest Plan

## Status

Planned Exodus / evidence-fabric integration surface.

## Purpose

AI chat histories are now critical personal and professional knowledge assets. Exodus must support migration, preservation, indexing, and document conversion for AI chat exports so users are not locked into a single assistant or provider UI.

This document defines the first ingest plan for ChatGPT/OpenAI and Claude/Anthropic chat exports, with room for later provider additions.

## Initial provider surfaces

### ChatGPT / OpenAI

Expected source path:

- provider data export archive,
- chat history HTML and structured export files where present,
- shared conversation export data where included,
- user-provided archive folders.

### Claude / Anthropic

Expected source path:

- provider data export archive,
- conversation history and account export files,
- workspace or organization export where the user is an authorized owner/admin,
- user-provided archive folders.

## Custody rules

1. Preserve the raw provider export archive as an immutable evidence blob.
2. Preserve each source file from the archive as raw or derived evidence according to extraction policy.
3. Treat provider IDs, conversation IDs, project/workspace IDs, shared-link IDs, filenames, and archive paths as source aliases.
4. Convert each conversation into a normalized document record.
5. Preserve attachments, generated files, code blocks, images, and tool outputs as linked blobs or derived records where available.
6. Chunk large conversations after raw custody and document normalization.
7. Do not treat model responses as verified truth; they are conversation records.

## Normalized conversation document

Each chat thread should become a document-like record with:

- provider,
- export source profile,
- conversation ID,
- title,
- created/updated timestamps where available,
- participant roles,
- message count,
- token or character count where computed,
- attachment refs,
- source alias refs,
- raw evidence refs,
- normalized text derivative refs,
- chunk refs,
- redaction status,
- search/index status.

## Output derivatives

First-pass derivatives:

- Markdown document per conversation,
- JSON document record per conversation,
- JSONL message stream per conversation,
- optional PDF/HTML render later,
- chunk manifests for search/vector pipelines.

## New chat integration

The goal is not only archival. Exodus should prepare conversations for reuse in open chat/workspace surfaces.

New chat integration should support:

- importing old conversations as read-only documents,
- citing old conversation chunks in new chats,
- linking attachments and generated artifacts,
- preserving provenance and source-provider context,
- marking migrated assistant outputs as historical records, not current model claims.

## Dashboard behavior

Exodus Dashboard should show:

- chat export archives landed,
- conversations discovered,
- conversations normalized,
- attachments preserved,
- large conversations chunked,
- blocked or malformed conversations,
- conversations ready for search,
- conversations ready for document export,
- conversations available to new chat/workspace integration.

## Privacy and redaction

AI chat exports may include secrets, credentials, personal records, legal/medical/financial details, and third-party information.

Default posture:

- preserve raw privately,
- do not publish by default,
- run optional secret/PII scans before proof-pack export,
- support redacted derivative documents,
- preserve the relationship between redacted derivatives and raw originals.

## Non-goals

- no provider account merge claim,
- no claim that imported chats recreate native provider history,
- no silent publication of private conversations,
- no treating model outputs as authoritative facts,
- no flattening attachments or generated files into untraceable text.

## Later provider candidates

Later candidates may include Gemini, Copilot, Perplexity, Poe, local assistant logs, IDE assistant chats, support bots, and enterprise assistant exports after current export paths are verified.
