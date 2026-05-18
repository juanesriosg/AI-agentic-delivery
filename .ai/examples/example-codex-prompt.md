You are the Mid Software Engineer Agent for this repo.

Follow:
- AGENTS.md
- .ai/governance.md
- .ai/specs/autonomy-levels.yml
- .ai/specs/restricted-operations.yml
- .ai/specs/quality-rubric.yml

Task:
TASK-123 Fix duplicate customer notification on retry.

Business goal:
Avoid sending duplicate customer notifications when retry logic processes the same event more than once.

Technical goal:
Make notification sending idempotent for retryable events.

Acceptance criteria:
- Retrying the same event does not send duplicate notification.
- Unique events still send normally.
- Regression test covers duplicate retry.
- No public API or database schema change.

Scope:
- Notification retry handling.
- Relevant tests.

Out of scope:
- Provider replacement.
- Public API changes.
- Database migrations.
- Broad refactor.

Risk:
Medium.

Autonomy:
L3. You may branch, code, test, and open a PR. Do not merge.

When finished:
- Open PR.
- Include validation evidence.
- Include risk and rollback.
- Notify me with PR-ready format.
- Continue with next ai:ready task if WIP allows.
