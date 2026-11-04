"""User access review.

Compares application accounts against the current staff roster and flags:
  - TERMINATED   : account still active for someone not on the roster
  - INACTIVE     : no login in the last N days
  - SHARED       : generic/shared account names (not allowed under 21 CFR Part 11)
  - ROLE_MISMATCH: application role not approved for the person's job title

Every flag is a recommendation for review, not an automatic change: access
changes still go through the normal approval and change process.

Usage:
    python access_review.py --accounts sample_data/accounts.csv \
        --roster sample_data/hr_roster.csv --inactive-days 90
"""
import argparse
import csv
from datetime import date, datetime

SHARED_HINTS = ("lab", "shared", "generic", "test", "admin", "temp")
APPROVED_ROLES = {
    "Scientist": {"Analyst", "Reviewer"},
    "Senior Scientist": {"Analyst", "Reviewer", "Approver"},
    "Lab Technician": {"Analyst"},
    "QA Specialist": {"Reviewer", "Approver"},
}


def load(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def review(accounts, roster, inactive_days, today):
    staff = {r["username"]: r for r in roster}
    findings = []
    for acct in accounts:
        if acct["status"] != "Active":
            continue
        user = acct["username"]
        last = datetime.strptime(acct["last_login"], "%Y-%m-%d").date()
        if any(h in user.lower() for h in SHARED_HINTS) and user not in staff:
            findings.append((user, "SHARED", "Generic account; needs an individual owner or removal"))
            continue
        if user not in staff:
            findings.append((user, "TERMINATED", "Active account but not on current roster"))
            continue
        if (today - last).days > inactive_days:
            findings.append((user, "INACTIVE", f"No login for {(today - last).days} days"))
        allowed = APPROVED_ROLES.get(staff[user]["job_title"], set())
        if acct["app_role"] not in allowed:
            findings.append((user, "ROLE_MISMATCH",
                             f"{acct['app_role']} not approved for {staff[user]['job_title']}"))
    return findings


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="User access review")
    p.add_argument("--accounts", required=True)
    p.add_argument("--roster", required=True)
    p.add_argument("--inactive-days", type=int, default=90)
    p.add_argument("--as-of", help="YYYY-MM-DD (default: today)")
    p.add_argument("--out", default="access_review_findings.csv")
    a = p.parse_args()
    today = datetime.strptime(a.as_of, "%Y-%m-%d").date() if a.as_of else date.today()
    findings = review(load(a.accounts), load(a.roster), a.inactive_days, today)
    with open(a.out, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["username", "finding", "detail", "reviewed_by", "action_taken"])
        for row in findings:
            w.writerow([*row, "", ""])
    print(f"{len(findings)} finding(s) written to {a.out}")
    for u, kind, detail in findings:
        print(f"  {kind:<13} {u:<14} {detail}")
