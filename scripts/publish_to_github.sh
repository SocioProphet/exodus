#!/usr/bin/env bash
set -euo pipefail

ORG="${1:-SocioProphet}"
REPO="${2:-exodus}"
VISIBILITY="${3:-public}"
DESCRIPTION="Exodus: governed migration, evidence, and progress tracking out of Apple, Google, Microsoft, and other control surfaces."

if ! command -v gh >/dev/null 2>&1; then
  echo "gh CLI is required." >&2
  exit 1
fi

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if [ ! -d .git ]; then
  git init
fi

git add .
git commit -m "initialize Exodus scaffold" || true

if ! gh repo view "$ORG/$REPO" >/dev/null 2>&1; then
  gh repo create "$ORG/$REPO" --"$VISIBILITY" --source=. --remote=origin --description "$DESCRIPTION" --push
else
  git remote remove origin >/dev/null 2>&1 || true
  git remote add origin "https://github.com/$ORG/$REPO.git"
  git push -u origin HEAD
fi
