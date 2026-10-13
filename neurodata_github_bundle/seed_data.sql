-- ============================================================
-- NeuroData — Seed Data (10+ records per table)
-- ============================================================

-- 1. DATASETS (10 records)
INSERT INTO DATASETS (dataset_id, table_name, target_database, row_count, last_refreshed) VALUES
(1, 'raw_user_events', 'analytics_dw', 1500000, NOW() - INTERVAL 10 MINUTE),
(2, 'financial_transactions', 'finance_dw', 450000, NOW() - INTERVAL 25 MINUTE),
(3, 'product_catalog', 'ecommerce_db', 8200, NOW() - INTERVAL 2 HOUR),
(4, 'ml_feature_store', 'ml_platform', 2300000, NOW() - INTERVAL 5 MINUTE),
(5, 'customer_profiles', 'crm_dw', 620000, NOW() - INTERVAL 1 HOUR),
(6, 'iot_sensor_telemetry', 'iot_warehouse', 12000000, NOW() - INTERVAL 1 MINUTE),
(7, 'website_clickstream', 'analytics_dw', 4500000, NOW() - INTERVAL 15 MINUTE),
(8, 'order_fulfillment_logs', 'logistics_db', 95000, NOW() - INTERVAL 45 MINUTE),
(9, 'marketing_campaigns', 'marketing_db', 1500, NOW() - INTERVAL 3 HOUR),
(10, 'support_tickets', 'cx_analytics', 48000, NOW() - INTERVAL 30 MINUTE);

-- 2. PIPELINES (10 records)
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

-- 3. PIPELINE_RUNS (10 records)
INSERT INTO PIPELINE_RUNS (run_id, pipeline_id, start_time, end_time, status, records_processed) VALUES
(101, 1, NOW() - INTERVAL 2 HOUR, NOW() - INTERVAL 1 HOUR 55 MINUTE, 'Success', 150000),
(102, 1, NOW() - INTERVAL 1 HOUR, NOW() - INTERVAL 55 MINUTE, 'Success', 155000),
(103, 2, NOW() - INTERVAL 5 HOUR, NOW() - INTERVAL 4 HOUR 40 MINUTE, 'Success', 45000),
(104, 2, NOW() - INTERVAL 1 HOUR, NOW() - INTERVAL 50 MINUTE, 'Failed', 12000),
(105, 3, NOW() - INTERVAL 3 HOUR, NOW() - INTERVAL 2 HOUR 58 MINUTE, 'Success', 8200),
(106, 4, NOW() - INTERVAL 30 MINUTE, NOW() - INTERVAL 25 MINUTE, 'Success', 230000),
(107, 4, NOW() - INTERVAL 10 MINUTE, NOW() - INTERVAL 5 MINUTE, 'Failed', 45000),
(108, 5, NOW() - INTERVAL 1 DAY, NOW() - INTERVAL 23 HOUR, 'Success', 620000),
(109, 6, NOW() - INTERVAL 15 MINUTE, NOW() - INTERVAL 10 MINUTE, 'Success', 500000),
(110, 8, NOW() - INTERVAL 4 HOUR, NOW() - INTERVAL 3 HOUR 50 MINUTE, 'Failed', 5000);

-- 4. QUALITY_RULES (10 records)
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

-- 5. RULE_VALIDATIONS (10 records)
INSERT INTO RULE_VALIDATIONS (validation_id, run_id, rule_id, passed, failed_row_count, validated_at) VALUES
(501, 101, 1, 1, 0, NOW() - INTERVAL 1 HOUR 55 MINUTE),
(502, 101, 2, 1, 0, NOW() - INTERVAL 1 HOUR 55 MINUTE),
(503, 103, 3, 1, 0, NOW() - INTERVAL 4 HOUR 40 MINUTE),
(504, 104, 3, 0, 142, NOW() - INTERVAL 50 MINUTE),
(505, 104, 4, 1, 0, NOW() - INTERVAL 50 MINUTE),
(506, 105, 5, 1, 0, NOW() - INTERVAL 2 HOUR 58 MINUTE),
(507, 106, 6, 1, 0, NOW() - INTERVAL 25 MINUTE),
(508, 107, 6, 0, 890, NOW() - INTERVAL 5 MINUTE),
(509, 108, 7, 1, 0, NOW() - INTERVAL 23 HOUR),
(510, 110, 10, 0, 52, NOW() - INTERVAL 3 HOUR 50 MINUTE);

