# Spec Implementation Pipeline

This is the required pipeline after a spec is detected on a watched branch.

## Stage 0 — Detection

Input:

- branch,
- commit SHA,
- spec path,
- repository.

Output:

- detected spec report,
- dispatch task or clarification request.

## Stage 1 — Spec comprehension

The agent must produce:

```md
Business goal:
Technical goal:
Acceptance criteria with IDs:
Assumptions:
Clarifications needed:
Safe progress while waiting:
Risk classification:
Test traceability:
```

For PRD/TRD packages, comprehension must include document type and source document paths:

```md
Document type:
PRD:
Implementation plan:
TRD:
Task list:
Conflict check:
```

Agents must read package documents in this authority order:

```text
PRD -> Implementation Plan -> TRD -> Task List
```

## Stage 2 — Planning

The agent must create a small implementation plan:

```md
Files likely affected:
Design approach:
Tests to add first:
Risks:
Rollback:
```

If the changed document is only a PRD, create or update `implementation-plan.md` before coding. If it is an implementation plan, create TRDs before coding. If it is a TRD, create or verify the task list before coding. If it is a ready task list, implement from the task list while checking the linked TRD, plan, and PRD for conflicts.

## Stage 3 — Test-first or test-near-first work

The agent should start with the smallest meaningful test:

1. Reproduce current behavior or bug.
2. Add unit tests for pure logic.
3. Add component tests for boundaries.
4. Add integration or contract tests for external interfaces.
5. Add E2E tests only where meaningful and maintainable.

## Stage 4 — Implementation

The implementation must be the smallest safe change that satisfies the acceptance criteria.

The agent must avoid broad refactors unless the spec explicitly asks for them or the refactor is necessary to safely implement the change.

## Stage 5 — Validation

The agent must run relevant validation in this order:

1. targeted unit tests,
2. component tests,
3. integration tests,
4. contract tests,
5. E2E tests,
6. lint,
7. typecheck,
8. build,
9. security/dependency checks,
10. dev/manual checks,
11. QA handoff checks.

Skipped test levels must be explained.

## Stage 6 — Self-review and improvement

The agent must criticize its own code and fix valid findings before marking the PR ready.

## Stage 7 — PR and notification

The PR must target the source spec branch and include:

- spec path,
- source spec branch,
- acceptance criteria satisfied,
- test evidence,
- bugs found,
- risks,
- rollback,
- QA handoff,
- deployment readiness.

## Stage 8 — QA and release readiness

A feature is not agent-complete until the agent provides QA evidence or a clear QA handoff with remaining manual verification steps.

Production deployment remains human-approved by default.
