#!/usr/bin/env python3
"""BSM audit-trail adapter (artifact class AC-09, GAP-10).

The macOS BSM audit trail (/var/audit) is the highest-value uninspected primary
source. The binary format is read with `praudit`; this adapter parses
`praudit -xn` XML into Examination-zone enrichments: a syscall sequence, a
uid/pid map, a file-access timeline, and a privilege-escalation flag list.

This closes the *implementation* gap (a tested parser exists). Operational
ingestion — running `praudit` against the target Mac's /var/audit — remains an
ops step (`ingest_bsm_file`). Pure XML parsing is used for tests so no real
audit data or `praudit` binary is required to validate the logic.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

# events that change effective identity — primary privilege-escalation signals.
_PRIV_EVENTS = ("setuid", "seteuid", "setgid", "setegid", "setreuid", "setregid", "su(", "sudo")


def _time_micros(rec: ET.Element) -> int | None:
    t = rec.get("time")
    if t is None:
        return None
    try:
        epoch = int(t)  # numeric epoch seconds (deterministic fixtures)
    except ValueError:
        try:
            epoch = int(dt.datetime.strptime(t, "%a %b %d %H:%M:%S %Y").replace(tzinfo=dt.timezone.utc).timestamp())
        except ValueError:
            return None
    msec = rec.get("msec", "0")
    try:
        msec_int = int(str(msec).strip().lstrip("+").replace("msec", "").strip() or "0")
    except ValueError:
        msec_int = 0
    return epoch * 1_000_000 + msec_int * 1_000


def parse_praudit_xml(xml_text: str) -> list[dict[str, Any]]:
    """Parse praudit -xn XML into structured records. Tolerates a stream of
    <record> elements with or without a single root wrapper."""
    wrapped = f"<audit>{xml_text}</audit>" if "<audit" not in xml_text.split(">", 1)[0] else xml_text
    root = ET.fromstring(wrapped)
    records: list[dict[str, Any]] = []
    for rec in root.iter("record"):
        subject = rec.find("subject")
        ret = rec.find("return")
        records.append({
            "event": rec.get("event", ""),
            "time_micros": _time_micros(rec),
            "subject": dict(subject.attrib) if subject is not None else {},
            "paths": [p.text for p in rec.findall("path") if p.text],
            "return_errval": (ret.get("errval") if ret is not None else None),
            "return_retval": (ret.get("retval") if ret is not None else None),
        })
    return records


def build_audit_enrichment(records: list[dict[str, Any]]) -> dict[str, Any]:
    syscall_sequence = []
    uid_pid_map: dict[str, set[str]] = {}
    file_access_timeline = []
    privilege_escalation = []

    for idx, r in enumerate(records):
        subj = r["subject"]
        pid, uid, ruid = subj.get("pid"), subj.get("uid"), subj.get("ruid")
        syscall_sequence.append({
            "idx": idx, "event": r["event"], "time_micros": r["time_micros"],
            "pid": pid, "uid": uid, "return": r["return_errval"],
        })
        if pid is not None:
            uid_pid_map.setdefault(pid, set())
            if uid is not None:
                uid_pid_map[pid].add(uid)
        for p in r["paths"]:
            file_access_timeline.append({"time_micros": r["time_micros"], "event": r["event"], "path": p})

        ev = r["event"].lower()
        effective_root = uid == "0" and ruid not in (None, "0")
        if any(tok in ev for tok in _PRIV_EVENTS) or effective_root:
            privilege_escalation.append({
                "idx": idx, "event": r["event"], "pid": pid, "uid": uid, "ruid": ruid,
                "reason": "identity-changing syscall" if any(t in ev for t in _PRIV_EVENTS) else "effective uid 0 with non-root ruid",
            })

    return {
        "artifact_class": "AuditRecord",
        "record_count": len(records),
        "syscall_sequence": syscall_sequence,
        "uid_pid_map": {pid: sorted(uids) for pid, uids in uid_pid_map.items()},
        "file_access_timeline": sorted(file_access_timeline, key=lambda e: (e["time_micros"] or 0)),
        "privilege_escalation": privilege_escalation,
    }


def ingest_bsm_file(path: str | Path) -> dict[str, Any]:
    """Operational path: shell to `praudit -xn` against a real /var/audit file."""
    out = subprocess.run(["praudit", "-xn", str(path)], capture_output=True, text=True, check=True).stdout
    return build_audit_enrichment(parse_praudit_xml(out))


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Parse a BSM audit trail (praudit -xn XML) into enrichments.")
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--xml", help="path to praudit -xn XML output")
    g.add_argument("--bsm", help="path to a raw /var/audit BSM file (requires praudit)")
    args = p.parse_args(argv if argv is not None else sys.argv[1:])
    if args.bsm:
        enrichment = ingest_bsm_file(args.bsm)
    else:
        enrichment = build_audit_enrichment(parse_praudit_xml(Path(args.xml).read_text(encoding="utf-8")))
    print(json.dumps(enrichment, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
