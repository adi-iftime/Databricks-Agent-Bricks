# Auto-deploy to dev (Databricks)

When changes merge to the **`dev`** branch, [`.github/workflows/databricks-deploy-dev.yml`](../../.github/workflows/databricks-deploy-dev.yml) deploys the Asset Bundle to the **`dev`** DAB target.

## Prerequisites

| Item | Detail |
|------|--------|
| Secrets | `DATABRICKS_HOST`, `DATABRICKS_TOKEN` (repository secrets) |
| Target | `dev` in `databricks.yml` → `mlops_intelligence_dev` catalog |
| CI gates | PRs must pass `databricks-cicd.yml` before merge |

## Flow

```text
PR → dev (merge) → databricks-deploy-dev workflow → bundle validate → bundle deploy -t dev
```

## Deployment log fields

Each run logs:

- `git_sha` — commit deployed
- `ref` — branch ref
- `bundle` — `mlops_intelligence`
- `target` — `dev`

## Rollback

1. Identify last good commit on `dev`.
2. Revert or cherry-pick fix onto `dev` and push (triggers redeploy), **or**
3. Locally: `git checkout <good-sha>` then `databricks bundle deploy -t dev` with the same secrets/profile.

Avoid `bundle deploy --force` unless documented in an incident runbook.

## Related

- [databricks-auth.md](databricks-auth.md)
- [github-actions.md](github-actions.md)
- [promotion.md](promotion.md) (SCRUM-124)
