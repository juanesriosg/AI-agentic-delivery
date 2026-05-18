# Example Spec Review

Task: Export active users as CSV
Repo: example/api

## Business goal

Support operations team reporting without manual database access.

## Technical goal

Add an authenticated endpoint that exports active users in CSV format.

## Acceptance criteria

- AC-001: Admin users can request a CSV export of active users.
- AC-002: Non-admin users receive a permission error.
- AC-003: Export is paginated/streamed and does not load all users into memory.
- AC-004: CSV includes id, email, created_at, and status.

## Assumptions

- A-001: Archived users are excluded because the task says active users.

## Clarifications

| ID | AC | Question | Blocking? | Safe progress |
|---|---|---|---|---|
| Q-001 | AC-004 | Should names be included in the CSV? | No | Implement required fields only. |

## Test traceability

| AC | Unit | Component | Integration | Contract | E2E/QA | Evidence |
|---|---|---|---|---|---|---|
| AC-001 | CSV formatter | Endpoint component | DB query export | API schema | Manual QA download | TBD |
| AC-002 | Permission rule | Endpoint component | Auth integration | API schema | Manual negative test | TBD |
| AC-003 | Pagination unit | Export service | Large fixture integration | N/A | QA with fixture | TBD |
| AC-004 | Formatter unit | Endpoint component | Export integration | API schema | CSV inspection | TBD |
