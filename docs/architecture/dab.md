# Databricks Asset Bundle (DAB)

Declarative deployment for **ML Operations Intelligence** resources: jobs, notebooks, SQL DDL, and grants under `resources/`.

## Bundle layout

| Path | Purpose |
|------|---------|
| `databricks.yml` | Bundle manifest, variables, targets |
| `resources/*.yml` | Job, pipeline, and other resource definitions |
| `notebooks/` | Notebook sources referenced by jobs (synced via `sync.paths`) |
| `src/mlops_intelligence/` | Python package for wheel tasks (future) |

## Variables

| Variable | Description |
|----------|-------------|
| `catalog` | Unity Catalog name per environment |
| `schema` | Default schema for platform tables |
| `workspace_root` | Workspace deployment root (`${workspace.current_user.userName}`, not bare `current_user`) |

## Targets and Git mapping

| DAB target | Workspace profile | Catalog variable | Git promotion |
|------------|-------------------|------------------|---------------|
| `dev` (default) | `dev` | `mlops_intelligence_dev` | PRs merge to `dev` |
| `staging` | `staging` | `mlops_intelligence_staging` | Promote from `dev` |
| `prod` | `prod` | `mlops_intelligence_prod` | PR `dev` → `main` |

Configure CLI profiles locally (`~/.databrickscfg`); never commit tokens or host secrets.

## Notebook sync

`sync.paths` includes `src/`, `notebooks/`, and `resources/` so bundle deploy uploads application code and notebooks alongside job definitions. Paths in job `notebook_task` must match files under `notebooks/` — see [notebooks/README.md](../../notebooks/README.md).

## Validation

```bash
# Requires Databricks CLI + configured profile (see docs/git-workflow.md)
databricks bundle validate -t dev
databricks bundle validate -t staging
databricks bundle validate -t prod
```

CI will run `bundle validate` in **Epic 2** (SCRUM-122). Until then, `tests/test_databricks_bundle.py` asserts manifest structure in PRs.

## Related stories

- SCRUM-125 — bundle scaffold (this document)
- SCRUM-126 — multi-environment targets
- SCRUM-127 — job resource definitions
- SCRUM-122 — CI validate gate
