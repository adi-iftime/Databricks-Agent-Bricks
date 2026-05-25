# Skills catalog (`.cursor/skills/`)

Reusable workflow skills for Cursor agents. Each skill lives in **`<name>/SKILL.md`** with YAML frontmatter (`name`, `description`) and procedural guidance.

**Full agent mapping** is in the main [README.md](../../README.md#skills-system) and in each agent’s **Alignment with this project** section.

## Lifecycle overview

```
  DEFINE          PLAN           BUILD          VERIFY         REVIEW          SHIP
 ┌──────┐      ┌──────┐      ┌──────┐      ┌──────┐      ┌──────┐      ┌──────┐
 │ Idea │ ───▶ │ Spec │ ───▶ │ Code │ ───▶ │ Test │ ───▶ │ Gate │ ───▶ │ Live │
 │Refine│      │ Plan │      │ Impl │      │Debug │      │Review│      │ Ship │
 └──────┘      └──────┘      └──────┘      └──────┘      └──────┘      └──────┘
```

## Define

| Skill | Purpose | Primary agents |
|-------|---------|----------------|
| [idea-refine](idea-refine/SKILL.md) | Divergent/convergent refinement of vague ideas | technical-planning-agent |
| [spec-driven-development](spec-driven-development/SKILL.md) | PRD/spec before implementation | technical-planning-agent |

## Plan

| Skill | Purpose | Primary agents |
|-------|---------|----------------|
| [architecture-analysis](architecture-analysis/SKILL.md) | Repo structure, boundaries, risks | technical-planning-agent |
| [feature-decomposition](feature-decomposition/SKILL.md) | Work breakdown, dependencies, parallelization | technical-planning-agent, orchestrator-agent |
| [jira-story-writing](jira-story-writing/SKILL.md) | Jira stories with acceptance criteria | technical-planning-agent |

## Build

| Skill | Purpose | Primary agents |
|-------|---------|----------------|
| [incremental-implementation](incremental-implementation/SKILL.md) | Vertical slices; implement, test, commit | backend, frontend, data-engineering, data-scientist |
| [test-driven-development](test-driven-development/SKILL.md) | Red–green–refactor discipline | All implementation workers, qa-agent |
| [api-development](api-development/SKILL.md) | APIs, contracts, backend patterns | backend-agent |
| [frontend-ui-engineering](frontend-ui-engineering/SKILL.md) | UI components, a11y, design systems | frontend-agent |
| [pyspark-development](pyspark-development/SKILL.md) | PySpark, Delta, medallion patterns | data-engineering-agent |
| [machine-learning](machine-learning/SKILL.md) | ML workflows and modeling patterns | data-scientist-agent |
| [business-intelligence](business-intelligence/SKILL.md) | KPIs, semantic layers, BI patterns | data-analyst-agent |
| [context-engineering](context-engineering/SKILL.md) | Session context, rules, MCP usage | orchestrator-agent, all agents |
| [source-driven-development](source-driven-development/SKILL.md) | Official docs–first implementation | All implementation workers |

## Verify

| Skill | Purpose | Primary agents |
|-------|---------|----------------|
| [unit-test-generation](unit-test-generation/SKILL.md) | Unit tests, edges, mocks | qa-agent, implementation workers |
| [pipeline-testing](pipeline-testing/SKILL.md) | Pipeline/schema/idempotency tests | qa-agent, data-engineering-agent |
| [browser-testing-with-devtools](browser-testing-with-devtools/SKILL.md) | Browser/DevTools validation | frontend-agent, qa-agent |
| [debugging-and-error-recovery](debugging-and-error-recovery/SKILL.md) | Reproduce → fix → guard | qa-agent, implementation workers |

## Review

| Skill | Purpose | Primary agents |
|-------|---------|----------------|
| [code-review](code-review/SKILL.md) | Five-axis PR review, sizing, severity | code-review-agent |
| [code-simplification](code-simplification/SKILL.md) | Simplify without behavior change | code-review-agent |
| [security-review](security-review/SKILL.md) | Security analysis and hardening | security-agent |
| [performance-optimization](performance-optimization/SKILL.md) | Measure-first optimization | backend, frontend, data-engineering |

## Ship

| Skill | Purpose | Primary agents |
|-------|---------|----------------|
| [git-workflow-and-versioning](git-workflow-and-versioning/SKILL.md) | Trunk-style git, atomic commits | All implementation workers |
| [pr-description-writing](pr-description-writing/SKILL.md) | Structured PR bodies | All workers (at PR time) |
| [ci-cd-and-automation](ci-cd-and-automation/SKILL.md) | Pipelines, flags, CI feedback | backend-agent, data-engineering-agent |
| [deprecation-and-migration](deprecation-and-migration/SKILL.md) | Safe deprecation and migrations | backend-agent, data-engineering-agent |
| [documentation-and-adrs](documentation-and-adrs/SKILL.md) | ADRs, API docs, runbooks | documentation-agent |
| [shipping-and-launch](shipping-and-launch/SKILL.md) | Release readiness and launch | orchestrator-agent |

## Conventions

- **`name`** in frontmatter matches the directory name (kebab-case).
- Use **`description: >-`** folded scalars when the description contains colons.
- Prefer **Load this skill when** bullets at the top of the body for discoverability.
- Skills complement **rules** (`.cursor/rules/`); rules are always-on governance, skills are on-demand playbooks.

## Merged during integration

These source files were **merged** into existing skills (not kept as duplicates):

| Source (removed) | Merged into |
|------------------|-------------|
| `code-review-and-quality` | `code-review` |
| `security-and-hardening` | `security-review` |
| `planning-and-task-breakdown` | `feature-decomposition` |
| `testing` | `unit-test-generation` |
