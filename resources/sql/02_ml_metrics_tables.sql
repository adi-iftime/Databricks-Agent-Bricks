-- ML observability tables (SCRUM-132)
-- Catalog: mlops_intelligence_dev (dev target)

CREATE TABLE IF NOT EXISTS mlops_intelligence_dev.bronze_ops.model_metrics (
  model_name STRING NOT NULL COMMENT 'MLflow registered model name',
  model_version STRING NOT NULL COMMENT 'MLflow model version',
  metric_name STRING NOT NULL COMMENT 'Canonical metric name (e.g. accuracy, latency_p99)',
  metric_value DOUBLE NOT NULL COMMENT 'Metric value at observation time',
  event_ts TIMESTAMP NOT NULL COMMENT 'Metric observation timestamp',
  ingested_at TIMESTAMP NOT NULL DEFAULT current_timestamp() COMMENT 'Ingestion timestamp'
)
USING DELTA
PARTITIONED BY (DATE(event_ts))
TBLPROPERTIES (
  'delta.autoOptimize.optimizeWrite' = 'true',
  'delta.autoOptimize.autoCompact' = 'true',
  'quality' = 'bronze',
  'project' = 'mlops_intelligence',
  'domain' = 'model'
)
COMMENT 'Model performance metrics keyed by MLflow model name and version';

CREATE TABLE IF NOT EXISTS mlops_intelligence_dev.bronze_ops.feature_store_metrics (
  feature_set STRING NOT NULL COMMENT 'Feature table or feature view name',
  freshness_lag_sec DOUBLE COMMENT 'Seconds since last feature update',
  null_rate DOUBLE COMMENT 'Fraction of null values in monitored column(s)',
  event_ts TIMESTAMP NOT NULL COMMENT 'Observation timestamp',
  ingested_at TIMESTAMP NOT NULL DEFAULT current_timestamp() COMMENT 'Ingestion timestamp'
)
USING DELTA
PARTITIONED BY (DATE(event_ts))
TBLPROPERTIES (
  'delta.autoOptimize.optimizeWrite' = 'true',
  'delta.autoOptimize.autoCompact' = 'true',
  'quality' = 'bronze',
  'project' = 'mlops_intelligence',
  'domain' = 'feature_store'
)
COMMENT 'Feature store health metrics for drift and freshness monitoring';
