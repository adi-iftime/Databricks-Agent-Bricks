# Manual promotion — staging and prod

Gated deploys to higher environments use [`.github/workflows/databricks-deploy-promotion.yml`](../../.github/workflows/databricks-deploy-promotion.yml) (**SCRUM-124**).

## When to use

| Trigger | Workflow | Target |
|---------|----------|--------|
| Merge to `dev` | [databricks-deploy-dev.yml](../../.github/workflows/databricks-deploy-dev.yml) | `dev` (automatic) |
| Manual promotion | [databricks-deploy-promotion.yml](../../.github/workflows/databricks-deploy-promotion.yml) | `staging` or `prod` |

## Dispatch inputs

| Input | Values | Notes |
|-------|--------|--------|
| `target` | `staging`, `prod` | Maps to DAB targets in `databricks.yml` |
| `git_ref` | branch or tag (default `main`) | **Prod** must be `main` (or `master`) |

Run from **Actions → Databricks deploy (promotion) → Run workflow**.

## Approval matrix

| Target | GitHub environment | Required reviewers | Typical `git_ref` |
|--------|-------------------|--------------------|-------------------|
| `staging` | `staging` | Platform / ML ops (configure in repo settings) | `main` after `dev` → `main` PR |
| `prod` | `prod` | Release manager + platform (configure in repo settings) | `main` only |

Configure **Settings → Environments → staging / prod** with protection rules and environment-scoped secrets (`DATABRICKS_HOST`, `DATABRICKS_TOKEN`) for each workspace.

## Flow

```text
dev validated on merge → PR dev → main → workflow_dispatch (staging) → optional prod dispatch
```

Each promotion run:

1. Validates inputs (`prod` + non-`main` ref is rejected)
2. Checks out `git_ref`
3. `databricks bundle validate -t <target>`
4. `databricks bundle deploy -t <target>`

## Audit trail

- **GitHub:** workflow run history, step summary (target, ref, SHA, actor, run URL)
- **Jira:** add a comment on the release or Epic ticket, for example:

```text
Promoted mlops_intelligence to <target> via GHA run <url> (git_ref=main, sha=<sha>, actor=<user>)
```

## Rollback

1. Identify last good commit on `main`.
2. Re-dispatch promotion with the same target and a known-good `git_ref`/tag, **or**
3. Local rollback: checkout good SHA and `databricks bundle deploy -t <target>` with the target profile.

Document incidents in Jira; avoid undocumented `--force` deploys.

## Related

- [deploy-dev.md](deploy-dev.md) — auto dev deploy
- [databricks-auth.md](databricks-auth.md) — secrets and profiles
- [git-workflow.md](../git-workflow.md) — branch promotion model
