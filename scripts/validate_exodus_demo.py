#!/usr/bin/env python3
"""Validate the synthetic Exodus Migration Workroom demo fixture.

This validator is intentionally offline. It does not require live provider
credentials, does not contact Apple/Google/Microsoft, and does not perform any
destructive or provider-side actions.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "schemas" / "exodus-run.v0.schema.json"
FIXTURE = ROOT / "examples" / "synthetic-tenant-a" / "exodus-run.json"


def load(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path} root must be object")
    return data


def validate_schema(schema: dict[str, Any], fixture: dict[str, Any]) -> str:
    try:
        import jsonschema  # type: ignore
    except Exception:
        return "skipped_jsonschema_unavailable"
    jsonschema.Draft202012Validator(schema).validate(fixture)
    return "valid"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def validate_refs(fixture: dict[str, Any]) -> dict[str, Any]:
    providers = {p["provider_id"] for p in fixture["providers"]}
    accounts = {a["account_id"] for a in fixture["accounts"]}
    evidence = {e["evidence_id"] for e in fixture["export_ledger"]}
    blockers = {b["blocker_id"] for b in fixture["blockers"]}
    recommendations = {r["recommendation_id"] for r in fixture["recommendations"]}
    waves = {w["wave_id"] for w in fixture["phase_2_budget_proposal"]["waves"]}

    require(fixture["demo_boundary"]["synthetic"] is True, "fixture must be synthetic")
    require(fixture["demo_boundary"]["live_credentials_required"] is False, "live credentials must not be required")
    require(fixture["demo_boundary"]["destructive_actions_allowed"] is False, "destructive actions must not be allowed")
    require(fixture["demo_boundary"]["provider_side_writes_allowed"] is False, "provider-side writes must not be allowed")

    expected_providers = {"provider.apple", "provider.google", "provider.microsoft"}
    require(expected_providers.issubset(providers), f"missing expected providers: {sorted(expected_providers - providers)}")

    for account in fixture["accounts"]:
        require(account["provider_ref"] in providers, f"account {account['account_id']} has unknown provider_ref")
    for item in fixture["asset_census"]:
        require(item["provider_ref"] in providers, f"asset {item['asset_collection_id']} has unknown provider_ref")
    for item in fixture["export_ledger"]:
        require(item["provider_ref"] in providers, f"evidence {item['evidence_id']} has unknown provider_ref")
        require(item["validation_status"] == "synthetic_verified", f"evidence {item['evidence_id']} must be synthetic_verified")
    for score in fixture["scores"]["pcs_by_provider"]:
        require(score["provider_ref"] in providers, f"provider score has unknown provider_ref {score['provider_ref']}")
        for ref in score["evidence_refs"]:
            require(ref in evidence, f"provider score {score['provider_ref']} references unknown evidence {ref}")
    for ref in fixture["scores"]["eri"]["evidence_refs"]:
        require(ref in evidence, f"ERI references unknown evidence {ref}")
    for blocker in fixture["blockers"]:
        require(blocker["provider_ref"] in providers, f"blocker {blocker['blocker_id']} has unknown provider_ref")
        for ref in blocker["evidence_refs"]:
            require(ref in evidence, f"blocker {blocker['blocker_id']} references unknown evidence {ref}")
    for rec in fixture["recommendations"]:
        for dep in rec["depends_on"]:
            require(dep in recommendations, f"recommendation {rec['recommendation_id']} depends on unknown recommendation {dep}")
        for ref in rec["evidence_refs"]:
            require(ref in evidence, f"recommendation {rec['recommendation_id']} references unknown evidence {ref}")
    for wave in fixture["phase_2_budget_proposal"]["waves"]:
        for provider in wave["provider_refs"]:
            require(provider in providers, f"wave {wave['wave_id']} references unknown provider {provider}")
        for dep in wave["depends_on"]:
            require(dep in waves, f"wave {wave['wave_id']} depends on unknown wave {dep}")
    for ref in fixture["phase_2_budget_proposal"]["evidence_refs"]:
        require(ref in evidence, f"budget proposal references unknown evidence {ref}")

    return {
        "provider_count": len(providers),
        "account_count": len(accounts),
        "asset_collection_count": len(fixture["asset_census"]),
        "evidence_count": len(evidence),
        "blocker_count": len(blockers),
        "recommendation_count": len(recommendations),
        "budget_wave_count": len(waves),
    }


def main() -> int:
    try:
        schema = load(SCHEMA)
        fixture = load(FIXTURE)
        schema_status = validate_schema(schema, fixture)
        counts = validate_refs(fixture)
    except Exception as exc:
        print(f"ERR: {exc}", file=sys.stderr)
        return 2

    report = {
        "schema_version": "exodus.synthetic-workroom-demo.validation.v0",
        "fixture": "examples/synthetic-tenant-a/exodus-run.json",
        "schema": "schemas/exodus-run.v0.schema.json",
        "schema_validation": schema_status,
        "cross_reference_validation": "valid",
        "demo_boundary": "synthetic_offline_no_provider_credentials_no_destructive_actions",
        **counts,
        "validation_status": "valid"
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
