# Pipeline run telemetry ingestion

Ingests Databricks Jobs API run metadata into the Unity Catalog `pipeline_runs` bronze table (SCRUM-135).

## Module

[`src/mlops_intelligence/ingestion/pipeline_runs.py`](../../src/mlops_intelligence/ingestion/pipeline_runs.py)

## Target table

`{catalog}.bronze_ops.pipeline_runs` — dev default: `mlops_intelligence_dev.bronze_ops.pipeline_runs`

Schema contract: [`resources/schema/pipeline_runs.yaml`](../../resources/schema/pipeline_runs.yaml)

## Behavior

1. **Fetch** — `POST /api/2.1/jobs/runs/list` with pagination (`next_page_token`).
2. **Transform** — Map API run objects to contract columns (`run_id`, `job_id`, `status`, `duration_sec`, `cost_usd`, `event_ts`, `ingested_at`).
3. **Load** — Delta `MERGE` keyed on `run_id` (idempotent reruns update existing rows).

Status mapping:

| API state | `pipeline_runs.status` |
|-----------|--------------------------|
| `result_state=SUCCESS` | `SUCCESS` |
| `result_state=FAILED` / `TIMEDOUT` | `FAILED` |
| `result_state=CANCELED` / `SKIPPED` | `CANCELLED` |
| `life_cycle_state=RUNNING` (and pending variants) | `RUNNING` |

## Configuration

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DATABRICKS_HOST` | Yes | — | Workspace URL (no trailing slash) |
| `DATABRICKS_TOKEN` | No* | — | PAT or OAuth token for API calls |
| `PIPELINE_RUNS_TABLE` | No | `mlops_intelligence_dev.bronze_ops.pipeline_runs` | Fully qualified Delta table |
| `DATABRICKS_API_PAGE_SIZE` | No | `25` | Runs per API page |
| `DATABRICKS_API_MAX_RETRIES` | No | `3` | Retries on 429/5xx and network errors |
| `DATABRICKS_API_TIMEOUT_SEC` | No | `30` | HTTP timeout |

\* On Databricks, prefer cluster/job identity or secret scope instead of embedding tokens in notebooks.

## Usage (notebook or job)

```python
from mlops_intelligence.ingestion.pipeline_runs import ingest_pipeline_runs

# spark session provided by Databricks runtime
merged = ingest_pipeline_runs(spark, job_id=None, correlation_id="scheduled-ingestion")
```

Pass an optional `job_id` to scope ingestion to a single job.

## Observability

- Structured logs include `correlation_id` on every ingestion step (fetch, merge, completion).
- Pagination logs `run_count` and `has_more` per page.
- Retries log attempt number, delay, and error class.

## Idempotency

Re-running ingestion for the same `run_id` executes `MERGE … WHEN MATCHED THEN UPDATE` — no duplicate rows.

## Tests

[`tests/test_pipeline_runs_ingestion.py`](../../tests/test_pipeline_runs_ingestion.py) uses fixture JSON under `tests/fixtures/` (no network).

```bash
python3 -m unittest discover -s tests -p "test_*.py" -v
```

## Related

- Table DDL: [`resources/sql/01_telemetry_tables.sql`](../../resources/sql/01_telemetry_tables.sql)
- DAB job stub: [`resources/jobs/ingestion.job.yml`](../../resources/jobs/ingestion.job.yml)
