-- ============================================================
-- NeuroData — 15 Course-Required SQL Queries
-- ============================================================

-- Query 1: Data Retrieval with Simple Filter & Sort
-- Description: Retrieve active pipelines sorted alphabetically
SELECT pipeline_id, pipeline_name, owner_email, schedule_cron 
FROM PIPELINES 
WHERE is_active = 1 
ORDER BY pipeline_name ASC;

-- Query 2: INNER JOIN
-- Description: Join pipelines with their target dataset details
SELECT p.pipeline_name, d.table_name, d.target_database, d.row_count 
FROM PIPELINES p 
JOIN DATASETS d ON p.dataset_id = d.dataset_id;

-- Query 3: Multi-Table JOIN across 3 Tables
-- Description: Detailed report of pipeline runs with dataset and pipeline info
SELECT r.run_id, p.pipeline_name, d.table_name, r.status, r.records_processed, r.start_time
FROM PIPELINE_RUNS r
JOIN PIPELINES p ON r.pipeline_id = p.pipeline_id
JOIN DATASETS d ON p.dataset_id = d.dataset_id
ORDER BY r.start_time DESC;

-- Query 4: Aggregation & GROUP BY
-- Description: Count total execution runs and average records processed per run status
SELECT status, COUNT(*) AS total_runs, ROUND(AVG(records_processed), 2) AS avg_records
FROM PIPELINE_RUNS 
GROUP BY status;

-- Query 5: Subquery with Aggregate Comparison
-- Description: Find datasets whose row count is above the average row count across all datasets
SELECT table_name, target_database, row_count 
FROM DATASETS 
WHERE row_count > (SELECT AVG(row_count) FROM DATASETS);

-- Query 6: LEFT JOIN to find Unused Records
-- Description: List pipelines that have never executed a run
SELECT p.pipeline_id, p.pipeline_name, p.owner_email 
FROM PIPELINES p 
LEFT JOIN PIPELINE_RUNS r ON p.pipeline_id = r.pipeline_id 
WHERE r.run_id IS NULL;

-- Query 7: Aggregation with Multiple Tables
-- Description: Summarize total failed rows by quality rule type and severity
SELECT qr.rule_type, qr.severity, COUNT(rv.validation_id) AS evaluations_count, SUM(rv.failed_row_count) AS total_failed_rows
FROM QUALITY_RULES qr 
JOIN RULE_VALIDATIONS rv ON qr.rule_id = rv.rule_id
GROUP BY qr.rule_type, qr.severity;

-- Query 8: Subquery with IN Operator
-- Description: Retrieve dataset details that currently have open anomaly alerts
SELECT dataset_id, table_name, target_database 
FROM DATASETS 
WHERE dataset_id IN (SELECT dataset_id FROM ANOMALY_ALERTS WHERE alert_status = 'Open');

-- Query 9: Aggregate Analysis with SLA Calculation
-- Description: Summary of pipeline execution count and total records processed
SELECT p.pipeline_name, COUNT(r.run_id) AS total_runs, SUM(r.records_processed) AS total_volume
FROM PIPELINES p
LEFT JOIN PIPELINE_RUNS r ON p.pipeline_id = r.pipeline_id
GROUP BY p.pipeline_id, p.pipeline_name;

-- Query 10: Dataset Health Breakdown
-- Description: List quality rule distribution across datasets
SELECT d.table_name, COUNT(qr.rule_id) AS total_rules
FROM DATASETS d
LEFT JOIN QUALITY_RULES qr ON d.dataset_id = qr.dataset_id
GROUP BY d.dataset_id, d.table_name;

-- Query 11: Common Table Expression (CTE)
-- Description: Use CTE to calculate success vs failure rates per pipeline
WITH PipelineStats AS (
    SELECT pipeline_id, 
           COUNT(*) AS total_runs, 
           SUM(CASE WHEN status = 'Success' THEN 1 ELSE 0 END) AS successful_runs,
           SUM(CASE WHEN status = 'Failed' THEN 1 ELSE 0 END) AS failed_runs
    FROM PIPELINE_RUNS 
    GROUP BY pipeline_id
)
SELECT p.pipeline_name, ps.total_runs, ps.successful_runs, ps.failed_runs
FROM PIPELINES p 
JOIN PipelineStats ps ON p.pipeline_id = ps.pipeline_id;

-- Query 12: Top Rule Violations Ranking
-- Description: Find top 3 quality rules causing the highest number of failed rows
SELECT qr.rule_id, qr.column_name, qr.rule_type, SUM(rv.failed_row_count) AS total_failed_rows
FROM RULE_VALIDATIONS rv 
JOIN QUALITY_RULES qr ON rv.rule_id = qr.rule_id
WHERE rv.passed = 0 
GROUP BY qr.rule_id, qr.column_name, qr.rule_type
ORDER BY total_failed_rows DESC 
LIMIT 3;

-- Query 13: HAVING Clause Filtering
-- Description: Identify datasets that have experienced more than 1 anomaly alert
SELECT d.table_name, COUNT(a.alert_id) AS anomaly_count
FROM DATASETS d
JOIN ANOMALY_ALERTS a ON d.dataset_id = a.dataset_id
GROUP BY d.dataset_id, d.table_name
HAVING COUNT(a.alert_id) >= 1;

-- Query 14: Diagnostic Error Log Audit
-- Description: Retrieve high-severity diagnostic messages with pipeline context
SELECT l.log_id, p.pipeline_name, l.log_level, l.message, l.created_at
FROM PIPELINE_LOGS l 
JOIN PIPELINE_RUNS r ON l.run_id = r.run_id
JOIN PIPELINES p ON r.pipeline_id = p.pipeline_id
WHERE l.log_level IN ('WARN', 'ERROR', 'CRITICAL')
ORDER BY l.created_at DESC;

-- Query 15: Anomaly Variance Analysis
-- Description: Report metrics where actual dataset value diverged from expected threshold
SELECT d.table_name, a.metric_name, a.expected_value, a.actual_value, a.variance_pct, a.alert_status
FROM ANOMALY_ALERTS a 
JOIN DATASETS d ON a.dataset_id = d.dataset_id
ORDER BY a.variance_pct DESC;
