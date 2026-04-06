#!/usr/bin/env bash
set -euo pipefail
REPO="${1:-SocioProphet/exodus}"

gh issue create --repo "$REPO" --title "Freeze canonical domain model and contracts" --body "Implement packages/contracts using the v0.4 schemas and synthetic tenant fixtures. Ensure one vocabulary across docs, schemas, and package READMEs." --label "phase:0:Scope and controls,area:contracts,priority:P0"

gh issue create --repo "$REPO" --title "Implement ERI, PCS, and score explanations" --body "Create packages/scoring with executable logic for ERI, PCS, score explanations, archive progress, open conversion progress, and cutover progress." --label "phase:0:Scope and controls,area:scoring,priority:P0"

gh issue create --repo "$REPO" --title "Build Phase 1 synthetic tenant validation harness" --body "Validate provider topology snapshot, asset census, dependency graph, size/temperature profile, exportability report, budget proposal, recommendation, and verification result examples against schemas." --label "phase:1:Crawl and topology,area:contracts,priority:P0"

gh issue create --repo "$REPO" --title "Define Exodus Dashboard MVP information architecture" --body "Implement apps/console information architecture for Overview, Providers, Accounts, Domains, Asset Collections, Export Ledger, Blockers, Recommendations, Evidence, and Score Explanations." --label "phase:5:Dashboard and guidance,area:console,priority:P1"
