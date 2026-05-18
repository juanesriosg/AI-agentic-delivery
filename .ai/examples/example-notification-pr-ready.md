Status: PR ready
Task: TASK-123 Fix duplicate customer notification on retry
Repo: example-org/customer-service
Branch: ai/TASK-123-notification-idempotency
PR: https://github.com/example-org/customer-service/pull/456

Acceptance criteria satisfied:
- Same event retry does not send duplicate notification.
- Unique events still send normally.
- Regression test added.

Validation:
- `npm test -- notification.service.test.ts` passed.
- `npm run lint` passed.

Risk:
Medium. Touches retry/notification behavior, no public API or migration.

Rollback:
Revert PR.

Files worth reviewing:
- `src/notifications/notification.service.ts`
- `src/notifications/notification.service.test.ts`

Manager action needed:
Review PR behavior and retry assumption.

Next agent action:
Continuing to next `ai:ready` low-risk task.
