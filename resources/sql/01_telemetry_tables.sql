-- Telemetry tables for ML Operations Intelligence (SCRUM-131)
-- Catalog: mlops_intelligence_dev (substitute per DAB target)

CREATE TABLE IF NOT EXISTS mlops_intelligence_dev.bronze_ops.pipeline_runs (
  run_id STRING NOT NULL COMMENT 'Unique pipeline run identifier',
  job_id STRING COMMENT 'Databricks job id or name',
  status STRING NOT NULL COMMENT 'SUCCESS | FAILED | RUNNING | CANCELLED',
  duration_sec DOUBLE COMMENT 'Wall-clock duration in seconds',
  cost_usd DOUBLE COMMENT 'Estimated run cost in USD',
  event_ts TIMESTAMP NOT NULL COMMENT 'Run start or event timestamp',
  ingested_at TIMESTAMP NOT NULL DEFAULT current_timestamp() COMMENT 'Ingestion timestamp'
)
USING DELTA
PARTITIONED BY (DATE(event_ts))
TBLPROPERTIES (
  'delta.autoOptimize.optimizeWrite' = 'true',
  'delta.autoOptimize.autoCompact' = 'true',
  'quality' = 'bronze',
  'project' = 'mlops_intelligence'
)
COMMENT 'Pipeline execution telemetry for anomaly detection and agent RCA';

CREATE TABLE IF NOT EXISTS mlops_intelligence_dev.bronze_ops.system_metrics (
  metric_name STRING NOT NULL COMMENT 'Metric identifier',
  metric_value DOUBLE NOT NULL COMMENT 'Observed value',
  host STRING COMMENT 'Source host or cluster id',
  event_ts TIMESTAMP NOT NULL COMMENT 'Observation timestamp',
  tags MAP<STRING, STRING> COMMENT 'Optional dimensions',
  ingested_at TIMESTAMP NOT NULL DEFAULT current_timestamp() COMMENT 'Ingestion timestamp'
)
USING DELTA
PARTITIONED BY (DATE(event_ts))
TBLPROPERTIES (
  'delta.autoOptimize.optimizeWrite' = 'true',
  'delta.autoOptimize.autoCompact' = 'true',
  'quality' = 'bronze',
  'project' = 'mlops_intelligence'
)
COMMENT 'Infrastructure and system metrics for operational intelligence';
