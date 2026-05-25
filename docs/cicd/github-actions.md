# GitHub Actions — Databricks CI/CD

ML Operations Intelligence delivery runs through [`.github/workflows/databricks-cicd.yml`](../../.github/workflows/databricks-cicd.yml).

## Triggers

| Event | Branches |
|-------|----------|
| `pull_request` | `dev`, `main`, `master` |
| `push` | `dev`, `main`, `master` |
| `workflow_dispatch` | Manual smoke runs |

## Jobs

| Job | Purpose |
|-----|---------|
| `setup` | Checkout and install Python dev dependencies |
| `lint` | `ruff check .cursor/hooks` |
| `unit-test` | `unittest` under `tests/` |
| `bundle-validate` | Manifest tests + `databricks bundle validate -t dev` |
| `databricks-auth` | `databricks current-user me` using `DATABRICKS_HOST` + `DATABRICKS_TOKEN` repo secrets |
| `deploy` | Disabled here; dev auto-deploy in [databricks-deploy-dev.yml](../../.github/workflows/databricks-deploy-dev.yml) |

## Authentication

Repository secrets **`DATABRICKS_HOST`** and **`DATABRICKS_TOKEN`** — see [databricks-auth.md](databricks-auth.md).

## Concurrency

One run per branch ref (`databricks-cicd-<ref>`); newer runs cancel in-progress jobs on the same ref.

## Related stories

- SCRUM-120 — this workflow scaffold
- SCRUM-121 — Databricks SP / OIDC auth in GHA
- SCRUM-122 — `databricks bundle validate` in CI
- SCRUM-119 — layout validation in `cursor-framework-ci.yml`

## Framework CI

Hook and orchestration policies continue in [`cursor-framework-ci.yml`](../../.github/workflows/cursor-framework-ci.yml). Both workflows run on platform PRs.
