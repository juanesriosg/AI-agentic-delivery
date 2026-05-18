# Example QA Handoff

Feature/task: CSV user export
Repo: example/api
Branch: ai/TASK-123-user-export
PR: #456
Environment: local dev / staging candidate

## Acceptance criteria status

| AC | Status | Evidence |
|---|---|---|
| AC-001 | Passed | integration export test, manual curl |
| AC-002 | Passed | negative permission test |
| AC-003 | Passed | large fixture pagination test |
| AC-004 | Passed | CSV formatter unit test |

## Automated validation

| Level | Command | Result |
|---|---|---|
| Unit | pytest tests/unit/test_csv_export.py | Passed |
| Integration | pytest tests/integration/test_user_export.py | Passed |
| Static | ruff check . | Passed |

## Manual QA steps

1. Log in as admin.
2. Open `/admin/users/export.csv`.
3. Verify CSV downloads with id, email, created_at, status.
4. Log in as non-admin and verify 403.

## Bugs found

None unresolved.

## Focus areas for QA

- Permission behavior.
- CSV column order.
- Large export responsiveness.
