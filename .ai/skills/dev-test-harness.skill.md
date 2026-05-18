# Skill: Dev Test Harness

## Purpose

Create the smallest safe local or cloud test harness needed to validate a task.

## Procedure

1. Discover existing test tools and conventions.
2. Prefer existing package scripts and wrappers.
3. Create task-scoped fixtures under test directories or ignored `.agent/` paths.
4. Avoid requiring production credentials or production data.
5. Make test data minimal, deterministic, and clearly named.
6. Document setup and teardown.
7. Remove temporary files unless they are intentionally ignored runtime artifacts.

## Examples

- Temporary directory for file-processing scripts.
- Local fake HTTP server.
- Docker compose test service when already used by repo.
- Seed data in test fixtures.
- Contract fixture JSON.
- CLI smoke script.

## Anti-patterns

- Global machine setup.
- Hardcoded local absolute paths.
- Tests that depend on developer-specific credentials.
- Tests that mutate shared external systems.
- Unbounded sleeps.
