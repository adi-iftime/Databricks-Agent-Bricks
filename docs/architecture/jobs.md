# Databricks job resources — ML Operations Intelligence

Core Lakeflow jobs declared in the Asset Bundle under `resources/jobs/`. Tasks are stubs until Epic 5–9 implementation stories wire notebooks and dependencies.

## Job catalog

| Resource key | Job name pattern | Notebook stub | Purpose |
|--------------|------------------|---------------|---------|
| `ingestion` | `[${bundle.target}] mlops ingestion` | `notebooks/ingestion/stub` | Bronze ingestion |
| `ml_observability` | `[${bundle.target}] mlops ml observability` | `notebooks/ml_obs/stub` | ML metrics collection |
| `anomaly_detection` | `[${bundle.target}] mlops anomaly detection` | `notebooks/anomaly/stub` | Anomaly scoring |
| `agent_analysis` | `[${bundle.target}] mlops agent analysis` | `notebooks/agent/stub` | Agent RCA orchestration |

Stub job clusters use `num_workers: 1` with no `custom_tags` or `spark_conf`. The current Databricks CLI fails `bundle validate` with `cannot interpolate non-primitive value of type map into string` when you use any of:

- job-level `tags` (map field coerced into string interpolation)
- `spark_conf` keys containing dots (e.g. `spark.databricks.cluster.profile`)
- `custom_tags: ResourceClass: SingleNode` without the full single-node `spark_conf` pair (triggers the single-node mutator)

Re-enable governance labels and single-node clusters in a follow-up using `type: complex` variables or nested `spark_conf` once validate is green.

## Bundle files

| File | Jobs defined |
|------|--------------|
| `resources/jobs/ingestion.job.yml` | `ingestion` |
| `resources/jobs/ml_observability.job.yml` | `ml_observability` |
| `resources/jobs/anomaly_detection.job.yml` | `anomaly_detection` |
| `resources/jobs/agent_analysis.job.yml` | `agent_analysis` |

## Deploy

```bash
databricks bundle deploy -t dev
```

Requires configured auth ([databricks-auth.md](../cicd/databricks-auth.md) for CI; local profiles for developers).

## Related stories

- SCRUM-127 — job resource definitions (this document)
- SCRUM-126 — environment targets
- Epic 9 — job DAG and task dependencies
