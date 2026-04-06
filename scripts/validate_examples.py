#!/usr/bin/env python3
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
for path in sorted((root / "examples").rglob("*.json")):
    with path.open("r", encoding="utf-8") as f:
        json.load(f)
print("validated example JSON")
