# Unity Catalog — ML Operations Intelligence

Governed storage for pipeline telemetry, system metrics, anomaly features, and agent context.

## Catalog naming

| DAB target | Git branch flow | Catalog name |
|------------|-----------------|--------------|
| `dev` | `feature/*` → `dev` | `mlops_intelligence_dev` |

Catalog name aligns with the `dev` target in [`databricks.yml`](../../databricks.yml).

## Schema layout

| Schema | Layer | Purpose |
|--------|-------|---------|
| `bronze_ops` | Bronze | Raw/near-raw operational events |
| `silver_ops` | Silver | Curated metrics and joins |
| `gold_ops` | Gold | Aggregates for agent RCA and BI |

## DDL

Initial catalog and schemas: [`resources/sql/00_catalog.sql`](../../resources/sql/00_catalog.sql).

Telemetry and ML observability tables:

| SQL file | Tables |
|----------|--------|
| [`01_telemetry_tables.sql`](../../resources/sql/01_telemetry_tables.sql) | `pipeline_runs`, `system_metrics` |
| [`02_ml_metrics_tables.sql`](../../resources/sql/02_ml_metrics_tables.sql) | `model_metrics`, `feature_store_metrics` |

Apply via SQL warehouse or bundle SQL task. Run `00_catalog.sql` first, then numbered table files in order.

## Security

- No broad `PUBLIC` read on `silver_ops` / `gold_ops`
- Audit and lineage tags: [`docs/security/audit-lineage.md`](../security/audit-lineage.md) and [`resources/sql/03_audit_lineage_tags.sql`](../../resources/sql/03_audit_lineage_tags.sql) (SCRUM-134)
- RBAC grants: Epic 10 / SCRUM-133
- Secrets never stored in SQL files

## Related stories

- SCRUM-130 — catalog + schemas (this document)
- SCRUM-131 — `pipeline_runs`, `system_metrics` tables
- SCRUM-132 — `model_metrics`, `feature_store_metrics` tables