-- 6. ANOMALY_ALERTS (10 records)
INSERT INTO ANOMALY_ALERTS (alert_id, dataset_id, metric_name, expected_value, actual_value, variance_pct, alert_status, created_at) VALUES
(1, 2, 'ROW_COUNT_DROP', 450000.00, 120000.00, 73.33, 'Open', NOW() - INTERVAL 50 MINUTE),
(2, 4, 'DATASET_HEALTH_SCORE', 100.00, 50.00, 50.00, 'Open', NOW() - INTERVAL 5 MINUTE),
(3, 8, 'NULL_VALUE_SPIKE', 0.00, 52.00, 100.00, 'Acknowledged', NOW() - INTERVAL 3 HOUR 50 MINUTE),
(4, 1, 'ROW_COUNT_DROP', 150000.00, 45000.00, 70.00, 'Resolved', NOW() - INTERVAL 2 DAY),
(5, 6, 'SENSOR_RANGE_OUTLIER', 250.00, 480.00, 92.00, 'Open', NOW() - INTERVAL 15 MINUTE),
(6, 2, 'TRANSACTION_AMOUNT_SPIKE', 50.00, 8900.00, 1770.00, 'Open', NOW() - INTERVAL 1 HOUR),
(7, 5, 'INVALID_EMAIL_PATTERN', 0.00, 15.00, 100.00, 'Resolved', NOW() - INTERVAL 1 DAY),
(8, 7, 'DUPLICATE_SESSION_IDS', 0.00, 34.00, 100.00, 'Acknowledged', NOW() - INTERVAL 6 HOUR),
(9, 3, 'PRICE_ZERO_ALERT', 0.00, 2.00, 100.00, 'Resolved', NOW() - INTERVAL 3 DAY),
(10, 10, 'ROW_COUNT_STABILITY', 48000.00, 12000.00, 75.00, 'Open', NOW() - INTERVAL 30 MINUTE);

-- 7. PIPELINE_LOGS (10 records)
INSERT INTO PIPELINE_LOGS (log_id, run_id, log_level, message, created_at) VALUES
(1, 101, 'INFO', 'Job started for pipeline user_clickstream_etl', NOW() - INTERVAL 2 HOUR),
(2, 101, 'INFO', 'All quality rules passed successfully.', NOW() - INTERVAL 1 HOUR 55 MINUTE),
(3, 104, 'INFO', 'Job started for pipeline payment_reconciliation_batch', NOW() - INTERVAL 1 HOUR),
(4, 104, 'ERROR', 'Rule validation failed for TRANSACTION_AMOUNT (142 rows invalid).', NOW() - INTERVAL 50 MINUTE),
(5, 104, 'CRITICAL', 'Pipeline terminated with status FAILED due to critical rule violations.', NOW() - INTERVAL 50 MINUTE),
(6, 106, 'INFO', 'Feature store backfill completed successfully.', NOW() - INTERVAL 25 MINUTE),
(7, 107, 'ERROR', 'NULL values detected in feature_vector column (890 rows invalid).', NOW() - INTERVAL 5 MINUTE),
(8, 108, 'INFO', 'CRM nightly sync finished. 620,000 records processed.', NOW() - INTERVAL 23 HOUR),
(9, 110, 'WARN', 'Missing package_status for 52 records in order_fulfillment_logs.', NOW() - INTERVAL 3 HOUR 50 MINUTE),
(10, 109, 'INFO', 'IoT streaming pipeline processed 500,000 events without errors.', NOW() - INTERVAL 10 MINUTE);
