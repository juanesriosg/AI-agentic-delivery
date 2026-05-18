# Skill: Component Testing

## Purpose

Validate a component as a coherent behavior unit while keeping tests fast and deterministic.

## Component boundary examples

- API handler.
- UI component.
- CLI command.
- Service method.
- Background job.
- Repository adapter.
- Script.
- Data transformer.

## Procedure

1. Identify the public behavior of the component.
2. Use real code inside the component boundary.
3. Control external dependencies with fakes, temp resources, local mocks, or contract fixtures.
4. Test realistic user/developer interactions.
5. Include edge cases and error handling.
6. Keep fixtures understandable.
7. Avoid testing private internals unless necessary for safety.

## Evidence

```md
Component tests:
- Component:
- Behavior:
- Command:
- Result:
- ACs covered:
```
