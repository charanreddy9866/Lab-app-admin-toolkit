"""Runs the SQL data-integrity checks in sql/data_integrity_checks.sql.

Uses SQLite so it runs anywhere for a demo; the same queries are standard SQL
and port to SQL Server or Oracle with minor syntax changes (see comments in
the .sql file). Each check returns the offending rows; zero rows = pass.

Usage:
    python integrity_check.py --build-demo   # creates demo.db with sample issues
    python integrity_check.py --db demo.db
"""
import argparse
import sqlite3

DEMO = """
DROP TABLE IF EXISTS samples; DROP TABLE IF EXISTS results; DROP TABLE IF EXISTS audit_log;
CREATE TABLE samples (sample_id TEXT PRIMARY KEY, experiment_no TEXT, instrument_id TEXT, created_by TEXT, created_at TEXT);
CREATE TABLE results (result_id INTEGER PRIMARY KEY, sample_id TEXT, measurement REAL, recorded_by TEXT, recorded_at TEXT);
CREATE TABLE audit_log (log_id INTEGER PRIMARY KEY, record_id TEXT, action TEXT, username TEXT, logged_at TEXT);
INSERT INTO samples VALUES
 ('S-001','EXP-100','VICELL-01','jdoe','2026-10-01 09:00'),
 ('S-002','EXP-100','VICELL-01','jdoe','2026-10-01 09:05'),
 ('S-003','EXP-101',NULL,'asmith','2026-10-02 10:00'),
 ('S-004','EXP-102','IMGLAB-02',NULL,'2026-10-02 11:00');
INSERT INTO results (sample_id, measurement, recorded_by, recorded_at) VALUES
 ('S-001', 1.25, 'jdoe', '2026-10-01 09:30'),
 ('S-001', 1.25, 'jdoe', '2026-10-01 09:30'),
 ('S-002', 0.98, 'jdoe', '2026-10-01 09:40'),
 ('S-999', 2.10, 'asmith', '2026-10-02 10:30');
INSERT INTO audit_log (record_id, action, username, logged_at) VALUES
 ('S-001','CREATE','jdoe','2026-10-01 09:00'),
 ('S-002','CREATE','jdoe','2026-10-01 09:05'),
 ('S-003','CREATE','asmith','2026-10-02 10:00');
"""


def load_checks(path):
    checks, name, lines = [], None, []
    for line in open(path):
        if line.startswith("-- CHECK:"):
            if name:
                checks.append((name, "".join(lines)))
            name, lines = line.split(":", 1)[1].strip(), []
        elif name:
            lines.append(line)
    if name:
        checks.append((name, "".join(lines)))
    return checks


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--db", default="demo.db")
    p.add_argument("--sql", default="sql/data_integrity_checks.sql")
    p.add_argument("--build-demo", action="store_true")
    a = p.parse_args()
    con = sqlite3.connect(a.db)
    if a.build_demo:
        con.executescript(DEMO)
        print(f"Demo database written to {a.db}")
    failed = 0
    for name, query in load_checks(a.sql):
        rows = con.execute(query).fetchall()
        status = "PASS" if not rows else f"FAIL ({len(rows)} row(s))"
        failed += bool(rows)
        print(f"[{status}] {name}")
        for r in rows:
            print(f"      {r}")
    print(f"\n{failed} check(s) need review.")
