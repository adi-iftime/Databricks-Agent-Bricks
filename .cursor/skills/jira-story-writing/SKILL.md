---
name: jira-story-writing
description: Decomposes feature work into small Jira stories with technical objectives, acceptance criteria, testing requirements, dependencies, risks, and recommended worker agent types; favors isolated PRs and low merge-conflict parallelization. Use when creating Jira stories, decomposing implementation work, planning sprint tasks, generating technical subtasks, creating bug tickets, defining acceptance criteria, or preparing orchestration execution plans.
---

# Jira Story Writing

Load this skill when:

- creating Jira stories
- decomposing implementation work
- planning sprint tasks
- generating technical subtasks
- creating bug tickets
- defining acceptance criteria
- preparing orchestration execution plans

## Workflow

1. Read the feature request and architecture analysis results.
2. Break implementation work into small independently executable stories.
3. Ensure stories are scoped to a single responsibility whenever possible.
4. Define clear technical objectives for each story.
5. Define acceptance criteria and testing requirements.
6. Identify dependencies between stories.
7. Assign the most appropriate worker agent type for each story.
8. Ensure stories can be implemented through isolated pull requests.
9. Avoid vague or oversized stories.
10. Prefer stories that minimize merge conflicts and parallel execution risks.

## Required fields and story rules

Every story must include:
- Objective
- Scope
- Acceptance Criteria
- Testing Requirements
- Dependencies
- Risks
- Recommended Agent Type

Story Rules:
- One responsibility per story.
- Stories must support isolated pull requests.
- Stories should minimize overlap with other stories.
- Avoid oversized implementation scope.

## Recommended Agent Type (values)

Use the worker type that best matches the story’s primary work. Prefer the project’s orchestration vocabulary if it differs.

| Agent type | Use when |
|------------|----------|
| `explore` | Read-only codebase discovery, locating files/patterns |
| `generalPurpose` | Multi-step implementation or ambiguous cross-cutting work |
| `shell` | Git, CI, commands, releases, scripted automation |
| `code-reviewer` | Review-only pass before merge |
| `ci-investigator` | Diagnose a specific failing CI check |
| `best-of-n-runner` | Isolated parallel attempts in separate worktrees |
| `cursor-guide` | Cursor product/settings/how-to (not app code) |

If none fit, set `Recommended Agent Type` to the closest match and one line explaining why.

## Story description template (paste into Jira)

Use these headings so each required field is explicit:

```markdown
## Objective
[Single technical outcome; link to feature request / architecture summary]

## Scope
[Inclusions: files, modules, APIs, flags. Exclusions: what this story explicitly does not change]

## Acceptance Criteria
- [ ] ...
- [ ] ...

## Testing Requirements
[Unit / integration / e2e / manual; commands or scenarios; data/fixtures]

## Dependencies
- Blocks: ...
- Blocked by: ...
- Related stories: ...

## Risks
[Merge conflict hotspots, shared files, rollout, backwards compatibility, perf]

## Recommended Agent Type
`...`

## PR isolation notes
[Expected touched paths; what other stories must avoid touching in parallel]
```

## Acceptance criteria style

Default to observable, testable bullets. Use Given/When/Then only when it improves clarity for behavior-heavy work.

## Parallel execution and merge conflicts

- Prefer stories that touch disjoint directories or modules; call out shared files early in **Risks** and **Dependencies**.
- Sequence stories that must edit the same high-churn file; do not parallelize those without an explicit merge owner.
- Favor contracts first (types, interfaces, feature flags) as thin stories, then implementations that consume them.

## Bug tickets

Still apply the required fields: **Objective** (fix outcome), **Scope** (versions/env), **Acceptance Criteria** (repro gone, regression covered), **Testing Requirements** (repro steps automated or checklist), **Dependencies**, **Risks**, **Recommended Agent Type** (often `generalPurpose` or `shell` for CI/logs).

## Output discipline

- Output a numbered story list for decomposition; each story must satisfy the required fields and story rules above.
- Mark unknowns as questions in **Risks** or **Dependencies**; do not invent product or architecture facts.
