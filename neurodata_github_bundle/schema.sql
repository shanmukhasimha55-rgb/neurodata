-- ============================================================
-- NeuroData — AI Data Quality & Pipeline Orchestration Platform
-- Database Schema Script (7 Relational Tables)
-- ============================================================

DROP TABLE IF EXISTS PIPELINE_LOGS;
DROP TABLE IF EXISTS ANOMALY_ALERTS;
DROP TABLE IF EXISTS RULE_VALIDATIONS;
DROP TABLE IF EXISTS QUALITY_RULES;
DROP TABLE IF EXISTS PIPELINE_RUNS;
DROP TABLE IF EXISTS PIPELINES;
DROP TABLE IF EXISTS DATASETS;

-- 1. DATASETS Table
CREATE TABLE DATASETS (
    dataset_id INT PRIMARY KEY AUTO_INCREMENT,
    table_name VARCHAR(100) NOT NULL UNIQUE,
    target_database VARCHAR(50) NOT NULL,
    row_count BIGINT DEFAULT 0 CHECK (row_count >= 0),
    last_refreshed TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. PIPELINES Table
CREATE TABLE PIPELINES (
    pipeline_id INT PRIMARY KEY AUTO_INCREMENT,
    dataset_id INT NOT NULL,
    pipeline_name VARCHAR(100) NOT NULL UNIQUE,
    schedule_cron VARCHAR(50) DEFAULT '0 * * * *',
    owner_email VARCHAR(100) NOT NULL,
    is_active SMALLINT DEFAULT 1 CHECK (is_active IN (0, 1)),
    FOREIGN KEY (dataset_id) REFERENCES DATASETS(dataset_id) ON DELETE CASCADE
);

-- 3. PIPELINE_RUNS Table
CREATE TABLE PIPELINE_RUNS (
    run_id INT PRIMARY KEY AUTO_INCREMENT,
    pipeline_id INT NOT NULL,
    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    end_time TIMESTAMP NULL,
    status VARCHAR(20) DEFAULT 'Running' CHECK (status IN ('Running', 'Success', 'Failed', 'Cancelled')),
    records_processed INT DEFAULT 0 CHECK (records_processed >= 0),
    FOREIGN KEY (pipeline_id) REFERENCES PIPELINES(pipeline_id) ON DELETE CASCADE
);

-- 4. QUALITY_RULES Table
CREATE TABLE QUALITY_RULES (
    rule_id INT PRIMARY KEY AUTO_INCREMENT,
    dataset_id INT NOT NULL,
    column_name VARCHAR(100) NOT NULL,
    rule_type VARCHAR(50) NOT NULL CHECK (rule_type IN ('NOT_NULL', 'RANGE', 'UNIQUE', 'REGEX', 'ROW_COUNT_STABILITY')),
    threshold_value VARCHAR(100),
    severity VARCHAR(20) DEFAULT 'HIGH' CHECK (severity IN ('CRITICAL', 'HIGH', 'MEDIUM', 'LOW')),
    FOREIGN KEY (dataset_id) REFERENCES DATASETS(dataset_id) ON DELETE CASCADE
);

-- 5. RULE_VALIDATIONS Table
CREATE TABLE RULE_VALIDATIONS (
    validation_id INT PRIMARY KEY AUTO_INCREMENT,
    run_id INT NOT NULL,
    rule_id INT NOT NULL,
    passed SMALLINT NOT NULL CHECK (passed IN (0, 1)),
    failed_row_count INT DEFAULT 0 CHECK (failed_row_count >= 0),
    validated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (run_id) REFERENCES PIPELINE_RUNS(run_id) ON DELETE CASCADE,
    FOREIGN KEY (rule_id) REFERENCES QUALITY_RULES(rule_id) ON DELETE CASCADE
);

-- 6. ANOMALY_ALERTS Table
CREATE TABLE ANOMALY_ALERTS (
    alert_id INT PRIMARY KEY AUTO_INCREMENT,
    dataset_id INT NOT NULL,
    metric_name VARCHAR(50) NOT NULL,
    expected_value NUMERIC(12,2) NOT NULL,
    actual_value NUMERIC(12,2) NOT NULL,
    variance_pct NUMERIC(5,2) NOT NULL,
    alert_status VARCHAR(20) DEFAULT 'Open' CHECK (alert_status IN ('Open', 'Acknowledged', 'Resolved')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (dataset_id) REFERENCES DATASETS(dataset_id) ON DELETE CASCADE
);

-- 7. PIPELINE_LOGS Table
CREATE TABLE PIPELINE_LOGS (
    log_id INT PRIMARY KEY AUTO_INCREMENT,
    run_id INT NOT NULL,
    log_level VARCHAR(10) NOT NULL CHECK (log_level IN ('INFO', 'WARN', 'ERROR', 'CRITICAL')),
    message TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (run_id) REFERENCES PIPELINE_RUNS(run_id) ON DELETE CASCADE
);
