# Skill: Integration and End-to-End Testing

## Purpose

Validate cross-component behavior and critical user flows.

## Integration testing

Use when the change affects:

- Database queries or migrations.
- External service adapters.
- Queues/events.
- API-to-service-to-storage flows.
- Authentication or authorization boundaries.
- Caching behavior.
- File or object storage.
- Multiple packages/modules.

## E2E testing

Use when the change affects:

- Critical customer journeys.
- Workflow orchestration.
- UI-to-API behavior.
- Release-blocking acceptance criteria.
- High-risk regressions.

## Procedure

1. Identify the path under test.
2. Define minimal representative data.
3. Prefer local reproducible environments.
4. Use bounded waits for async behavior.
5. Assert outcomes visible to users or downstream systems.
6. Record known gaps and flakiness risk.

## Evidence

```md
Integration/E2E validation:
- Flow:
- Environment:
- Data:
- Command/manual steps:
- Result:
- Bugs found:
- Gaps:
```
