# Skill: Test Pyramid and Testing Lifecycle

## Purpose

Choose the right level of testing for fast feedback and real confidence.

## Principles

- Unit tests are fast and isolate logic.
- Component tests validate meaningful behavior inside a bounded component.
- Integration tests validate important collaborations.
- Contract tests protect API/event/schema compatibility.
- E2E tests validate critical user journeys but should be few, stable, and valuable.
- Dev tests are implementation-agent smoke checks.
- QA tests are acceptance and exploratory checks from a user/stakeholder perspective.

## Default strategy

For each task:

1. Add/adjust unit tests for changed logic.
2. Add component tests when behavior crosses a meaningful boundary.
3. Add integration/contract tests when the change affects APIs, persistence, messages, dependencies, or cross-module behavior.
4. Add E2E tests for critical user journeys or high-risk regressions.
5. Provide manual QA steps when automation is not practical.
6. Record all validation evidence.

## Anti-patterns

- Only testing the happy path.
- Relying only on E2E tests for business logic.
- Relying only on unit tests for cross-system behavior.
- Mocking the thing being validated.
- Asserting implementation details instead of behavior.
- Removing tests to pass CI.
