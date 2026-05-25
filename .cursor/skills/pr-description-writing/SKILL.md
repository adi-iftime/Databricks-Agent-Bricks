---
name: pr-description-writing
description: >-
  Drafts structured pull request descriptions from diffs and context: purpose,
  approach, impacted systems, testing, risks, dependencies, rollout, and links
  to tickets or ADRs for reviewer clarity and traceability. Use when creating
  pull requests, generating implementation summaries, documenting code changes,
  preparing review context, documenting rollout considerations, summarizing
  completed work, linking Jira stories and dependencies, or preparing
  production-ready PRs.
---

# PR Description Writing

Load this skill when:

- creating pull requests
- generating implementation summaries
- documenting code changes
- preparing review context
- documenting rollout considerations
- summarizing completed work
- linking Jira stories and dependencies
- preparing production-ready PRs

## Workflow

1. Analyze the pull request changes and impacted systems.
2. Summarize the business and technical purpose of the implementation.
3. Explain the implementation approach and architectural decisions.
4. Describe testing coverage and validation performed.
5. Identify risks, limitations, rollout considerations, and dependencies.
6. Link related Jira stories, architecture decisions, or upstream dependencies.
7. Ensure the PR description is concise, structured, and understandable.
8. Improve traceability and maintainability of implementation history.
9. Ensure reviewers can quickly understand the implementation scope and impact.
10. Avoid vague, incomplete, or unstructured pull request descriptions.

Every PR description must include:
- Summary
- Business Context
- Technical Implementation Details
- Impacted Components
- Testing Performed
- Risks and Limitations
- Dependencies
- Rollout Notes

PR Rules:

Keep explanations concise and structured.
Clearly explain why the change exists.
Avoid vague implementation summaries.
Include all relevant testing information.
Document architectural decisions and tradeoffs.
Reference related stories and dependencies.

## Template (non-normative)

Paste and fill; headings match the required sections above.

```markdown
## Summary
[What changed in one short paragraph]

## Business Context
[Problem, user outcome, or ticket driver]

## Technical Implementation Details
[Approach, key decisions, tradeoffs]

## Impacted Components
[Services, modules, APIs, data paths]

## Testing Performed
[Commands run, manual checks, env]

## Risks and Limitations
[Known gaps, follow-ups, feature flags]

## Dependencies
[Other PRs, releases, migrations, config]

## Rollout Notes
[Deploy order, monitoring, rollback]
```
