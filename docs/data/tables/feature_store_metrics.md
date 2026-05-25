# `feature_store_metrics`

Bronze Delta table for feature store freshness and quality signals.

## Location

`{catalog}.bronze_ops.feature_store_metrics` — dev: `mlops_intelligence_dev.bronze_ops.feature_store_metrics`

## Schema contract

[`resources/schema/feature_store_metrics.yaml`](../../resources/schema/feature_store_metrics.yaml)

## Columns

| Column | Type | Description |
|--------|------|-------------|
| `feature_set` | STRING | Feature table or feature view name |
| `freshness_lag_sec` | DOUBLE | Seconds since last feature update |
| `null_rate` | DOUBLE | Null fraction for monitored columns (0–1) |
| `event_ts` | TIMESTAMP | Observation time (partition key) |
| `ingested_at` | TIMESTAMP | Ingestion timestamp |

## DDL

[`resources/sql/02_ml_metrics_tables.sql`](../../resources/sql/02_ml_metrics_tables.sql)
