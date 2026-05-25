# Unity Catalog — ML Operations Intelligence

Governed storage for pipeline telemetry, system metrics, anomaly features, and agent context.

## Catalog naming

| DAB target | Git branch flow | Catalog name |
|------------|-----------------|--------------|
| `dev` | `feature/*` → `dev` | `mlops_intelligence_dev` |
| `staging` | `dev` → staging promote | `mlops_intelligence_staging` |
| `prod` | `dev` → `main` | `mlops_intelligence_prod` |

Catalog names align with [`databricks.yml`](../../databricks.yml) target variables (SCRUM-126).

## Schema layout

| Schema | Layer | Purpose |
|--------|-------|---------|
| `bronze_ops` | Bronze | Raw/near-raw operational events |
| `silver_ops` | Silver | Curated metrics and joins |
| `gold_ops` | Gold | Aggregates for agent RCA and BI |

## DDL

Initial catalog and schemas: [`resources/sql/00_catalog.sql`](../../resources/sql/00_catalog.sql).

Deploy via SQL warehouse or bundle SQL task (SCRUM-127+). When applying manually, substitute the catalog prefix for the target environment.

## Security

- No broad `PUBLIC` read on `silver_ops` / `gold_ops`
- Grants and service principals: Epic 10 (SCRUM-163+)
- Secrets never stored in SQL files

## Related stories

- SCRUM-130 — catalog + schemas (this document)
- SCRUM-131 — `pipeline_runs`, `system_metrics` tables
- SCRUM-126 — per-environment catalog variables
