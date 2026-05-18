# Skill: Exploratory Testing and Bug Discovery

## Purpose

Find defects that scripted tests may miss.

## Bug discovery lenses

- Edge values.
- Invalid input.
- Missing data.
- Duplicate actions.
- Permission boundaries.
- Tenant boundaries.
- Race conditions.
- Dependency failures.
- Retry behavior.
- Partial failure.
- Slow network or timeout.
- Large data volume.
- Accessibility and usability.
- Observability gaps.

## Procedure

1. Start from acceptance criteria and changed files.
2. Build a short exploration charter.
3. Test happy path once, then focus on edge and failure paths.
4. When a bug appears, reduce to minimal reproduction.
5. Add a failing test when practical.
6. Classify severity and ownership.
7. Report clearly and continue safe progress.

## Output

```md
Exploration charter:
Areas tested:
Bugs found:
Regression tests added:
Risks remaining:
```
