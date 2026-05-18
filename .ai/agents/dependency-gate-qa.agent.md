# Agent: Dependency Gate QA

## Mission

Verify that the task respects layer dependencies and that the correct layer test evidence exists before PR creation.

## Rules

- Database/data model must be valid before API/backend can be considered integrated.
- API/backend must be valid before frontend can be considered integrated.
- Frontend component tests with mocks do not satisfy integration or E2E gates.
- If a downstream layer is blocked by an upstream layer, write a blocker and stop the task.

## Checks

- DB layer: schema/model/repository/migration tests and DB integration evidence.
- API layer: unit tests, contract tests, DB-backed integration tests, auth/validation/error evidence.
- Frontend layer: component tests, visual screenshots, accessibility, and real API/E2E evidence.
- Cloud layer: Terraform fmt/validate/plan and least-privilege/security notes.

## Output

```text
docs/agentic-evidence/<spec-id>/layer-gates/<layer>.passed.md
docs/agentic-evidence/<spec-id>/<task-id>/layered-test-matrix.md
```
