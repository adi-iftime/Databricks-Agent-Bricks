# Example PR description (ML Operations Intelligence)

Use this as a filled-in reference when opening platform PRs. Copy sections into [.github/pull_request_template.md](../../.github/pull_request_template.md).

---

## Summary

Adds Unity Catalog DDL for the `ml_obs` schema and wires the bronze ingestion job into the dev DAB target.

## Branch target

- **Base branch:** `dev`
- **Flow:** [docs/git-workflow.md](../git-workflow.md)

## Jira

- **Story:** SCRUM-XXX — Short title
- Link: https://levi9-team-ivfys2q6.atlassian.net/browse/SCRUM-XXX

## Governance checklist

- [x] Jira key in title and description
- [x] Single story scope
- [x] Tests updated (`tests/test_repo_structure.py` or story-specific tests)
- [x] `OWNERSHIP=resources/` on implementation Task

## Unity Catalog impact

| Object | Change | Environment |
|--------|--------|-------------|
| `mlops_intelligence_dev.ml_obs.events` | CREATE TABLE | dev |
| Grants | `USE CATALOG` for job SP | dev |

**Backward compatibility:** Additive only; no column drops.

## Databricks Asset Bundle

| Item | Detail |
|------|--------|
| Bundle | `mlops_intelligence` |
| Resources touched | `resources/jobs/bronze_ingestion.job.yml` |
| Target | `dev` (validate + deploy in CI after SCRUM-122) |
| Variables | `catalog`, `schema` unchanged |

```bash
databricks bundle validate -t dev
```

## Business context

Operators need bronze event storage before ML observability metrics (Epic 5).

## Technical implementation

- SQL DDL under `resources/sql/ml_obs/`
- Job references notebook `notebooks/ingestion/bronze_events.py`

## Impacted components

- `resources/sql/`, `resources/jobs/`, `notebooks/ingestion/`

## Testing performed

```bash
python3 -m unittest discover -s tests -p "test_*.py" -v
```

## Risks and limitations

- Deploy uses `dev` target only (`databricks bundle deploy -t dev` on merge to `dev`).

## Dependencies

- Requires SCRUM-125 bundle scaffold merged.

## Rollout notes

1. Merge to `dev` → auto-validate (CI).
2. Manual `bundle deploy -t dev` until SCRUM-121 workflow exists.
3. **Rollback:** Revert PR; run `DROP TABLE` only if deploy ran (document in ops runbook).

## Documentation

- [x] Updated `docs/architecture/repo-layout.md` if paths changed
