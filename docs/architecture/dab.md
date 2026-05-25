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
| `catalog` | Unity Catalog name (`mlops_intelligence_dev` on dev target) |
| `schema` | Default schema for platform tables |
| `workspace_root` | Workspace deployment root (`${workspace.current_user.userName}`, not bare `current_user`) |

## Target

This project deploys to a single Databricks workspace via the **`dev`** target:

| DAB target | Workspace profile | Catalog variable | Git branch |
|------------|-------------------|------------------|------------|
| `dev` (default) | `dev` | `mlops_intelligence_dev` | PRs merge to `dev` |

Configure the CLI profile locally (`~/.databrickscfg` profile `dev`); never commit tokens or host secrets.

## Notebook sync

`sync.paths` includes `src/`, `notebooks/`, and `resources/` so bundle deploy uploads application code and notebooks alongside job definitions. Paths in job `notebook_task` must match files under `notebooks/` — see [notebooks/README.md](../../notebooks/README.md).

## Validation and deploy

```bash
databricks bundle validate -t dev
databricks bundle deploy -t dev
```

CI runs `databricks bundle validate -t dev` on every PR via [databricks-cicd.yml](../../.github/workflows/databricks-cicd.yml) (SCRUM-122). Pushes to `dev` deploy via [databricks-deploy-dev.yml](../../.github/workflows/databricks-deploy-dev.yml) (SCRUM-123).

## Related stories

- SCRUM-125 — bundle scaffold (this document)
- SCRUM-127 — job resource definitions
- SCRUM-122 — CI validate gate
- SCRUM-123 — auto deploy to dev
