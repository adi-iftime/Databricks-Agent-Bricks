# Git workflow — ML Operations Intelligence

Branching and promotion model for **Databricks-Agent-Bricks**, aligned with Databricks Asset Bundle (DAB) targets (SCRUM-126).

## Branches

| Branch | Role | DAB target (when configured) | Merge policy |
|--------|------|------------------------------|--------------|
| `main` | Production source of truth | `prod` | Protected; PR from `dev` only; required reviews + CI |
| `dev` | Integration / staging integration | `dev` (auto-deploy in Epic 2) | Protected; PR from `feature/*`; required CI |
| `feature/<JIRA-KEY>-<slug>` | Single Jira story work | — (validate only on PR) | Short-lived; PR → `dev` |

## Flow

```text
feature/SCRUM-XXX-*  ──PR──►  dev  ──PR (approval)──►  main
                              │                        │
                              ▼                        ▼
                         deploy -t dev            deploy -t prod
                         (Epic 2 GHA)            (manual dispatch)
```

### Feature branches

- One Jira story per branch and per PR ([one-story-per-pr](../.cursor/rules/one-story-per-pr.mdc)).
- Naming: `feature/SCRUM-115-dab-monorepo-layout` (key + short slug).
- Base branch for new work: **`dev`** (after `dev` exists); hotfixes from `main` documented below.

### Integration (`dev`)

- Default target for agent implementation PRs.
- Must pass CI (`cursor-framework-ci` and future Databricks bundle validate).
- Orchestrator unlocks dependent stories after PR verification gate passes.

### Production (`main`)

- Reflects production-deployed bundle state.
- Promotion: merge `dev` → `main` via PR with human approval (and staging validation when Epic 2 adds `staging`).

## Hotfix (exception path)

1. Branch from `main`: `feature/SCRUM-XXX-hotfix-<slug>`.
2. PR directly to `main` with explicit **hotfix** label and rollback plan in PR body.
3. Back-merge `main` → `dev` immediately after merge to avoid drift.

Document hotfix in Jira; do not bypass protection without approval.

## Branch protection (GitHub)

Configure in **Settings → Branches** (repository admin). Recommended rules:

### `main`

- Require pull request before merging
- Require status checks: `hooks-and-policies` (and future `bundle-validate`, `repo-structure`)
- Require at least 1 approval
- Restrict who can push (no direct pushes)
- Do not allow force push

### `dev`

- Require pull request before merging
- Require status checks: `hooks-and-policies` (and future checks)
- Restrict who can push
- Do not allow force push

Use [branch-protection-checklist.md](architecture/branch-protection-checklist.md) when applying settings.

## DAB target mapping (reference)

| Git branch | Bundle target | Notes |
|------------|---------------|--------|
| `dev` | `dev` | Auto-deploy on merge (SCRUM-123) |
| `main` | `staging` / `prod` | Manual `workflow_dispatch` promotion (SCRUM-124) |

Details in `docs/architecture/dab.md` (SCRUM-125+).

## Related docs

- [repo-layout.md](architecture/repo-layout.md) — directory structure
- [CONTRIBUTING.md](../CONTRIBUTING.md) — PR and Jira traceability
