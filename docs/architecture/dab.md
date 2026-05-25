# Databricks Asset Bundle (DAB)

Declarative deployment for **ML Operations Intelligence** resources: jobs, notebooks, SQL DDL, and grants under `resources/`.

## Bundle layout

| Path | Purpose |
|------|---------|
| `databricks.yml` | Bundle manifest, variables, targets |
| `resources/*.yml` | Job, pipeline, and other resource definitions |
| `notebooks/` | Notebook sources referenced by jobs |
| `src/mlops_intelligence/` | Python package for wheel tasks (future) |

## Variables

| Variable | Description |
|----------|-------------|
| `catalog` | Unity Catalog name per environment |
| `schema` | Default schema for platform tables |
| `workspace_root` | Workspace deployment root for bundle artifacts |

Environment-specific overrides are added in **SCRUM-126** (`dev`, `staging`, `prod` targets).

## Validation

```bash
# Requires Databricks CLI + configured profile (see docs/git-workflow.md)
databricks bundle validate
```

CI will run `bundle validate` in **Epic 2** (SCRUM-122). Until then, `tests/test_databricks_bundle.py` asserts manifest structure in PRs.

## Related stories

- SCRUM-125 — bundle scaffold (this document)
- SCRUM-126 — multi-environment targets
- SCRUM-127 — job resource definitions
- SCRUM-122 — CI validate gate
