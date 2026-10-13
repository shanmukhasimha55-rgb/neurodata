-- ============================================================
-- NeuroData — PL/SQL Procedures, Functions, Cursor & Triggers
-- ============================================================

-- ------------------------------------------------------------
-- PROCEDURE 1: sp_execute_pipeline_run
-- Starts a new pipeline execution run and logs initial status
-- ------------------------------------------------------------
DELIMITER //
CREATE PROCEDURE sp_execute_pipeline_run(
    IN p_pipeline_id INT,
    IN p_records_processed INT,
    OUT p_run_id INT
)
BEGIN
    -- Insert new pipeline run entry
    INSERT INTO PIPELINE_RUNS (pipeline_id, start_time, status, records_processed)
    VALUES (p_pipeline_id, NOW(), 'Running', p_records_processed);
    
    SET p_run_id = LAST_INSERT_ID();
    
    -- Log pipeline execution start
    INSERT INTO PIPELINE_LOGS (run_id, log_level, message)
    VALUES (p_run_id, 'INFO', CONCAT('Pipeline execution started for Pipeline ID: ', p_pipeline_id));
END //
DELIMITER ;

-- ------------------------------------------------------------
-- PROCEDURE 2: sp_complete_pipeline_run
-- Finalizes pipeline run status based on critical rule violations
-- ------------------------------------------------------------
DELIMITER //
CREATE PROCEDURE sp_complete_pipeline_run(
    IN p_run_id INT
)
BEGIN
    DECLARE v_critical_failures INT DEFAULT 0;
    
    -- Count critical quality rule failures for this run
    SELECT COUNT(*) INTO v_critical_failures
    FROM RULE_VALIDATIONS rv
    JOIN QUALITY_RULES qr ON rv.rule_id = qr.rule_id
    WHERE rv.run_id = p_run_id 
      AND rv.passed = 0 
      AND qr.severity = 'CRITICAL';
      
    IF v_critical_failures > 0 THEN
        UPDATE PIPELINE_RUNS 
        SET status = 'Failed', end_time = NOW() 
        WHERE run_id = p_run_id;
        
        INSERT INTO PIPELINE_LOGS (run_id, log_level, message)
        VALUES (p_run_id, 'ERROR', CONCAT('Pipeline failed due to ', v_critical_failures, ' critical data quality rule violation(s).'));
    ELSE
        UPDATE PIPELINE_RUNS 
        SET status = 'Success', end_time = NOW() 
        WHERE run_id = p_run_id;
        
        INSERT INTO PIPELINE_LOGS (run_id, log_level, message)
        VALUES (p_run_id, 'INFO', 'Pipeline completed successfully with all quality checks passed.');
    END IF;
END //
DELIMITER ;

-- ------------------------------------------------------------
-- FUNCTION 1: fn_calculate_pipeline_sla
-- Calculates SLA success percentage for a pipeline
-- ------------------------------------------------------------
DELIMITER //
CREATE FUNCTION fn_calculate_pipeline_sla(p_pipeline_id INT) 
RETURNS NUMERIC(5,2)
DETERMINISTIC
BEGIN
    DECLARE v_total_runs INT DEFAULT 0;
    DECLARE v_success_runs INT DEFAULT 0;
    DECLARE v_sla NUMERIC(5,2) DEFAULT 100.00;
    
    SELECT COUNT(*) INTO v_total_runs 
    FROM PIPELINE_RUNS 
    WHERE pipeline_id = p_pipeline_id;
    
    IF v_total_runs > 0 THEN
        SELECT COUNT(*) INTO v_success_runs 
        FROM PIPELINE_RUNS 
        WHERE pipeline_id = p_pipeline_id AND status = 'Success';
        
        SET v_sla = (v_success_runs / v_total_runs) * 100.00;
    END IF;
    
    RETURN v_sla;
END //
DELIMITER ;

