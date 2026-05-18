# Skill: Safe Implementation

## Purpose

Implement tasks with minimal, maintainable, reviewable changes.

## Procedure

1. Restate the task goal.
2. Identify the smallest code area that needs change.
3. Read neighboring code and tests.
4. Match existing style and patterns.
5. Implement the change.
6. Add tests.
7. Avoid unrelated cleanup.
8. Run validation.
9. Review the diff.
10. Document assumptions.

## Rules

- Keep changes narrow.
- Prefer existing abstractions.
- Avoid introducing dependencies.
- Avoid broad formatting.
- Avoid speculative refactors.
- Avoid touching high-risk paths unless required.
- Do not change public behavior beyond acceptance criteria.

## When refactoring is allowed

Refactoring is allowed only when:

- Required to implement the task safely.
- Small and local.
- Covered by tests.
- Clearly explained in the PR.

## Output

```md
Implementation summary:
Files changed:
Main design choice:
Alternatives considered:
Why this is the smallest safe change:
```
