# `pipeline_runs`

Bronze Delta table for pipeline execution telemetry.

## Location

`{catalog}.bronze_ops.pipeline_runs` — dev example: `mlops_intelligence_dev.bronze_ops.pipeline_runs`

## Schema contract

[`resources/schema/pipeline_runs.yaml`](../../resources/schema/pipeline_runs.yaml)

## Columns

| Column | Type | Description |
|--------|------|-------------|
| `run_id` | STRING | Unique run identifier |
| `job_id` | STRING | Job name or id |
| `status` | STRING | Run status |
| `duration_sec` | DOUBLE | Duration in seconds |
| `cost_usd` | DOUBLE | Estimated cost |
| `event_ts` | TIMESTAMP | Event time (partition key) |
| `ingested_at` | TIMESTAMP | Ingestion timestamp |

## DDL

[`resources/sql/01_telemetry_tables.sql`](../../resources/sql/01_telemetry_tables.sql)
