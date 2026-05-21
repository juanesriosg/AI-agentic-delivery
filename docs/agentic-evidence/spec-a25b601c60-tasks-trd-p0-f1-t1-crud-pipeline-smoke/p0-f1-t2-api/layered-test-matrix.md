# Layered Test Matrix

| AC ID | Layer | Validation | Status |
|---|---|---|---|
| AC-001 | Database dependency | `python3 -m unittest tests.test_database_notes` and existing database layer gate evidence | passed |
| AC-002 | API backend | `python3 -m unittest discover -s backend/tests -v` after DB gate passed; code-edit scope blocked by branch conflict guard, but validation evidence is complete | passed |
| AC-003 | Frontend | Not applicable for this task. Frontend remains blocked on the later UI task. | n/a |
| AC-004 | QA/PM evidence | `qa-checklist.md`, `pm-checklist.md`, `test-evidence.md`, `pr-notification.md`, `scale-security-architecture-review.md` | passed |

## Notes

- The API layer depends on the database layer that was already completed in `P0-F1-T1-DB`.
- The API task stayed within the local SQLite boundary and did not introduce auth, cloud, or deployment changes.
- The execution order was database first, then API validation, then deferred frontend work.
