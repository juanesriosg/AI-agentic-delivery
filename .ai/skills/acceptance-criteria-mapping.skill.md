# Skill: Acceptance Criteria Mapping

## Purpose

Ensure the agent builds and tests exactly what was requested.

## Procedure

1. Convert each requirement into an acceptance criterion.
2. Reject vague criteria such as "works well" or "is scalable" unless translated into observable behavior.
3. For each criterion, define:
   - Inputs.
   - Expected behavior.
   - Negative/edge cases.
   - Validation method.
   - Evidence required.
4. Map criteria to tests and PR sections.
5. During self-review, verify every criterion has been satisfied or explicitly deferred.

## Traceability table

```md
| AC ID | Requirement | Implementation | Test/Evidence | Status | Notes |
|---|---|---|---|---|---|
```

## Status values

- `satisfied`
- `partially_satisfied`
- `blocked`
- `deferred_with_approval`
- `not_applicable`
