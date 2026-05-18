# Test Levels

## Spec validation

The agent verifies that requirements are clear, testable, and mapped to evidence.

## Unit tests

Fast tests for isolated logic. Use them for algorithms, business rules, validation, formatting, and pure functions.

## Component tests

Tests for one component with controlled dependencies. Use them for API handlers, UI components, scripts, CLI commands, services, jobs, and adapters.

## Integration tests

Tests that verify important real collaborations: database, cache, queue, API, storage, auth, package boundaries, or service adapters.

## Contract tests

Tests that protect schemas, public APIs, events, SDK interfaces, or cross-repo contracts.

## End-to-end tests

Tests that simulate critical user journeys. Use sparingly and focus on workflows that matter to acceptance or release confidence.

## Dev tests

Manual or semi-automated smoke tests performed by the implementing agent to prove the feature works in a realistic local/cloud environment.

## QA tests

Acceptance and exploratory validation from the user/stakeholder perspective. QA tests may be manual or automated, but evidence must be recorded.

## Regression tests

Tests added after a bug is found so the issue does not return.
