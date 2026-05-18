# Escalation Policy

Agents should escalate early. Escalation is not failure.

## Escalate before coding when

- Risk is high.
- Repo is not owned by the manager/project.
- Acceptance criteria are missing.
- Task touches protected areas.
- Public API or cross-repo contract may change.
- Data migration or deletion may be required.
- Security/auth/billing/payment behavior may change.
- Infrastructure or deployment pipeline may change.

## Escalate during coding when

- Requirement conflicts with code reality.
- Tests reveal broader bug.
- Implementation requires scope expansion.
- Existing code has critical defect unrelated to task.
- Needed credentials/secrets are unavailable.
- Third-party dependency behavior is unclear.

## Escalate after validation when

- Related tests fail and cannot be fixed safely.
- Unrelated tests fail and block confidence.
- Coverage decreases.
- CI fails more than twice.
- PR risk increased from original task.

## Escalation format

```md
Status: Needs manager decision
Task:
Repo:
Current state:
Decision needed:
Options:
Recommendation:
Risk if we continue:
Risk if we stop:
```
