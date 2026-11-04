-- Data-integrity checks for a lab/business application database.
-- Each check returns offending rows; zero rows = pass.
-- Written in standard SQL. SQL Server / Oracle notes inline.

-- CHECK: Duplicate results (same sample, value, user and timestamp)
SELECT sample_id, measurement, recorded_by, recorded_at, COUNT(*) AS copies
FROM results
GROUP BY sample_id, measurement, recorded_by, recorded_at
HAVING COUNT(*) > 1;

-- CHECK: Orphan results (result points to a sample that does not exist)
SELECT r.result_id, r.sample_id
FROM results r
LEFT JOIN samples s ON s.sample_id = r.sample_id
WHERE s.sample_id IS NULL;

-- CHECK: Samples missing required fields (instrument or creator)
-- Attributable (ALCOA+): every record needs an owner and a source instrument.
SELECT sample_id, instrument_id, created_by
FROM samples
WHERE instrument_id IS NULL OR created_by IS NULL;
-- SQL Server: same. Oracle: same (empty strings are NULL in Oracle).

-- CHECK: Samples with no CREATE entry in the audit trail
SELECT s.sample_id
FROM samples s
LEFT JOIN audit_log a ON a.record_id = s.sample_id AND a.action = 'CREATE'
WHERE a.log_id IS NULL;

-- CHECK: Results recorded by someone other than a known user in the audit trail
SELECT DISTINCT r.recorded_by
FROM results r
WHERE r.recorded_by NOT IN (SELECT DISTINCT username FROM audit_log);
