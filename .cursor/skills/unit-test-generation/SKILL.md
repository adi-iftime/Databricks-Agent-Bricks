---
name: unit-test-generation
description: Analyzes implementation and expected behavior, generates isolated deterministic unit tests for happy paths, edges, boundaries, nulls, and errors, mocks externals when appropriate, and surfaces coverage gaps with concise cases. Use when implementing new functionality, modifying business logic, creating APIs, modifying pipelines, adding utility functions, validating edge cases, or improving test coverage.
---

# Unit Test Generation

Load this skill when:

- implementing new functionality
- modifying business logic
- creating APIs
- modifying pipelines
- adding utility functions
- validating edge cases
- improving test coverage

## Workflow

1. Analyze the implementation logic and expected behavior.
2. Generate unit tests covering normal scenarios and edge cases.
3. Validate boundary conditions, null handling, and error handling.
4. Ensure tests are isolated and deterministic.
5. Mock external systems and dependencies when appropriate.
6. Ensure tests remain maintainable and readable.
7. Verify expected outputs and side effects.
8. Detect missing test coverage areas.
9. Prefer concise and focused test cases.
10. Avoid flaky or environment-dependent tests.

Unit Testing Rules:
- Every production change requires tests.
- Cover positive and negative scenarios.
- Cover boundary conditions and edge cases.
- Avoid flaky tests.
- Mock external dependencies whenever possible.

Required Test Areas:

Happy Path
Edge Cases
Error Handling
Null Handling
Boundary Conditions

## Notes (non-normative)

- Match the project’s test framework, fixtures, and naming; mirror existing patterns in the same package.
- For time, randomness, and I/O: inject or stub dependencies so outcomes do not depend on wall clock, network, or global mutable state unless the test explicitly owns that setup.

---

## Stack and patterns (general testing)

# Skill: Testing

Reusable capability definition. **Not** tied to any single agent; routing is defined in orchestration rules.

## Technologies

- Test runners and frameworks **already in the repository** (e.g. pytest, JUnit, vitest)
- HTTP testing tools appropriate to the stack (client libraries, in-process app clients)
- Fixtures, factories, and snapshot tools if the repo already adopts them

## Patterns

- Arrange–act–assert; isolated unit tests vs narrower integration tests
- Stable selectors and boundary testing for public APIs
- Data setup/teardown that avoids cross-test coupling

## Domain knowledge

- Coverage as a signal, not a goal; risk-based test selection
- Flake detection: time, network, concurrency, shared global state
- CI expectations: fast feedback suites vs heavier nightly suites (project-dependent)

## Best practices

- One logical behavior per test; descriptive names
- Prefer testing public contracts over implementation details
- Fail messages should explain *what* broke and *where* to look
