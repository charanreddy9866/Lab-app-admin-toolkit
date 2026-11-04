# Runbook: Instrument software cannot save data

**Applies to:** instrument PCs running vendor acquisition software
**Priority:** High if a run is in progress (data at risk)

## 1. Gather facts (before touching anything)
- Instrument ID, PC hostname, application and version
- Exact error message (screenshot)
- When it started; does it affect other users or instruments?
- Is a run in progress? **If yes, do not reboot.** Escalate per data-integrity procedure.

## 2. Check the basics
| Check | How | Tool |
|---|---|---|
| Disk space | Free space > 15% | `python health_check.py` |
| Data share reachable/writable | Can the PC write to the share? | `health_check.py` |
| Database reachable | Port open to DB server | `health_check.py` |
| Acquisition service running | services.msc / `systemctl status` | OS |
| User account | Locked, expired password, lost drive mapping | AD / app admin |
| Recent changes | Patches, config changes in last 7 days | Change records |

## 3. Logs
- Application log (vendor path)
- Windows Event Viewer → Application and System
- Linux: `journalctl -u <service>`

## 4. Fix
- Approved, documented fixes only (e.g., restart service per SOP, remap share).
- Anything that changes a validated system → **change control**, not an on-the-spot fix.

## 5. Verify and close
- User saves a test record successfully.
- Document root cause and fix in the ticket and update this runbook.
- If run data was affected, notify the system owner / QA.