-- ------------------------------------------------------------
-- FUNCTION 2: fn_get_dataset_health_score
-- Calculates quality health score (0-100) for a dataset
-- ------------------------------------------------------------
DELIMITER //
CREATE FUNCTION fn_get_dataset_health_score(p_dataset_id INT) 
RETURNS NUMERIC(5,2)
DETERMINISTIC
BEGIN
    DECLARE v_total_validations INT DEFAULT 0;
    DECLARE v_passed_validations INT DEFAULT 0;
    DECLARE v_health_score NUMERIC(5,2) DEFAULT 100.00;
    
    SELECT COUNT(*) INTO v_total_validations
    FROM RULE_VALIDATIONS rv
    JOIN QUALITY_RULES qr ON rv.rule_id = qr.rule_id
    WHERE qr.dataset_id = p_dataset_id;
    
    IF v_total_validations > 0 THEN
        SELECT COUNT(*) INTO v_passed_validations
        FROM RULE_VALIDATIONS rv
        JOIN QUALITY_RULES qr ON rv.rule_id = qr.rule_id
        WHERE qr.dataset_id = p_dataset_id AND rv.passed = 1;
        
        SET v_health_score = (v_passed_validations / v_total_validations) * 100.00;
    END IF;
    
    RETURN v_health_score;
END //
DELIMITER ;

-- ------------------------------------------------------------
-- CURSOR: cur_daily_quality_audit_sweep
-- Sweeps all datasets and flags low health scores into ANOMALY_ALERTS
-- ------------------------------------------------------------
DELIMITER //
CREATE PROCEDURE cur_daily_quality_audit_sweep()
BEGIN
    DECLARE done INT DEFAULT FALSE;
    DECLARE v_dataset_id INT;
    DECLARE v_table_name VARCHAR(100);
    DECLARE v_health_score NUMERIC(5,2);
    
    DECLARE dataset_cursor CURSOR FOR 
        SELECT dataset_id, table_name FROM DATASETS;
        
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;
    
    OPEN dataset_cursor;
    
    read_loop: LOOP
        FETCH dataset_cursor INTO v_dataset_id, v_table_name;
        IF done THEN
            LEAVE read_loop;
        END IF;
        
        SET v_health_score = fn_get_dataset_health_score(v_dataset_id);
        
        IF v_health_score < 75.00 THEN
            INSERT INTO ANOMALY_ALERTS (dataset_id, metric_name, expected_value, actual_value, variance_pct, alert_status)
            VALUES (v_dataset_id, 'DATASET_HEALTH_SCORE', 100.00, v_health_score, (100.00 - v_health_score), 'Open');
        END IF;
    END LOOP;
    
    CLOSE dataset_cursor;
END //
DELIMITER ;

-- ------------------------------------------------------------
-- TRIGGER 1: trg_detect_volume_anomaly
-- Triggers anomaly alert if dataset row count drops by >30%
-- ------------------------------------------------------------
DELIMITER //
CREATE TRIGGER trg_detect_volume_anomaly
AFTER UPDATE ON DATASETS
FOR EACH ROW
BEGIN
    DECLARE v_diff_pct NUMERIC(5,2);
    
    IF OLD.row_count > 0 AND NEW.row_count <> OLD.row_count THEN
        SET v_diff_pct = ((NEW.row_count - OLD.row_count) / OLD.row_count) * 100.00;
        
        IF v_diff_pct < -30.00 THEN
            INSERT INTO ANOMALY_ALERTS (dataset_id, metric_name, expected_value, actual_value, variance_pct, alert_status)
            VALUES (NEW.dataset_id, 'ROW_COUNT_DROP', OLD.row_count, NEW.row_count, ABS(v_diff_pct), 'Open');
        END IF;
    END IF;
END //
DELIMITER ;

-- ------------------------------------------------------------
-- TRIGGER 2: trg_auto_log_failed_rule
-- Automatically writes a log entry whenever a rule validation fails
-- ------------------------------------------------------------
DELIMITER //
CREATE TRIGGER trg_auto_log_failed_rule
AFTER INSERT ON RULE_VALIDATIONS
FOR EACH ROW
BEGIN
    DECLARE v_rule_type VARCHAR(50);
    DECLARE v_col_name VARCHAR(100);
    
    IF NEW.passed = 0 THEN
        SELECT rule_type, column_name INTO v_rule_type, v_col_name
        FROM QUALITY_RULES WHERE rule_id = NEW.rule_id;
        
        INSERT INTO PIPELINE_LOGS (run_id, log_level, message)
        VALUES (
            NEW.run_id, 
            'WARN', 
            CONCAT('Quality check failed for rule [', v_rule_type, '] on column [', v_col_name, ']. Failed rows: ', NEW.failed_row_count)
        );
    END IF;
END //
DELIMITER ;
