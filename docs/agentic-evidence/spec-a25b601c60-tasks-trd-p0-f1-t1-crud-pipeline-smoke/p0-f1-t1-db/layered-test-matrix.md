# Layered Test Matrix

Task: `p0-f1-t1-db`
Story: `STORY-crud-pipeline-smoke`
Spec: `SPEC-20260520-crud-pipeline-smoke`

## Spec comprehension

Business goal:
Verify the agentic SDLC can deliver a local CRUD smoke app and move work through database, API, frontend, QA, and PM evidence gates.

Technical goal:
Implement and validate the SQLite notes persistence layer for create, list, read, update, and delete.

Acceptance criteria with IDs:
- AC-001: SQLite schema and repository tests prove create/list/update/delete behavior. Status: passed by `tests.test_database_notes`.
- AC-002: Relevant tests or explicit blocker evidence are recorded. Status: passed by `test-evidence.md` and `agents.log.md`.
- AC-003: QA and PM evidence accurately reflect pass, blocked, or not-applicable status. Status: passed by `qa-checklist.md` and `pm-checklist.md`.

Assumptions:
- This task is database-only and does not change API or frontend behavior.
- Local SQLite files are created in temporary paths for tests.
- Downstream API/UI/QA tasks own their own test evidence and remain blocked on their corresponding layer work, not on this database layer.

Clarifications needed:
- None.

Safe progress while waiting:
- N/A; the task is not blocked.

Test traceability:
- AC-001 -> `python3 -m unittest tests.test_database_notes -v`
- AC-002 -> `agents.log.md`, `test-evidence.md`
- AC-003 -> `qa-checklist.md`, `pm-checklist.md`, `layer-gates/database.passed.md`

## Validation levels

- Spec validation: reviewed task list and TRD mappings.
- Static checks: not required because this task only confirms the DB layer contract and repository behavior already present in the repo.
- Unit tests: passed.
- Component tests: not applicable for database layer.
- Integration tests: passed via SQLite-backed repository tests.
- Contract tests: not applicable for database layer.
- End-to-end tests: not applicable for database layer.
- Dev tests: not applicable.
- QA tests: recorded as pass for the database layer; downstream UI QA is explicitly not part of this task.
- PM tests: recorded as not-applicable for downstream product approval at this layer.
- Regression tests: covered by CRUD round-trip, empty-title rejection, missing-note behavior, and schema/trigger validation.
