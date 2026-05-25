# Audit logging and lineage — ML Operations Intelligence

Unity Catalog tags, table comments, and audit query patterns for compliance and agent observability.

## Tagged objects

Apply [`resources/sql/03_audit_lineage_tags.sql`](../../resources/sql/03_audit_lineage_tags.sql) after catalog, table DDL, and RBAC grants.

| Object | Tags |
|--------|------|
| `bronze_ops.pipeline_runs` | `project`, `domain=pipeline`, `layer=bronze`, `data_classification=operational` |
| `bronze_ops.system_metrics` | `project`, `domain=infrastructure`, `layer=bronze` |
| `bronze_ops.model_metrics` | `project`, `domain=model`, `layer=bronze` |
| `bronze_ops.feature_store_metrics` | `project`, `domain=feature_store`, `layer=bronze` |
| Schemas `bronze_ops`, `silver_ops`, `gold_ops` | `project`, `layer` |

Table-level `COMMENT` clauses are defined in `01_telemetry_tables.sql` and `02_ml_metrics_tables.sql`.

## Verify tags (dev)

```sql
SELECT catalog_name, schema_name, table_name, tag_name, tag_value
FROM system.information_schema.table_tags
WHERE catalog_name = 'mlops_intelligence_dev'
ORDER BY schema_name, table_name, tag_name;
```

Or in the UC UI: **Catalog Explorer → table → Tags**.

## Lineage

After ingestion jobs write to bronze tables, UC **Lineage** shows upstream Jobs/notebooks and downstream gold models (when present). Key tables for agent RCA:

- `bronze_ops.pipeline_runs` — job failure and cost attribution
- `bronze_ops.model_metrics` — model performance drift

Document notebook/job names in bundle resources so lineage graphs stay connected.

## Audit queries — agent service principal

Use the workspace audit log table (requires audit log delivery enabled):

```sql
SELECT
  event_time,
  user_identity.email AS principal,
  action_name,
  request_params,
  response.status_code
FROM system.access.audit
WHERE user_identity.email LIKE '%mlops-agent-sp%'
  AND event_date >= current_date() - INTERVAL 7 DAYS
ORDER BY event_time DESC
LIMIT 500;
```

### Runbook checklist

1. Confirm audit log delivery to `system.access.audit` in the workspace.
2. Run the query weekly or on security incident; export to SIEM in Epic 10.
3. Alert on denied actions (`response.status_code = 403`) for agent SP.
4. Correlate with application logs using `correlation_id` from ingestion jobs.

## Ingestion SP audit

Same pattern with `mlops-ingestion-sp` — focus on `createTable`, `modifyTable`, and `runJob` actions.

## Limitations (this story)

- No full SIEM integration or automated alerting.
- Audit coverage depends on workspace audit log configuration.
- Pair with [UC RBAC](./uc-rbac.md) before production data.

## Related

- [Unity Catalog layout](../data/unity-catalog.md)
- [Pipeline run ingestion](../pipelines/ingestion-pipeline-runs.md)
