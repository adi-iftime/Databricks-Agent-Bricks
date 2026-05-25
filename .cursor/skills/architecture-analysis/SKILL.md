---
name: architecture-analysis
description: Analyzes repository structure, patterns, module boundaries, dependencies, downstream impact, and architectural risks; recommends reuse and incremental extension; produces a concise summary for planners and implementers. Use when starting a new feature, analyzing an unfamiliar codebase, planning implementation, decomposing tasks into stories, modifying system architecture, evaluating dependencies, introducing new services, pipelines, or modules, validating consistency with existing patterns, or planning distributed systems or data pipelines. Skip for simple documentation edits, small isolated bug fixes, or unrelated frontend styling changes.
---

# Architecture Analysis

## When to load this skill

Load this skill when:

- starting a new feature
- analyzing an unfamiliar codebase
- planning implementation work
- decomposing tasks into stories
- modifying system architecture
- evaluating dependencies
- introducing new services, pipelines, or modules
- validating consistency with existing patterns
- planning distributed systems or data pipelines

Do not load for:

- simple documentation edits
- small isolated bug fixes
- unrelated frontend styling changes

## Workflow

1. Inspect the existing repository structure before proposing changes.
2. Identify architecture patterns, module boundaries, naming conventions, and existing abstractions.
3. Detect impacted systems, modules, services, pipelines, or APIs.
4. Identify dependencies and downstream consumers.
5. Evaluate consistency with existing architecture and engineering conventions.
6. Detect risks such as breaking changes, circular dependencies, or architectural drift.
7. Recommend reuse of existing abstractions before introducing new patterns.
8. Produce a concise architecture summary that can be used by planning and implementation agents.
9. Avoid implementation details unless necessary for architectural reasoning.
10. Prefer incremental extension of the existing architecture over large refactors.

## Mandatory Architecture Rules

- Inspect existing patterns before introducing new ones.
- Reuse existing abstractions whenever possible.
- Avoid unnecessary architectural complexity.
- Avoid unrelated refactors.
- Respect module ownership boundaries.
- Prefer incremental changes over large rewrites.

## Required Output Sections

- Existing Architecture Summary
- Impacted Components
- Dependency Analysis
- Risk Analysis
- Recommended Implementation Direction
