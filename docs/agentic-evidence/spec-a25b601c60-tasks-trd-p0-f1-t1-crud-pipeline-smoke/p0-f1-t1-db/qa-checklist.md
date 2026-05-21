# QA Checklist

Task: `p0-f1-t1-db`

- [x] Database schema exists for notes.
- [x] Repository supports create, list, read, update, delete.
- [x] Empty title validation is enforced.
- [x] Missing-note behavior is deterministic.
- [x] SQLite-backed unit/integration test passed.
- [x] Current verification run was completed in the local runtime with `python3` after confirming `python` is not on PATH.
- [x] Exact blocker evidence recorded when tests are unavailable or explicitly not applicable.
- [x] No cloud, auth, secrets, or deployment scope was introduced.

Status: pass
Reason: The database layer is implemented and verified with SQLite-backed tests; QA/PM are intentionally not-applicable beyond this layer.
