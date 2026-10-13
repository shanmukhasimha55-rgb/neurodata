import sqlite3
import os

DB_FILE = os.path.join(os.path.dirname(__file__), "neurodata.db")

def get_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initializes the database schema and seeds initial records if empty."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Enable foreign keys
    cursor.execute("PRAGMA foreign_keys = ON;")
    
    # 1. Create Tables
    cursor.executescript("""
    CREATE TABLE IF NOT EXISTS DATASETS (
        dataset_id INTEGER PRIMARY KEY AUTOINCREMENT,
        table_name TEXT NOT NULL UNIQUE,
        target_database TEXT NOT NULL,
        row_count INTEGER DEFAULT 0 CHECK (row_count >= 0),
        last_refreshed TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS PIPELINES (
        pipeline_id INTEGER PRIMARY KEY AUTOINCREMENT,
        dataset_id INTEGER NOT NULL,
        pipeline_name TEXT NOT NULL UNIQUE,
        schedule_cron TEXT DEFAULT '0 * * * *',
        owner_email TEXT NOT NULL,
        is_active INTEGER DEFAULT 1 CHECK (is_active IN (0, 1)),
        FOREIGN KEY (dataset_id) REFERENCES DATASETS(dataset_id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS PIPELINE_RUNS (
        run_id INTEGER PRIMARY KEY AUTOINCREMENT,
        pipeline_id INTEGER NOT NULL,
        start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        end_time TIMESTAMP NULL,
        status TEXT DEFAULT 'Running' CHECK (status IN ('Running', 'Success', 'Failed', 'Cancelled')),
        records_processed INTEGER DEFAULT 0 CHECK (records_processed >= 0),
        FOREIGN KEY (pipeline_id) REFERENCES PIPELINES(pipeline_id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS QUALITY_RULES (
        rule_id INTEGER PRIMARY KEY AUTOINCREMENT,
        dataset_id INTEGER NOT NULL,
        column_name TEXT NOT NULL,
        rule_type TEXT NOT NULL CHECK (rule_type IN ('NOT_NULL', 'RANGE', 'UNIQUE', 'REGEX', 'ROW_COUNT_STABILITY')),
        threshold_value TEXT,
        severity TEXT DEFAULT 'HIGH' CHECK (severity IN ('CRITICAL', 'HIGH', 'MEDIUM', 'LOW')),
        FOREIGN KEY (dataset_id) REFERENCES DATASETS(dataset_id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS RULE_VALIDATIONS (
        validation_id INTEGER PRIMARY KEY AUTOINCREMENT,
        run_id INTEGER NOT NULL,
        rule_id INTEGER NOT NULL,
        passed INTEGER NOT NULL CHECK (passed IN (0, 1)),
        failed_row_count INTEGER DEFAULT 0 CHECK (failed_row_count >= 0),
        validated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (run_id) REFERENCES PIPELINE_RUNS(run_id) ON DELETE CASCADE,
        FOREIGN KEY (rule_id) REFERENCES QUALITY_RULES(rule_id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS ANOMALY_ALERTS (
        alert_id INTEGER PRIMARY KEY AUTOINCREMENT,
        dataset_id INTEGER NOT NULL,
        metric_name TEXT NOT NULL,
        expected_value REAL NOT NULL,
        actual_value REAL NOT NULL,
        variance_pct REAL NOT NULL,
        alert_status TEXT DEFAULT 'Open' CHECK (alert_status IN ('Open', 'Acknowledged', 'Resolved')),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (dataset_id) REFERENCES DATASETS(dataset_id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS PIPELINE_LOGS (
        log_id INTEGER PRIMARY KEY AUTOINCREMENT,
        run_id INTEGER NOT NULL,
        log_level TEXT NOT NULL CHECK (log_level IN ('INFO', 'WARN', 'ERROR', 'CRITICAL')),
        message TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (run_id) REFERENCES PIPELINE_RUNS(run_id) ON DELETE CASCADE
    );
    """)
    
    # Check if DATASETS table is already seeded
    cursor.execute("SELECT COUNT(*) FROM DATASETS")
    count = cursor.fetchone()[0]
    
    if count == 0:
        # Seed 10 records per table
        cursor.executescript("""
        INSERT INTO DATASETS (dataset_id, table_name, target_database, row_count, last_refreshed) VALUES
        (1, 'raw_user_events', 'analytics_dw', 1500000, datetime('now', '-10 minutes')),
        (2, 'financial_transactions', 'finance_dw', 450000, datetime('now', '-25 minutes')),
        (3, 'product_catalog', 'ecommerce_db', 8200, datetime('now', '-2 hours')),
        (4, 'ml_feature_store', 'ml_platform', 2300000, datetime('now', '-5 minutes')),
        (5, 'customer_profiles', 'crm_dw', 620000, datetime('now', '-1 hour')),
        (6, 'iot_sensor_telemetry', 'iot_warehouse', 12000000, datetime('now', '-1 minute')),
        (7, 'website_clickstream', 'analytics_dw', 4500000, datetime('now', '-15 minutes')),
        (8, 'order_fulfillment_logs', 'logistics_db', 95000, datetime('now', '-45 minutes')),
        (9, 'marketing_campaigns', 'marketing_db', 1500, datetime('now', '-3 hours')),
        (10, 'support_tickets', 'cx_analytics', 48000, datetime('now', '-30 minutes'));

        INSERT INTO PIPELINES (pipeline_id, dataset_id, pipeline_name, schedule_cron, owner_email, is_active) VALUES
        (1, 1, 'user_clickstream_etl', '0 * * * *', 'data_team@neurodata.ai', 1),
        (2, 2, 'payment_reconciliation_batch', '0 0 * * *', 'finance_eng@neurodata.ai', 1),
        (3, 3, 'catalog_sync_hourly', '0 */2 * * *', 'catalog_team@neurodata.ai', 1),
        (4, 4, 'feature_store_backfill', '*/15 * * * *', 'mlops_eng@neurodata.ai', 1),
        (5, 5, 'crm_sync_nightly', '0 2 * * *', 'crm_team@neurodata.ai', 1),
        (6, 6, 'iot_telemetry_stream', '*/5 * * * *', 'iot_eng@neurodata.ai', 1),
        (7, 7, 'clickstream_attribution', '0 * * * *', 'growth_data@neurodata.ai', 1),
        (8, 8, 'logistics_tracking_sync', '0 */4 * * *', 'logistics@neurodata.ai', 1),
        (9, 9, 'campaign_roi_pipeline', '0 6 * * *', 'marketing_data@neurodata.ai', 0),
        (10, 10, 'cx_ticket_nlp_etl', '0 */6 * * *', 'nlp_team@neurodata.ai', 1);

        INSERT INTO PIPELINE_RUNS (run_id, pipeline_id, start_time, end_time, status, records_processed) VALUES
        (101, 1, datetime('now', '-2 hours'), datetime('now', '-115 minutes'), 'Success', 150000),
        (102, 1, datetime('now', '-1 hour'), datetime('now', '-55 minutes'), 'Success', 155000),
        (103, 2, datetime('now', '-5 hours'), datetime('now', '-280 minutes'), 'Success', 45000),
        (104, 2, datetime('now', '-1 hour'), datetime('now', '-50 minutes'), 'Failed', 12000),
        (105, 3, datetime('now', '-3 hours'), datetime('now', '-178 minutes'), 'Success', 8200),
        (106, 4, datetime('now', '-30 minutes'), datetime('now', '-25 minutes'), 'Success', 230000),
        (107, 4, datetime('now', '-10 minutes'), datetime('now', '-5 minutes'), 'Failed', 45000),
        (108, 5, datetime('now', '-1 day'), datetime('now', '-23 hours'), 'Success', 620000),
        (109, 6, datetime('now', '-15 minutes'), datetime('now', '-10 minutes'), 'Success', 500000),
        (110, 8, datetime('now', '-4 hours'), datetime('now', '-230 minutes'), 'Failed', 5000);

        INSERT INTO QUALITY_RULES (rule_id, dataset_id, column_name, rule_type, threshold_value, severity) VALUES
        (1, 1, 'user_id', 'NOT_NULL', NULL, 'CRITICAL'),
        (2, 1, 'event_timestamp', 'NOT_NULL', NULL, 'CRITICAL'),
        (3, 2, 'transaction_amount', 'RANGE', '0.01:1000000.00', 'CRITICAL'),
        (4, 2, 'account_id', 'NOT_NULL', NULL, 'CRITICAL'),
        (5, 3, 'price', 'RANGE', '0.00:50000.00', 'HIGH'),
        (6, 4, 'feature_vector', 'NOT_NULL', NULL, 'CRITICAL'),
        (7, 5, 'email', 'REGEX', '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$', 'HIGH'),
        (8, 6, 'vibration_hz', 'RANGE', '0.0:500.0', 'MEDIUM'),
        (9, 7, 'session_id', 'UNIQUE', NULL, 'HIGH'),
        (10, 8, 'package_status', 'NOT_NULL', NULL, 'MEDIUM');

        INSERT INTO RULE_VALIDATIONS (validation_id, run_id, rule_id, passed, failed_row_count, validated_at) VALUES
        (501, 101, 1, 1, 0, datetime('now', '-115 minutes')),
        (502, 101, 2, 1, 0, datetime('now', '-115 minutes')),
        (503, 103, 3, 1, 0, datetime('now', '-280 minutes')),
        (504, 104, 3, 0, 142, datetime('now', '-50 minutes')),
        (505, 104, 4, 1, 0, datetime('now', '-50 minutes')),
        (506, 105, 5, 1, 0, datetime('now', '-178 minutes')),
        (507, 106, 6, 1, 0, datetime('now', '-25 minutes')),
        (508, 107, 6, 0, 890, datetime('now', '-5 minutes')),
        (509, 108, 7, 1, 0, datetime('now', '-23 hours')),
        (510, 110, 10, 0, 52, datetime('now', '-230 minutes'));

        INSERT INTO ANOMALY_ALERTS (alert_id, dataset_id, metric_name, expected_value, actual_value, variance_pct, alert_status, created_at) VALUES
        (1, 2, 'ROW_COUNT_DROP', 450000.00, 120000.00, 73.33, 'Open', datetime('now', '-50 minutes')),
        (2, 4, 'DATASET_HEALTH_SCORE', 100.00, 50.00, 50.00, 'Open', datetime('now', '-5 minutes')),
        (3, 8, 'NULL_VALUE_SPIKE', 0.00, 52.00, 100.00, 'Acknowledged', datetime('now', '-230 minutes')),
        (4, 1, 'ROW_COUNT_DROP', 150000.00, 45000.00, 70.00, 'Resolved', datetime('now', '-2 days')),
        (5, 6, 'SENSOR_RANGE_OUTLIER', 250.00, 480.00, 92.00, 'Open', datetime('now', '-15 minutes')),
        (6, 2, 'TRANSACTION_AMOUNT_SPIKE', 50.00, 8900.00, 1770.00, 'Open', datetime('now', '-1 hour')),
        (7, 5, 'INVALID_EMAIL_PATTERN', 0.00, 15.00, 100.00, 'Resolved', datetime('now', '-1 day')),
        (8, 7, 'DUPLICATE_SESSION_IDS', 0.00, 34.00, 100.00, 'Acknowledged', datetime('now', '-6 hours')),
        (9, 3, 'PRICE_ZERO_ALERT', 0.00, 2.00, 100.00, 'Resolved', datetime('now', '-3 days')),
        (10, 10, 'ROW_COUNT_STABILITY', 48000.00, 12000.00, 75.00, 'Open', datetime('now', '-30 minutes'));

        INSERT INTO PIPELINE_LOGS (log_id, run_id, log_level, message, created_at) VALUES
        (1, 101, 'INFO', 'Job started for pipeline user_clickstream_etl', datetime('now', '-2 hours')),
        (2, 101, 'INFO', 'All quality rules passed successfully.', datetime('now', '-115 minutes')),
        (3, 104, 'INFO', 'Job started for pipeline payment_reconciliation_batch', datetime('now', '-1 hour')),
        (4, 104, 'ERROR', 'Rule validation failed for TRANSACTION_AMOUNT (142 rows invalid).', datetime('now', '-50 minutes')),
        (5, 104, 'CRITICAL', 'Pipeline terminated with status FAILED due to critical rule violations.', datetime('now', '-50 minutes')),
        (6, 106, 'INFO', 'Feature store backfill completed successfully.', datetime('now', '-25 minutes')),
        (7, 107, 'ERROR', 'NULL values detected in feature_vector column (890 rows invalid).', datetime('now', '-5 minutes')),
        (8, 108, 'INFO', 'CRM nightly sync finished. 620,000 records processed.', datetime('now', '-23 hours')),
        (9, 110, 'WARN', 'Missing package_status for 52 records in order_fulfillment_logs.', datetime('now', '-230 minutes')),
        (10, 109, 'INFO', 'IoT streaming pipeline processed 500,000 events without errors.', datetime('now', '-10 minutes'));
        """)
    
    conn.commit()
    conn.close()

