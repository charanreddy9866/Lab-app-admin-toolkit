"""Patch validation: capture a baseline before a patch, re-run after, compare.

Typical use for an OS or SQL-driver patch on an application server:
    python patch_validation.py baseline --db demo.db --share ./data_share
    ...apply patch in the TEST environment...
    python patch_validation.py verify   --db demo.db --share ./data_share

Checks: database connects, key queries return the same row counts, the data
share is writable. Results are saved as JSON evidence for the change record.
"""
import argparse
import json
import os
import sqlite3
import tempfile
import time
from datetime import datetime, timezone

KEY_QUERIES = {
    "sample_count": "SELECT COUNT(*) FROM samples",
    "result_count": "SELECT COUNT(*) FROM results",
    "audit_count": "SELECT COUNT(*) FROM audit_log",
}


def collect(db, share):
    out = {"captured_at": datetime.now(timezone.utc).isoformat(), "checks": {}}
    try:
        start = time.perf_counter()
        con = sqlite3.connect(db)
        for name, q in KEY_QUERIES.items():
            out["checks"][name] = con.execute(q).fetchone()[0]
        out["checks"]["db_connect"] = "OK"
        out["checks"]["query_ms"] = round((time.perf_counter() - start) * 1000, 1)
    except sqlite3.Error as exc:
        out["checks"]["db_connect"] = f"FAIL: {exc}"
    try:
        os.makedirs(share, exist_ok=True)
        with tempfile.NamedTemporaryFile(dir=share):
            pass
        out["checks"]["share_writable"] = "OK"
    except OSError as exc:
        out["checks"]["share_writable"] = f"FAIL: {exc}"
    return out


def compare(base, now):
    issues = []
    for key in ("db_connect", "share_writable", *KEY_QUERIES):
        if base["checks"].get(key) != now["checks"].get(key):
            issues.append(f"{key}: before={base['checks'].get(key)} after={now['checks'].get(key)}")
    b, a = base["checks"].get("query_ms", 0), now["checks"].get("query_ms", 0)
    if b and a > b * 2:
        issues.append(f"query_ms more than doubled: {b} -> {a}")
    return issues


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("mode", choices=["baseline", "verify"])
    p.add_argument("--db", required=True)
    p.add_argument("--share", required=True)
    p.add_argument("--baseline-file", default="patch_baseline.json")
    a = p.parse_args()
    snap = collect(a.db, a.share)
    if a.mode == "baseline":
        json.dump(snap, open(a.baseline_file, "w"), indent=2)
        print(f"Baseline saved to {a.baseline_file}: {snap['checks']}")
    else:
        issues = compare(json.load(open(a.baseline_file)), snap)
        evidence = {"verified": snap, "issues": issues, "result": "PASS" if not issues else "FAIL"}
        json.dump(evidence, open("patch_verification.json", "w"), indent=2)
        print(f"Result: {evidence['result']}")
        for i in issues:
            print("  -", i)
        print("Evidence saved to patch_verification.json (attach to the change record).")
