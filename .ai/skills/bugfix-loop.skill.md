# Skill: Bugfix Loop

## Purpose

Fix bugs with reproduction, root cause analysis, and regression coverage.

## Procedure

1. Understand bug report.
2. Reproduce issue.
3. Capture expected vs actual behavior.
4. Locate root cause.
5. Write or identify failing test.
6. Implement minimal fix.
7. Verify test passes.
8. Run related tests.
9. Document root cause.
10. Open PR.

## Bug report minimum

```yaml
expected_behavior:
actual_behavior:
steps_to_reproduce:
affected_env:
customer_impact:
logs_or_errors:
```

## Escalate when

- Cannot reproduce and no logs exist.
- Fix requires product decision.
- Fix affects data integrity.
- Fix requires migration.
- Fix affects auth/security/billing.
- Root cause is external service or non-owned repo.

## Output

```md
Root cause:
Reproduction:
Fix:
Regression test:
Validation:
Risk:
Follow-up:
```
