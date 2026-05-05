# Provider Coverage Roadmap

## Status

Backlog for world-class Exodus provider coverage.

## Purpose

Exodus should become the open migration, evidence, and sovereignty layer for every major closed or semi-closed user data surface. Provider coverage should expand in waves, but the architecture must assume that all providers are eventual ingress surfaces.

The rule remains stable:

- source systems are ingress only,
- raw custody happens before parsing or conversion,
- provider IDs and paths are source aliases,
- user attestation and policy gates are evidence records,
- normalization produces open derived records,
- proof packs show what was captured, converted, blocked, or left behind.

## Coverage waves

### Wave 0: Core personal cloud exits

- Apple iCloud Drive
- Apple iCloud Photos
- Apple Notes / iCloud Notes
- Apple Mail / iCloud Mail
- Apple Music local library / iTunes library exports
- Google Drive
- Google Photos
- Google Keep
- Gmail / Google Takeout Mail
- Google Calendar and Contacts
- Microsoft OneDrive
- Microsoft Outlook / Exchange / Microsoft 365 Mail
- Microsoft OneNote
- Microsoft Teams export surfaces where available

### Wave 1: AI chat and assistant exports

- ChatGPT / OpenAI
- Claude / Anthropic
- Gemini / Google
- Copilot / Microsoft
- Perplexity
- Poe
- Mistral Le Chat
- xAI Grok
- Meta AI exports where available
- local assistant logs
- Ollama / LM Studio / local inference chat logs
- IDE assistant logs from Cursor, Windsurf, Copilot Chat, Continue, and similar tools
- enterprise support-bot exports where users/admins are authorized

### Wave 2: Email, calendar, contacts, and identity-adjacent data

- generic IMAP
- generic SMTP archive exports
- MBOX
- Maildir
- EML folders
- Proton Mail exports where available
- Fastmail exports
- Yahoo Mail exports
- Zoho Mail exports
- Exchange archives
- CardDAV contacts
- CalDAV calendars
- ICS calendar exports
- vCard contact exports

### Wave 3: Notes, documents, knowledge bases, and writing systems

- Notion
- Evernote
- Obsidian vaults
- Joplin
- Standard Notes
- Apple Pages / Numbers / Keynote exports
- Microsoft Word / Excel / PowerPoint documents
- Google Docs / Sheets / Slides exports
- Dropbox Paper
- Box Notes
- Confluence
- Coda
- Quip
- Markdown folders
- local wiki exports

### Wave 4: Messaging, collaboration, and social workspaces

- Slack
- Discord
- Microsoft Teams
- Matrix
- Telegram export archives
- Signal local export paths where available and authorized
- WhatsApp export archives
- iMessage local export paths where available and authorized
- Google Chat
- Zoom chat/transcripts/cloud recordings where exportable
- Mattermost
- Zulip

### Wave 5: Media libraries and creative assets

- local music libraries
- local video libraries
- Apple Photos libraries
- Google Photos exports
- Adobe Lightroom exports
- Adobe Creative Cloud files where exportable
- DaVinci Resolve projects
- Final Cut Pro projects
- Logic Pro projects
- GarageBand projects
- Audacity projects
- camera SD card exports
- podcast project folders
- Plex / Jellyfin metadata and libraries

### Wave 6: Developer and technical work history

- GitHub repositories, issues, PRs, discussions, releases, actions artifacts
- GitLab projects
- Bitbucket projects
- Jira projects
- Linear issues
- Azure DevOps projects
- CI/CD logs
- local shell histories where user-authorized
- terminal transcripts
- browser console captures
- device console captures
- package registry metadata
- container image manifests

### Wave 7: Financial, legal, medical, and administrative archives

- bank statement exports
- brokerage statement exports
- tax archives
- invoices and receipts
- legal document folders
- medical record exports where user-authorized
- insurance documents
- government portal exports
- signed PDFs
- scanned archives

These surfaces require stronger redaction, local-only defaults, and proof-pack controls.

### Wave 8: Social media and creator platforms

- X/Twitter data archive
- Facebook data archive
- Instagram data archive
- TikTok data archive
- YouTube Studio exports
- Substack exports
- Medium exports
- Patreon creator/member exports where available
- Mastodon export archives
- Bluesky export paths where available

## Cross-cutting provider object types

Every provider should be mapped into these canonical migration object families:

- SourceProfile
- MigrationWavePlan
- EvidenceDashboardState
- ProofPackSummary
- SourceAliasReport
- BlockedObjectReport
- ConversionProfile
- ConversionReceipt
- AttestationRecord
- RedactionReviewRecord
- DeletionEligibilityRecord
- ProviderDowngradePlan

## Missing contract families

The current PR has strong starts for dashboard, migration wave, proof pack, notes, owned media, playlist, and AI chat exports. The next missing contract families are:

- EmailSourceProfile
- CalendarSourceProfile
- ContactSourceProfile
- MessageThreadDocument
- ChatConversationReusePolicy
- RedactionReviewRecord
- SourceAliasReport
- BlockedObjectReport
- ConversionReceipt
- ProviderTopologySnapshot
- ProviderControlSurfaceReport
- DeletionEligibilityRecord
- ProviderDowngradePlan

## Provider onboarding checklist

For each new provider, Exodus should capture:

1. source account or export method,
2. export artifact format,
3. raw custody path,
4. expected metadata,
5. attachment/media handling,
6. redaction risk,
7. conversion targets,
8. blocked states,
9. proof-pack outputs,
10. provider downgrade or deletion eligibility gates.

## Acceptance rule

A provider is not considered covered until Exodus can:

- preserve raw source artifacts,
- enumerate source aliases,
- normalize at least one useful derived record,
- report blocked objects,
- emit dashboard state,
- emit proof-pack summary,
- and explain whether provider downgrade/deletion is safe, blocked, or unknown.
