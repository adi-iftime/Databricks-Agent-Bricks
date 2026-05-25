# Notebooks

Deployable Databricks notebooks synced by the Asset Bundle (`databricks.yml` → `sync.paths`).

## Layout

| Directory | Purpose | Referenced by job |
|-----------|---------|-------------------|
| `ingestion/` | Bronze / raw ingestion stubs | `ingestion` |
| `ml_obs/` | ML observability metrics | `ml_observability` |
| `anomaly/` | Anomaly detection | `anomaly_detection` |
| `agent/` | Agent RCA orchestration | `agent_analysis` |

## Workspace paths

After `databricks bundle deploy -t <target>`, notebooks appear under the bundle sync root in the workspace (see `${workspace_root}` in [dab.md](../docs/architecture/dab.md)).

Job `notebook_task.notebook_path` values are relative to each `resources/jobs/*.job.yml` file (`../../notebooks/<domain>/stub.py`). The CLI requires a file extension (`.py`, `.sql`, `.ipynb`, etc.).

## Adding notebooks

1. Place `.py` or `.ipynb` under the domain folder.
2. Update the matching job resource in `resources/jobs/`.
3. Run `databricks bundle validate -t dev` before opening a PR.
