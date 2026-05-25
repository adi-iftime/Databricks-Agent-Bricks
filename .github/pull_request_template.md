<!--
Keep PRs traceable, single-scoped, and aligned with .cursor/rules.
Fill every section; remove this comment block before opening the PR if you prefer a cleaner description.
-->

## Summary

<!-- One short paragraph: what changed and why. -->

## Jira

- **Story:** <!-- e.g. PROJ-123 — paste key and title -->
- Link to issue: <!-- Jira URL -->

## Governance checklist

- [ ] **Jira key** appears in the **PR title** and this description (traceability).
- [ ] **Single story scope** — this PR maps to **one** Jira story ([one-story-per-pr](.cursor/rules/one-story-per-pr.mdc)); no bundled unrelated work.
- [ ] **Tests** — added or updated per [.cursor/rules/mandatory-tests.mdc](.cursor/rules/mandatory-tests.mdc), or the PR states a **documented exception** and why.
- [ ] **OWNERSHIP** — if work was driven via Cursor **Task** for implementation, the Task prompt included **`OWNERSHIP=path/prefix/`** where required ([jira-atlassian-mcp.mdc](.cursor/rules/jira-atlassian-mcp.mdc), [ownership-enforcement.mdc](.cursor/rules/ownership-enforcement.mdc)).

## Business context

<!-- Problem, user outcome, or ticket driver. -->

## Technical implementation

<!-- Approach, key decisions, tradeoffs. -->

## Impacted components

<!-- Paths, services, modules, pipelines. -->

## Testing performed

<!-- Commands run (e.g. pytest, ruff), manual checks, environment notes. -->

## Risks and limitations

<!-- Known gaps, follow-ups, feature flags. -->

## Dependencies

<!-- Other PRs, releases, migrations, config. -->

## Rollout notes

<!-- Deploy order, monitoring, rollback. -->

## Documentation

- [ ] README / runbooks / ADRs updated if behavior or ops changed ([mandatory-documentation.mdc](.cursor/rules/mandatory-documentation.mdc)), or **no doc delta** explained here.
