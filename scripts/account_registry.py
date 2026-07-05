#!/usr/bin/env python3
"""Exodus account registry loader — backs CHK-09 (SourceAccountRegistered).

An artifact may only enter intake if its source_account is registered and
active. This loader turns examples/account-registry.json into the set the gate
engine's CHK-09 consults.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

DEFAULT_REGISTRY = Path(__file__).resolve().parents[1] / "examples/account-registry.json"


def load_registry(path: str | Path | None = None) -> dict[str, Any]:
    return json.loads(Path(path or DEFAULT_REGISTRY).read_text(encoding="utf-8"))


def registered_accounts(registry: dict[str, Any]) -> set[str]:
    """Accounts that are present AND active."""
    return {a["account"] for a in registry.get("accounts", []) if a.get("status") == "active"}


def is_registered(registry: dict[str, Any], account: str | None) -> bool:
    return account in registered_accounts(registry)


if __name__ == "__main__":
    import sys

    reg = load_registry(sys.argv[1] if len(sys.argv) > 1 else None)
    print(json.dumps(sorted(registered_accounts(reg)), indent=2))
