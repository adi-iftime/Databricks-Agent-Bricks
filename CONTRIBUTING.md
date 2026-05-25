# Contributing

This repository hosts the **ML Operations Intelligence** platform and the **Cursor AI SDLC** framework. See [docs/architecture/repo-layout.md](docs/architecture/repo-layout.md) for boundaries.

## Git workflow

- **Integration branch:** `dev` — open feature PRs against `dev`.
- **Production branch:** `main` — promote via PR from `dev` (or documented hotfix path).
- **Feature branches:** `feature/<JIRA-KEY>-<slug>` — one story per PR.

Full model, DAB mapping, and branch protection guidance: [docs/git-workflow.md](docs/git-workflow.md).

## Pull requests

New pull requests use [.github/pull_request_template.md](.github/pull_request_template.md). Before opening a PR, confirm:

1. **Jira key** in the title and description when your team uses Jira for traceability.
2. **Single story scope** — one Jira story per PR ([one-story-per-pr.mdc](.cursor/rules/one-story-per-pr.mdc)).
3. **Tests** — update [tests/](tests/) when hook or policy behavior changes ([mandatory-tests.mdc](.cursor/rules/mandatory-tests.mdc)).
4. **`OWNERSHIP=path/prefix/`** on Cursor **Task** prompts for implementation work where your team requires it ([jira-atlassian-mcp.mdc](.cursor/rules/jira-atlassian-mcp.mdc), [ownership-enforcement.mdc](.cursor/rules/ownership-enforcement.mdc)).

## Ownership lanes (CODEOWNERS)

GitHub [`.github/CODEOWNERS`](.github/CODEOWNERS) defines review ownership for parallel agent work. Map **Task** `OWNERSHIP=` prefixes to the closest CODEOWNERS path:

| OWNERSHIP= prefix | CODEOWNERS path | Typical worker |
|-------------------|-----------------|----------------|
| `OWNERSHIP=.cursor/` | `/.cursor/` | Framework / orchestration changes |
| `OWNERSHIP=.github/` | `/.github/` | CI/CD, templates, CODEOWNERS |
| `OWNERSHIP=src/mlops_intelligence/ingestion/` | `/src/mlops_intelligence/` (ingestion subdir when present) | data-engineering-agent |
| `OWNERSHIP=src/mlops_intelligence/agent/` | `/src/mlops_intelligence/agent/` (when present) | backend-agent |
| `OWNERSHIP=notebooks/` | `/notebooks/` | data-engineering-agent |
| `OWNERSHIP=resources/` | `/resources/` | data-engineering-agent |
| `OWNERSHIP=databricks.yml` | `/databricks.yml` | data-engineering-agent |
| `OWNERSHIP=docs/` | `/docs/` | documentation-agent |
| `OWNERSHIP=./` | Root + docs (coordinate with orchestrator file registry) | shell / story owner |

Orchestrator maintains a **file touch registry** per story to avoid conflicting parallel edits. See [.cursor/orchestration/README.md](.cursor/orchestration/README.md).

## Agents and Jira

When the Atlassian integration is enabled, use the **Atlassian MCP** for Jira operations — see [.cursor/rules/jira-atlassian-mcp.mdc](.cursor/rules/jira-atlassian-mcp.mdc).

## Local verification

```bash
# Hook and orchestration policy tests (required)
python3 -m unittest discover -s tests -p "test_*.py" -v

# Optional: lint hook Python
pip install -e ".[dev]"
ruff check .cursor/hooks
```

CI runs the same checks in [.github/workflows/cursor-framework-ci.yml](.github/workflows/cursor-framework-ci.yml).

## ML Operations pull requests

Platform changes (Unity Catalog, DAB, jobs, notebooks) must document operational impact in the PR. Use [.github/pull_request_template.md](.github/pull_request_template.md) and fill every section.

### Required sections (platform PRs)

| Section | What to include |
|---------|-----------------|
| **Unity Catalog impact** | Catalogs, schemas, tables, grants; additive vs breaking |
| **Databricks Asset Bundle** | Resources changed, target (`dev`/`staging`/`prod`), `bundle validate` command |
| **Rollout notes** | Deploy order, monitoring, **rollback** steps |
| **Testing performed** | `unittest`, SQL checks, notebook smoke paths |

### Pre-merge checklist

1. Jira key in PR title and description.
2. One story per PR; `OWNERSHIP=` matches CODEOWNERS lane.
3. Tests pass locally: `python3 -m unittest discover -s tests -p "test_*.py" -v`.
4. No secrets in `databricks.yml`, workflows, or docs.
5. For UC DDL: prefer additive migrations; document breaking changes and backfill.

**Example filled PR:** [docs/contributing/example-pr-description.md](docs/contributing/example-pr-description.md).
