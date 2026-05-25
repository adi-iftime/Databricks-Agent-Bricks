# `system_metrics`

Bronze Delta table for infrastructure and system metrics.

## Location

`{catalog}.bronze_ops.system_metrics` — dev example: `mlops_intelligence_dev.bronze_ops.system_metrics`

## Schema contract

[`resources/schema/system_metrics.yaml`](../../resources/schema/system_metrics.yaml)

## Columns

| Column | Type | Description |
|--------|------|-------------|
| `metric_name` | STRING | Metric identifier |
| `metric_value` | DOUBLE | Observed value |
| `host` | STRING | Source host or cluster |
| `event_ts` | TIMESTAMP | Observation time (partition key) |
| `tags` | MAP<STRING,STRING> | Dimensions |
| `ingested_at` | TIMESTAMP | Ingestion timestamp |

## DDL

[`resources/sql/01_telemetry_tables.sql`](../../resources/sql/01_telemetry_tables.sql)
