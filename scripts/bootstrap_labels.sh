#!/usr/bin/env bash
set -euo pipefail
REPO="${1:-SocioProphet/exodus}"
labels=(
  "phase:0:Scope and controls"
  "phase:1:Crawl and topology"
  "phase:2:Planning and budget"
  "phase:3:Intake and preservation"
  "phase:4:Processing and normalization"
  "phase:5:Dashboard and guidance"
  "area:contracts"
  "area:scoring"
  "area:adapters"
  "area:console"
  "area:docs"
  "area:infra"
  "priority:P0"
  "priority:P1"
  "priority:P2"
)
for label in "${labels[@]}"; do
  gh label create "$label" --repo "$REPO" --force || true
done
