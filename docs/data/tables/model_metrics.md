# `model_metrics`

Bronze Delta table for ML model performance metrics (MLflow-aligned naming).

## Location

`{catalog}.bronze_ops.model_metrics` — dev: `mlops_intelligence_dev.bronze_ops.model_metrics`

## Schema contract

[`resources/schema/model_metrics.yaml`](../../resources/schema/model_metrics.yaml)

## MLflow naming conventions

| Column | MLflow source |
|--------|----------------|
| `model_name` | Registered model name in Unity Catalog / MLflow (`models:/<name>`) |
| `model_version` | Model version string from registry (e.g. `3`, `Staging`, `Production`) |

Ingestion jobs should use the **same** `model_name` as the UC registered model so agent RCA can join to registry metadata.

## Canonical metric names

Use stable, lowercase snake_case identifiers:

| `metric_name` | Meaning |
|---------------|---------|
| `accuracy` | Classification accuracy |
| `f1` | F1 score |
| `latency_p50` / `latency_p99` | Serving latency percentiles (ms) |
| `request_count` | Inference request volume |

Document new metrics in the ingestion job before writing rows.

## Columns

| Column | Type | Description |
|--------|------|-------------|
| `model_name` | STRING | MLflow registered model name |
| `model_version` | STRING | Model version |
| `metric_name` | STRING | Canonical metric identifier |
| `metric_value` | DOUBLE | Observed value |
| `event_ts` | TIMESTAMP | Observation time (partition key) |
| `ingested_at` | TIMESTAMP | Ingestion timestamp |

## DDL

[`resources/sql/02_ml_metrics_tables.sql`](../../resources/sql/02_ml_metrics_tables.sql)