# --- PL/SQL Simulation Python Functions ---

def fn_calculate_pipeline_sla(pipeline_id):
    """Function 1: Returns SLA success rate % for a pipeline."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM PIPELINE_RUNS WHERE pipeline_id = ?", (pipeline_id,))
    total = cursor.fetchone()[0]
    if total == 0:
        conn.close()
        return 100.0
    cursor.execute("SELECT COUNT(*) FROM PIPELINE_RUNS WHERE pipeline_id = ? AND status = 'Success'", (pipeline_id,))
    success = cursor.fetchone()[0]
    conn.close()
    return round((success / total) * 100.0, 2)

def fn_get_dataset_health_score(dataset_id):
    """Function 2: Returns Data Quality Health Score (0-100) for a dataset."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT COUNT(*) FROM RULE_VALIDATIONS rv
        JOIN QUALITY_RULES qr ON rv.rule_id = qr.rule_id
        WHERE qr.dataset_id = ?
    """, (dataset_id,))
    total = cursor.fetchone()[0]
    if total == 0:
        conn.close()
        return 100.0
    cursor.execute("""
        SELECT COUNT(*) FROM RULE_VALIDATIONS rv
        JOIN QUALITY_RULES qr ON rv.rule_id = qr.rule_id
        WHERE qr.dataset_id = ? AND rv.passed = 1
    """, (dataset_id,))
    passed = cursor.fetchone()[0]
    conn.close()
    return round((passed / total) * 100.0, 2)

def sp_execute_pipeline_run(pipeline_id, records_processed):
    """Procedure 1: Starts a new pipeline run, logs execution, and returns run_id."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO PIPELINE_RUNS (pipeline_id, start_time, status, records_processed)
        VALUES (?, datetime('now'), 'Running', ?)
    """, (pipeline_id, records_processed))
    run_id = cursor.lastrowid
    
    cursor.execute("""
        INSERT INTO PIPELINE_LOGS (run_id, log_level, message, created_at)
        VALUES (?, 'INFO', ?, datetime('now'))
    """, (run_id, f"Pipeline execution started for Pipeline ID: {pipeline_id}"))
    
    conn.commit()
    conn.close()
    return run_id

def sp_complete_pipeline_run(run_id):
    """Procedure 2: Evaluates quality validations and sets final run status."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT COUNT(*) FROM RULE_VALIDATIONS rv
        JOIN QUALITY_RULES qr ON rv.rule_id = qr.rule_id
        WHERE rv.run_id = ? AND rv.passed = 0 AND qr.severity = 'CRITICAL'
    """, (run_id,))
    critical_failures = cursor.fetchone()[0]
    
    if critical_failures > 0:
        cursor.execute("""
            UPDATE PIPELINE_RUNS SET status = 'Failed', end_time = datetime('now') WHERE run_id = ?
        """, (run_id,))
        cursor.execute("""
            INSERT INTO PIPELINE_LOGS (run_id, log_level, message, created_at)
            VALUES (?, 'ERROR', ?, datetime('now'))
        """, (run_id, f"Pipeline failed due to {critical_failures} critical data quality rule violation(s)."))
    else:
        cursor.execute("""
            UPDATE PIPELINE_RUNS SET status = 'Success', end_time = datetime('now') WHERE run_id = ?
        """, (run_id,))
        cursor.execute("""
            INSERT INTO PIPELINE_LOGS (run_id, log_level, message, created_at)
            VALUES (?, 'INFO', 'Pipeline completed successfully with all quality checks passed.', datetime('now'))
        """, (run_id,))
        
    conn.commit()
    conn.close()

def cur_daily_quality_audit_sweep():
    """Cursor simulation: Sweeps all datasets and flags health scores < 75%."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT dataset_id, table_name FROM DATASETS")
    datasets = cursor.fetchall()
    
    alerts_triggered = 0
    for row in datasets:
        d_id = row['dataset_id']
        health = fn_get_dataset_health_score(d_id)
        if health < 75.0:
            cursor.execute("""
                INSERT INTO ANOMALY_ALERTS (dataset_id, metric_name, expected_value, actual_value, variance_pct, alert_status, created_at)
                VALUES (?, 'DATASET_HEALTH_SCORE', 100.0, ?, ?, 'Open', datetime('now'))
            """, (d_id, health, round(100.0 - health, 2)))
            alerts_triggered += 1
            
    conn.commit()
    conn.close()
    return alerts_triggered

def update_dataset_rows(dataset_id, new_row_count):
    """Trigger Simulation: Updates row count and fires trg_detect_volume_anomaly if count drops >30%."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT row_count FROM DATASETS WHERE dataset_id = ?", (dataset_id,))
    old_count = cursor.fetchone()[0]
    
    cursor.execute("UPDATE DATASETS SET row_count = ?, last_refreshed = datetime('now') WHERE dataset_id = ?", (new_row_count, dataset_id))
    
    alert_created = False
    if old_count > 0 and new_row_count < old_count:
        drop_pct = ((old_count - new_row_count) / old_count) * 100.0
        if drop_pct > 30.0:
            cursor.execute("""
                INSERT INTO ANOMALY_ALERTS (dataset_id, metric_name, expected_value, actual_value, variance_pct, alert_status, created_at)
                VALUES (?, 'ROW_COUNT_DROP', ?, ?, ?, 'Open', datetime('now'))
            """, (dataset_id, old_count, new_row_count, round(drop_pct, 2)))
            alert_created = True
            
    conn.commit()
    conn.close()
    return alert_created

if __name__ == "__main__":
    init_db()
    print("Database initialized and populated successfully.")
