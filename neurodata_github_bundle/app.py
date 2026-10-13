import streamlit as st
import pandas as pd
import sqlite3
import database as db

st.set_page_config(
    page_title="NeuroData Platform",
    page_icon="🧠",
    layout="wide"
)

# Ensure DB is initialized
db.init_db()

st.sidebar.title("🧠 NeuroData AI Platform")
st.sidebar.markdown("**AI Data Quality & Orchestration Engine**")
menu = st.sidebar.radio("Navigation", [
    "📊 Pipeline Dashboard",
    "⚡ Trigger Pipeline Run",
    "🛡️ Quality Rules & Logs",
    "🚨 Anomaly Alert Center",
    "🔍 15-Query SQL Runner"
])

conn = db.get_connection()

# --- Page 1: Pipeline Dashboard ---
if menu == "📊 Pipeline Dashboard":
    st.title("📊 Data Pipelines & Dataset Health Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    # Summary Metrics
    total_pipelines = pd.read_sql("SELECT COUNT(*) FROM PIPELINES", conn).iloc[0, 0]
    total_datasets = pd.read_sql("SELECT COUNT(*) FROM DATASETS", conn).iloc[0, 0]
    open_alerts = pd.read_sql("SELECT COUNT(*) FROM ANOMALY_ALERTS WHERE alert_status = 'Open'", conn).iloc[0, 0]
    failed_runs = pd.read_sql("SELECT COUNT(*) FROM PIPELINE_RUNS WHERE status = 'Failed'", conn).iloc[0, 0]
    
    col1.metric("Total Pipelines", total_pipelines)
    col2.metric("Monitored Datasets", total_datasets)
    col3.metric("Open Anomaly Alerts", open_alerts, delta_color="inverse")
    col4.metric("Failed Runs", failed_runs, delta_color="inverse")
    
    st.divider()
    
    st.subheader("📋 Pipeline Performance & SLA Summary")
    df_pipelines = pd.read_sql("""
        SELECT p.pipeline_id, p.pipeline_name, d.table_name, p.owner_email, p.schedule_cron, p.is_active
        FROM PIPELINES p JOIN DATASETS d ON p.dataset_id = d.dataset_id
    """, conn)
    
    # Calculate PL/SQL simulated functions SLA and Health Score
    df_pipelines['SLA Success Rate (%)'] = df_pipelines['pipeline_id'].apply(db.fn_calculate_pipeline_sla)
    df_pipelines['Dataset Health Score'] = df_pipelines['pipeline_id'].apply(db.fn_get_dataset_health_score)
    
    st.dataframe(df_pipelines, use_container_width=True)
    
    st.subheader("⏱️ Recent Pipeline Runs")
    df_runs = pd.read_sql("""
        SELECT r.run_id, p.pipeline_name, r.status, r.records_processed, r.start_time, r.end_time
        FROM PIPELINE_RUNS r
        JOIN PIPELINES p ON r.pipeline_id = p.pipeline_id
        ORDER BY r.start_time DESC LIMIT 10
    """, conn)
    st.dataframe(df_runs, use_container_width=True)

# --- Page 2: Trigger Pipeline Run ---
elif menu == "⚡ Trigger Pipeline Run":
    st.title("⚡ Interactive Pipeline Execution Simulator")
    st.markdown("Demonstrates: **User Operation → PL/SQL Procedure → Database Processing → Result**")
    
    pipelines = pd.read_sql("SELECT pipeline_id, pipeline_name FROM PIPELINES WHERE is_active = 1", conn)
    pipeline_options = {row['pipeline_name']: row['pipeline_id'] for _, row in pipelines.iterrows()}
    
    selected_name = st.selectbox("Select Pipeline to Execute", list(pipeline_options.keys()))
    pipeline_id = pipeline_options[selected_name]
    
    records_count = st.number_input("Records to Process", min_value=100, max_value=5000000, value=25000, step=5000)
    simulated_outcome = st.radio("Simulate Outcome", ["Success (All Quality Checks Pass)", "Failure (Critical Rule Violation)"])
    
    if st.button("🚀 Execute Pipeline Procedure"):
        # Step 1: Call Procedure sp_execute_pipeline_run
        run_id = db.sp_execute_pipeline_run(pipeline_id, records_count)
        st.info(f"Procedure `sp_execute_pipeline_run` executed. Allocated Run ID: #{run_id}")
        
        # Step 2: Insert rule validation simulation
        if "Failure" in simulated_outcome:
            conn_temp = db.get_connection()
            cursor = conn_temp.cursor()
            # Fetch first rule for this dataset
            dataset_id = pd.read_sql(f"SELECT dataset_id FROM PIPELINES WHERE pipeline_id = {pipeline_id}", conn_temp).iloc[0,0]
            rule_id = pd.read_sql(f"SELECT rule_id FROM QUALITY_RULES WHERE dataset_id = {dataset_id} LIMIT 1", conn_temp).iloc[0,0]
            cursor.execute("""
                INSERT INTO RULE_VALIDATIONS (run_id, rule_id, passed, failed_row_count, validated_at)
                VALUES (?, ?, 0, 150, datetime('now'))
            """, (run_id, rule_id))
            conn_temp.commit()
            conn_temp.close()
        
        # Step 3: Call Procedure sp_complete_pipeline_run
        db.sp_complete_pipeline_run(run_id)
        
        if "Success" in simulated_outcome:
            st.success(f"Pipeline Run #{run_id} completed successfully with status: SUCCESS!")
        else:
            st.error(f"Pipeline Run #{run_id} completed with status: FAILED due to critical rule violations!")
            
        # Display Generated Logs
        st.subheader("📜 Diagnostic Logs Generated during Execution")
        df_logs = pd.read_sql(f"SELECT log_id, log_level, message, created_at FROM PIPELINE_LOGS WHERE run_id = {run_id}", conn)
        st.dataframe(df_logs, use_container_width=True)

# --- Page 3: Quality Rules & Logs ---
elif menu == "🛡️ Quality Rules & Logs":
    st.title("🛡️ Data Quality Assertion Rules & Diagnostic Logs")
    
    st.subheader("📋 Enforced Quality Rules")
    df_rules = pd.read_sql("""
        SELECT q.rule_id, d.table_name, q.column_name, q.rule_type, q.threshold_value, q.severity
        FROM QUALITY_RULES q JOIN DATASETS d ON q.dataset_id = d.dataset_id
    """, conn)
    st.dataframe(df_rules, use_container_width=True)
    
    st.subheader("🔍 Diagnostics & Error Log Audit")
    df_logs_all = pd.read_sql("""
        SELECT l.log_id, l.run_id, p.pipeline_name, l.log_level, l.message, l.created_at
        FROM PIPELINE_LOGS l 
        JOIN PIPELINE_RUNS r ON l.run_id = r.run_id
        JOIN PIPELINES p ON r.pipeline_id = p.pipeline_id
        ORDER BY l.created_at DESC
    """, conn)
    st.dataframe(df_logs_all, use_container_width=True)

# --- Page 4: Anomaly Alert Center ---
elif menu == "🚨 Anomaly Alert Center":
    st.title("🚨 AI Anomaly Alert Management & Trigger Simulator")
    
    st.subheader("Simulate Database Trigger `trg_detect_volume_anomaly`")
    st.write("Updating a dataset row count downwards by >30% automatically triggers an Anomaly Alert record!")
    
    datasets_df = pd.read_sql("SELECT dataset_id, table_name, row_count FROM DATASETS", conn)
    selected_ds = st.selectbox("Select Dataset to Update", datasets_df['table_name'])
    ds_row = datasets_df[datasets_df['table_name'] == selected_ds].iloc[0]
    
    st.write(f"Current Row Count for `{selected_ds}`: **{ds_row['row_count']:,}**")
    new_rows = st.number_input("New Row Count", min_value=0, value=int(ds_row['row_count'] * 0.5))
    
    if st.button("Update Row Count (Fire Trigger Simulation)"):
        alert_fired = db.update_dataset_rows(ds_row['dataset_id'], new_rows)
        if alert_fired:
            st.warning(f"Trigger Fired! Row count dropped from {ds_row['row_count']:,} to {new_rows:,} (>30% drop). Anomaly Alert created!")
        else:
            st.success("Row count updated. No volume drop anomaly triggered.")
            
    st.divider()
    
    st.subheader("📢 Active Anomaly Alerts")
    df_alerts = pd.read_sql("""
        SELECT a.alert_id, d.table_name, a.metric_name, a.expected_value, a.actual_value, a.variance_pct, a.alert_status, a.created_at
        FROM ANOMALY_ALERTS a JOIN DATASETS d ON a.dataset_id = d.dataset_id
        ORDER BY a.created_at DESC
    """, conn)
    st.dataframe(df_alerts, use_container_width=True)
    
    st.subheader("Cursor Audit Sweep Simulator")
    if st.button("Run `cur_daily_quality_audit_sweep` Cursor"):
        alerts_count = db.cur_daily_quality_audit_sweep()
        st.info(f"Cursor sweep complete. Flagged {alerts_count} dataset(s) with health scores < 75%.")

# --- Page 5: 15-Query SQL Runner ---
elif menu == "🔍 15-Query SQL Runner":
    st.title("🔍 15 Course-Required SQL Queries Executor")
    
    queries = {
        "1. Data Retrieval & Sorting (Active Pipelines)": 
            "SELECT pipeline_id, pipeline_name, owner_email, schedule_cron FROM PIPELINES WHERE is_active = 1 ORDER BY pipeline_name ASC;",
            
        "2. INNER JOIN (Pipelines & Datasets)": 
            "SELECT p.pipeline_name, d.table_name, d.target_database, d.row_count FROM PIPELINES p JOIN DATASETS d ON p.dataset_id = d.dataset_id;",
            
        "3. Multi-Table Join across 3 Tables": 
            "SELECT r.run_id, p.pipeline_name, d.table_name, r.status, r.records_processed, r.start_time FROM PIPELINE_RUNS r JOIN PIPELINES p ON r.pipeline_id = p.pipeline_id JOIN DATASETS d ON p.dataset_id = d.dataset_id ORDER BY r.start_time DESC;",
            
        "4. Aggregation & GROUP BY (Run Status Summary)": 
            "SELECT status, COUNT(*) AS total_runs, ROUND(AVG(records_processed), 2) AS avg_records FROM PIPELINE_RUNS GROUP BY status;",
            
        "5. Subquery with Aggregate Comparison": 
            "SELECT table_name, target_database, row_count FROM DATASETS WHERE row_count > (SELECT AVG(row_count) FROM DATASETS);",
            
        "6. LEFT JOIN (Pipelines with Zero Runs)": 
            "SELECT p.pipeline_id, p.pipeline_name, p.owner_email FROM PIPELINES p LEFT JOIN PIPELINE_RUNS r ON p.pipeline_id = r.pipeline_id WHERE r.run_id IS NULL;",
            
        "7. Quality Rule Failure Aggregation": 
            "SELECT qr.rule_type, qr.severity, COUNT(rv.validation_id) AS evaluations_count, SUM(rv.failed_row_count) AS total_failed_rows FROM QUALITY_RULES qr JOIN RULE_VALIDATIONS rv ON qr.rule_id = rv.rule_id GROUP BY qr.rule_type, qr.severity;",
            
        "8. Subquery with IN (Datasets with Open Alerts)": 
            "SELECT dataset_id, table_name, target_database FROM DATASETS WHERE dataset_id IN (SELECT dataset_id FROM ANOMALY_ALERTS WHERE alert_status = 'Open');",
            
        "9. Aggregate Volume Analysis": 
            "SELECT p.pipeline_name, COUNT(r.run_id) AS total_runs, SUM(r.records_processed) AS total_volume FROM PIPELINES p LEFT JOIN PIPELINE_RUNS r ON p.pipeline_id = r.pipeline_id GROUP BY p.pipeline_id, p.pipeline_name;",
            
        "10. Dataset Rule Distribution": 
            "SELECT d.table_name, COUNT(qr.rule_id) AS total_rules FROM DATASETS d LEFT JOIN QUALITY_RULES qr ON d.dataset_id = qr.dataset_id GROUP BY d.dataset_id, d.table_name;",
            
        "11. Common Table Expression (CTE) Success Rates": 
            "WITH PipelineStats AS (SELECT pipeline_id, COUNT(*) AS total_runs, SUM(CASE WHEN status = 'Success' THEN 1 ELSE 0 END) AS successful_runs, SUM(CASE WHEN status = 'Failed' THEN 1 ELSE 0 END) AS failed_runs FROM PIPELINE_RUNS GROUP BY pipeline_id) SELECT p.pipeline_name, ps.total_runs, ps.successful_runs, ps.failed_runs FROM PIPELINES p JOIN PipelineStats ps ON p.pipeline_id = ps.pipeline_id;",
            
        "12. Top 3 Rule Violation Ranking": 
            "SELECT qr.rule_id, qr.column_name, qr.rule_type, SUM(rv.failed_row_count) AS total_failed_rows FROM RULE_VALIDATIONS rv JOIN QUALITY_RULES qr ON rv.rule_id = qr.rule_id WHERE rv.passed = 0 GROUP BY qr.rule_id, qr.column_name, qr.rule_type ORDER BY total_failed_rows DESC LIMIT 3;",
            
        "13. HAVING Clause (Datasets with >= 1 Alerts)": 
            "SELECT d.table_name, COUNT(a.alert_id) AS anomaly_count FROM DATASETS d JOIN ANOMALY_ALERTS a ON d.dataset_id = a.dataset_id GROUP BY d.dataset_id, d.table_name HAVING COUNT(a.alert_id) >= 1;",
            
        "14. Diagnostic Log Audit": 
            "SELECT l.log_id, p.pipeline_name, l.log_level, l.message, l.created_at FROM PIPELINE_LOGS l JOIN PIPELINE_RUNS r ON l.run_id = r.run_id JOIN PIPELINES p ON r.pipeline_id = p.pipeline_id WHERE l.log_level IN ('WARN', 'ERROR', 'CRITICAL') ORDER BY l.created_at DESC;",
            
        "15. Anomaly Variance Analysis": 
            "SELECT d.table_name, a.metric_name, a.expected_value, a.actual_value, a.variance_pct, a.alert_status FROM ANOMALY_ALERTS a JOIN DATASETS d ON a.dataset_id = d.dataset_id ORDER BY a.variance_pct DESC;"
    }
    
    selected_query_title = st.selectbox("Select Query to Execute", list(queries.keys()))
    query_sql = queries[selected_query_title]
    
    st.code(query_sql, language="sql")
    
    if st.button("▶️ Run Selected SQL Query"):
        try:
            res_df = pd.read_sql(query_sql, conn)
            st.success("Query Executed Successfully!")
            st.dataframe(res_df, use_container_width=True)
        except Exception as e:
            st.error(f"Error executing query: {e}")

conn.close()
