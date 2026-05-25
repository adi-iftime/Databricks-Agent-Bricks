# Repository layout

This repository is the **GitHub single source of truth** for the ML Operations Intelligence platform on Databricks. It combines:

1. **Cursor AI SDLC framework** (`.cursor/`) — agents, rules, skills, hooks, orchestration
2. **Production ML ops platform** — DAB bundle, Python package, notebooks, Unity Catalog assets

## Top-level directories

| Path | Purpose |
|------|---------|
| `.cursor/` | Agent orchestration framework (do not remove for platform work) |
| `src/mlops_intelligence/` | Python application code (ingestion, anomaly, agent, governance) |
| `notebooks/` | Databricks notebooks deployed via bundle |
| `resources/` | DAB resources: jobs, SQL DDL, grants |
| `tests/` | Unit tests (hooks today; platform tests added per story) |
| `docs/` | Architecture and runbooks |
| `databricks.yml` | Asset Bundle root manifest |
| `.github/workflows/` | CI/CD (framework today; Databricks deploy in Epic 2) |

## DAB alignment

Deployment follows [Databricks Asset Bundles](https://docs.databricks.com/dev-tools/bundles/index.html):

- `databricks bundle validate` / `deploy` from repo root
- Environment targets: `dev`, `staging`, `prod` (SCRUM-126)
- Jobs and notebooks referenced from `resources/` and `notebooks/`

## Framework vs application boundaries

| Concern | Location | Owned by |
|---------|----------|----------|
| Agent orchestration, Jira workflow | `.cursor/` | Framework template |
| Data pipelines, agent runtime | `src/`, `notebooks/`, `resources/` | ML ops platform stories |
| Hook/policy CI | `tests/test_hook_policies.py`, `cursor-framework-ci.yml` | Must keep passing on every PR |
| Repo layout CI | `tests/test_repo_structure.py` (dedicated workflow step) | Fails PR if scaffold paths missing (SCRUM-119) |

## Evolution from template

The repo started as **Databricks-Agent-Bricks** (Cursor template). Platform stories (SCRUM-103+) add production paths without deleting orchestration assets. Each PR maps to one Jira story and one ownership lane (`OWNERSHIP=` in Task prompts).

## Git workflow

Branching (`main` / `dev` / `feature/*`) and protection rules: [docs/git-workflow.md](../git-workflow.md).

## Ownership

Parallel agent lanes: [`.github/CODEOWNERS`](../../.github/CODEOWNERS) and [CONTRIBUTING.md](../../CONTRIBUTING.md#ownership-lanes-codeowners).

## CI validation

[`.github/workflows/cursor-framework-ci.yml`](../../.github/workflows/cursor-framework-ci.yml) runs on pull requests and pushes to `main`, `master`, and `dev`. The **Repository layout validation** step executes `tests/test_repo_structure.py` so missing scaffold directories fail before merge.

## Related Jira epics

- Epic 1 (SCRUM-103): GitHub structure — this document
- Epic 2 (SCRUM-104): GitHub Actions → Databricks deploy
- Epic 3 (SCRUM-105): DAB targets and jobs
- Epic 4 (SCRUM-106): Unity Catalog schemas under `resources/sql/`
