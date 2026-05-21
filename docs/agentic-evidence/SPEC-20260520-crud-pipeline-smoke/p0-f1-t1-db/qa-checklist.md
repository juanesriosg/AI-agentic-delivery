# QA Checklist - P0-F1-T1-DB

## Scope

Database layer only: SQLite notes schema and repository behavior.

## Spec comprehension summary

Business goal: prove the autonomous SDLC can validate a local CRUD database layer as part of the smoke pipeline.
Technical goal: verify the SQLite notes schema and repository support create, list, read, update, and delete with empty-title rejection and missing-note handling.
Acceptance criteria with IDs:
- AC-001: Database layer creates and tests the notes schema and CRUD repository behavior.
- AC-004: QA/PM evidence maps FR-001 through FR-004 to validation output, risk, rollback, and follow-up gaps.
Assumptions:
- The database layer is already implemented in `database/schema.sql` and `tests/test_database_notes.py`.
- No cloud, auth, or production data work is in scope.
Clarifications needed:
- None blocking for the database layer.
Safe progress while waiting:
- Validate the schema and repository tests, then write QA artifacts and layer-gate evidence.
Test traceability:
- FR-001 -> `tests/test_database_notes.py`
- AC-001 -> `tests/test_database_notes.py`
- NFR-REL-001 -> environment blocker note in `test-evidence.md`

## Functional checklist

- [x] SQLite schema defines the `notes` table with the required columns.
- [x] Repository behavior supports create, list, read, update, and delete.
- [x] Empty titles are rejected.
- [x] Missing notes return `None` or `False` instead of fabricated records.
- [x] Timestamps are populated and updated by SQLite-backed behavior.

## Test checklist

- [x] Unit/repository tests executed successfully with `python3 -m unittest tests.test_database_notes -v`.
- [x] Environment gap recorded: `python` is not available on PATH.
- [x] No API, frontend, E2E, visual, or accessibility checks are required for this task layer.

## Regression checklist

- [x] Tests cover CRUD round-trip behavior.
- [x] Tests cover empty-title validation.
- [x] Tests cover missing note handling.
- [x] Test coverage is local and temporary-file based.

## Pass / Fail

- Status: PASS
- Notes: The database layer is ready for the API task to consume.
