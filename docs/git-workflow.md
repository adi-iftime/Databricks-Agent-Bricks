# Git workflow — ML Operations Intelligence

Branching model for **Databricks-Agent-Bricks**. Databricks deployment uses the single **`dev`** bundle target only.

## Branches

| Branch | Role | DAB target | Merge policy |
|--------|------|------------|--------------|
| `dev` | Integration; auto-deploy workspace | `dev` | Protected; PR from `feature/*`; required CI |
| `main` | Release / template baseline (optional) | — | Protected; no Databricks deploy from this repo |
| `feature/<JIRA-KEY>-<slug>` | Single Jira story work | — (validate on PR) | Short-lived; PR → `dev` |

## Flow

```text
feature/SCRUM-XXX-*  ──PR──►  dev  ──►  bundle deploy -t dev (on merge)
```

### Feature branches

- One Jira story per branch and per PR ([one-story-per-pr](../.cursor/rules/one-story-per-pr.mdc)).
- Naming: `feature/SCRUM-115-dab-monorepo-layout` (key + short slug).
- Base branch for new work: **`dev`**.

### Integration (`dev`)

- Default target for implementation PRs.
- Must pass CI (`cursor-framework-ci` and `databricks-cicd` including `bundle-validate`).
- Merge to `dev` triggers [databricks-deploy-dev.yml](../.github/workflows/databricks-deploy-dev.yml).

## Hotfix (exception path)

1. Branch from `dev`: `feature/SCRUM-XXX-hotfix-<slug>`.
2. PR to `dev` with explicit **hotfix** label and rollback plan in PR body.

Document hotfix in Jira; do not bypass protection without approval.

## Branch protection (GitHub)

Configure in **Settings → Branches** (repository admin). Recommended rules for **`dev`**:

- Require pull request before merging
- Require status checks: `hooks-and-policies`, `bundle-validate`, `unit-test`, `databricks-auth`
- Restrict who can push
- Do not allow force push

Use [branch-protection-checklist.md](architecture/branch-protection-checklist.md) when applying settings.

## DAB target mapping

| Git branch | Bundle target | Notes |
|------------|---------------|--------|
| `dev` | `dev` | Auto-deploy on merge (SCRUM-123) |

Details in [dab.md](architecture/dab.md).

## Related docs

- [repo-layout.md](architecture/repo-layout.md) — directory structure
- [CONTRIBUTING.md](../CONTRIBUTING.md) — PR and Jira traceability
- [deploy-dev.md](cicd/deploy-dev.md) — CI deploy workflow
