# [AI][Bugfix] Prevent duplicate customer notification on retry

## Summary

Added idempotency handling to notification retry flow so the same event does not send duplicate customer notifications.

## Business goal

Customers should not receive duplicate notifications when an internal retry occurs.

## Technical notes

- Added idempotency check before sending notification.
- Preserved existing behavior for unique events.
- Added regression test for duplicate retry.

## Validation

```text
npm test -- notification.service.test.ts
Result: passed

npm run lint
Result: passed
```

## Risk

Medium.

Reason: touches notification behavior and retry flow. No schema or public API changes.

## Rollback

Revert this PR. The system returns to previous retry behavior.

## Files worth reviewing carefully

- `src/notifications/notification.service.ts`
- `src/notifications/notification.service.test.ts`

## Assumptions

- Event ID is stable across retries.
- Duplicate suppression is desired only for the same event ID.

## Follow-up

Consider adding metric for suppressed duplicate notifications.

## Task / Epic

- TASK-123
