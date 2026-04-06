# Repo bootstrap

Canonical destination: `SocioProphet/exodus`

This scaffold is publish-ready. The connected GitHub tooling available during generation could inspect installations and repositories, but did not expose a repository-creation action. Because of that, publication is handled through the `gh` CLI script in `scripts/publish_to_github.sh`.

## Publish sequence

```bash
cd exodus_repo_scaffold_v0_4 && python3 scripts/validate_examples.py && ./scripts/publish_to_github.sh SocioProphet exodus public
```

## Post-publish bootstrap

```bash
./scripts/bootstrap_labels.sh SocioProphet/exodus && ./scripts/bootstrap_issues.sh SocioProphet/exodus
```

## Existing lineage note

A separate public repository named `SociOS-Linux/EXODUS` exists and should be treated as separate lineage unless explicitly chosen otherwise.
