# Skill: Notifications

## Purpose

Keep the manager informed without requiring constant monitoring.

## Notification events

Notify when:

- Task claimed.
- Task blocked.
- PR ready.
- PR updated after review.
- Feature agent-complete.
- Epic agent-complete.
- High-risk decision needed.
- CI repeatedly failing.
- Ownership unclear.
- Queue empty.
- Guardrail violation detected.

## Channels

Use available project mechanisms:

- GitHub issue comment.
- GitHub PR comment.
- Project board status.
- Slack or Teams if configured by the organization.
- Email only if configured by the organization.

Do not invent external notification channels.

## Task done notification

```md
Status: PR ready
Task:
Repo:
Branch:
PR:
Acceptance criteria satisfied:
Validation:
Risk:
Rollback:
Manager action needed:
Next agent action:
```

## Feature done notification

```md
Status: Feature agent-complete
Feature:
Related tasks:
Related PRs:
Validation:
Known risks:
Ready for:
Manager action needed:
```

## Epic done notification

```md
Status: Epic agent-complete
Epic:
Completed features:
Related PRs:
Integration validation:
Remaining risks:
Stakeholder acceptance needed:
Manager action needed:
```

## Blocked notification

```md
Status: Blocked
Task:
Repo:
Blocker:
Impact:
Options:
Recommendation:
Manager/owner decision needed:
```
