# Unity Catalog RBAC — ML Operations Intelligence

Dev catalog `mlops_intelligence_dev` uses **least-privilege service principals** so ingestion and agent workloads cannot be separated.

## Service principals

| Principal | Purpose | Write | Read |
|-----------|---------|-------|------|
| `mlops-ingestion-sp` | Jobs API → Delta MERGE into bronze/silver | `bronze_ops`, `silver_ops` | Same schemas only |
| `mlops-agent-sp` | Agent tools / RCA queries | None | `gold_ops` only |
| `mlops-cicd-sp` (optional) | Bundle deploy + DDL in dev | Catalog DDL (scoped) | Metadata |

Create principals in **Workspace admin → Identity → Service principals** before applying grants.

## Grant matrix (dev)

| Object | Ingestion SP | Agent SP |
|--------|--------------|----------|
| Catalog `mlops_intelligence_dev` | USE | USE |
| Schema `bronze_ops` | USE, MODIFY | — |
| Schema `silver_ops` | USE, MODIFY | — |
| Schema `gold_ops` | — | USE, SELECT |
| `bronze_ops.pipeline_runs` | MODIFY | — |
| `bronze_ops.system_metrics` | MODIFY | — |
| `bronze_ops.model_metrics` | MODIFY | — |
| `bronze_ops.feature_store_metrics` | MODIFY | — |
| Gold tables (future) | — | SELECT |

**MODIFY** on Delta tables covers INSERT, UPDATE, DELETE, and MERGE — sufficient for ingestion jobs.

## SQL assets

Apply after catalog and table DDL:

```text
resources/sql/00_catalog.sql
resources/sql/01_telemetry_tables.sql
resources/sql/02_ml_metrics_tables.sql
resources/grants/00_dev_grants.sql   ← this story
```

## Negative tests (workspace)

Run as each SP (OAuth or token exchange):

1. **Ingestion SP** — `INSERT INTO mlops_intelligence_dev.bronze_ops.pipeline_runs …` → **allowed**
2. **Ingestion SP** — `SELECT * FROM mlops_intelligence_dev.gold_ops.<table>` → **denied** (no USE on gold)
3. **Agent SP** — `SELECT * FROM mlops_intelligence_dev.gold_ops.<table>` → **allowed** (when tables exist)
4. **Agent SP** — `INSERT INTO mlops_intelligence_dev.bronze_ops.pipeline_runs …` → **denied**

Use `SHOW GRANTS ON TABLE mlops_intelligence_dev.bronze_ops.pipeline_runs` to verify effective privileges.

## Production notes

- Do not reuse dev principals in staging/prod.
- Pair with audit tags ([audit-lineage.md](./audit-lineage.md)) and CI SP/OIDC (Epic 10).
- Review grant SQL in security review before promoting data with PII.

## Related

- [Unity Catalog layout](../data/unity-catalog.md)
- [Databricks auth (CI)](../cicd/databricks-auth.md)
