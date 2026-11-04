"""Instrument PC / application server health check.

Checks the things that most often break data capture on a lab or business
application host: free disk space, reachability of the data server/database
port, and whether the data share path is writable. Writes a JSON report that
can be attached to a ticket.

Usage:
    python health_check.py --config sample_data/hosts.json
"""
import argparse
import json
import os
import shutil
import socket
import tempfile
from datetime import datetime, timezone


def check_disk(path, min_free_pct):
    usage = shutil.disk_usage(path)
    free_pct = round(usage.free / usage.total * 100, 1)
    return {"check": "disk_space", "path": path, "free_pct": free_pct,
            "status": "OK" if free_pct >= min_free_pct else "FAIL"}


def check_port(host, port, timeout=3):
    try:
        with socket.create_connection((host, port), timeout=timeout):
            status = "OK"
    except OSError as exc:
        status = f"FAIL ({exc.__class__.__name__})"
    return {"check": "port_reachable", "target": f"{host}:{port}", "status": status}


def check_share_writable(path):
    try:
        os.makedirs(path, exist_ok=True)
        with tempfile.NamedTemporaryFile(dir=path, delete=True) as f:
            f.write(b"health-check")
        status = "OK"
    except OSError as exc:
        status = f"FAIL ({exc.__class__.__name__})"
    return {"check": "share_writable", "path": path, "status": status}


def run(config):
    results = []
    for disk in config.get("disks", []):
        results.append(check_disk(disk["path"], disk.get("min_free_pct", 15)))
    for target in config.get("ports", []):
        results.append(check_port(target["host"], target["port"]))
    for share in config.get("shares", []):
        results.append(check_share_writable(share))
    return {
        "host": socket.gethostname(),
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "overall": "OK" if all(r["status"] == "OK" for r in results) else "ATTENTION",
        "results": results,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--config", required=True)
    parser.add_argument("--out", default="health_report.json")
    args = parser.parse_args()
    with open(args.config) as f:
        report = run(json.load(f))
    with open(args.out, "w") as f:
        json.dump(report, f, indent=2)
    print(f"Overall: {report['overall']}")
    for r in report["results"]:
        print(f"  [{r['status']}] {r['check']}: {r.get('path') or r.get('target')}")
