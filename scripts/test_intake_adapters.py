#!/usr/bin/env python3
"""Tests for the account registry (CHK-09 backing) and the BSM adapter (AC-09).

Run: python3 scripts/test_intake_adapters.py  (dependency-free)
"""
from __future__ import annotations

from pathlib import Path

from account_registry import is_registered, load_registry, registered_accounts
from bsm_intake import build_audit_enrichment, parse_praudit_xml

ROOT = Path(__file__).resolve().parents[1]


def test_account_registry_active_only() -> None:
    reg = load_registry()  # default examples/account-registry.json
    accts = registered_accounts(reg)
    assert "operator@example.org" in accts
    assert is_registered(reg, "owner.personal@example.com")
    assert not is_registered(reg, "stranger@example.com")


def test_account_registry_excludes_revoked() -> None:
    reg = {"registry_version": 1, "accounts": [
        {"account": "a@x", "platform": "Other", "owner": "o", "status": "active"},
        {"account": "b@x", "platform": "Other", "owner": "o", "status": "revoked"},
    ]}
    assert is_registered(reg, "a@x") and not is_registered(reg, "b@x")


def test_bsm_parses_records_and_paths() -> None:
    xml = (ROOT / "tests/bsm-fixtures/sample.praudit.xml").read_text()
    recs = parse_praudit_xml(xml)
    assert len(recs) == 3
    e = build_audit_enrichment(recs)
    assert e["record_count"] == 3
    # file access timeline picks up the mail path
    paths = [a["path"] for a in e["file_access_timeline"]]
    assert "/Users/synthetic/Library/Mail/synthetic.eml" in paths
    # timeline is time-ordered
    times = [a["time_micros"] for a in e["file_access_timeline"]]
    assert times == sorted(times)


def test_bsm_detects_privilege_escalation() -> None:
    recs = parse_praudit_xml((ROOT / "tests/bsm-fixtures/sample.praudit.xml").read_text())
    e = build_audit_enrichment(recs)
    events = {p["event"] for p in e["privilege_escalation"]}
    # setuid is an identity-changing syscall; execve with uid=0/ruid=501 is effective-root.
    assert "setuid(2)" in events
    assert any("execve" in ev for ev in events)
    # the benign open() is NOT flagged
    assert not any("open" in ev for ev in events)


def test_bsm_time_micros() -> None:
    recs = parse_praudit_xml((ROOT / "tests/bsm-fixtures/sample.praudit.xml").read_text())
    # 1751025600 s + 120 ms -> micros
    assert recs[0]["time_micros"] == 1751025600 * 1_000_000 + 120 * 1_000


def main() -> None:
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    for t in tests:
        t()
    print(f"OK: account-registry + BSM adapter — {len(tests)} tests passed")


if __name__ == "__main__":
    main()
