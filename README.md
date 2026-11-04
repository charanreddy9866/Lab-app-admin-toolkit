# Lab & Enterprise Application Admin Toolkit

Small, practical tools and templates for supporting lab and business applications
in a regulated (GxP) environment: the day-to-day work of an application administrator.

| Task | Tool | What it does |
|---|---|---|
| Incident troubleshooting | `health_check.py` | Disk space, DB/server port reachability and data-share write test on an instrument PC or app server. JSON report to attach to the ticket. |
| User access reviews | `access_review.py` | Compares app accounts to the staff roster; flags terminated, inactive, shared and wrong-role accounts. Output is a review sheet, not automatic changes. |
| Data integrity | `integrity_check.py` + `sql/data_integrity_checks.sql` | SQL checks for duplicates, orphan records, missing owner/instrument (ALCOA+ "Attributable") and gaps in the audit trail. |
| Patch testing | `patch_validation.py` | Baseline before a patch (OS / SQL driver), verify after, saves JSON evidence for the change record. |
| Knowledge management | `docs/` | Runbook (instrument software cannot save data) and a GxP-aware change record template. |

## Quick start (Python 3.9+, standard library only)
```bash
python access_review.py --accounts sample_data/accounts.csv --roster sample_data/hr_roster.csv --as-of 2026-11-04
python integrity_check.py --build-demo
python patch_validation.py baseline --db demo.db --share ./data_share
python patch_validation.py verify   --db demo.db --share ./data_share
python health_check.py --config sample_data/hosts.json
```

## Design principles
- **Process over shortcuts:** tools produce evidence and recommendations; changes still go through approval and change control.
- **Data integrity first:** checks map to ALCOA+ and 21 CFR Part 11 ideas (attributable records, intact audit trails, no shared logins).
- **Portable SQL:** queries are standard SQL with notes for SQL Server and Oracle.
- **Documentation is part of the fix:** every runbook ends with "update the knowledge base."

Sample data is fictional.
