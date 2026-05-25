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
