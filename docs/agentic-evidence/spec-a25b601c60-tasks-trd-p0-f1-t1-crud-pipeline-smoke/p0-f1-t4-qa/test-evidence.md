# Test Evidence

## Environment

- Runtime: local
- Repo: `AI-autonomous-page`
- Branch: `dev/crud-pipeline-smoke`
- Python available for validation: `python3 3.12.3`
- Node available for validation: `v22.19.0`
- Browser tooling available after `npx playwright install chromium`
- Browser flow run against a temporary reverse proxy on `http://127.0.0.1:4178/` with the API on `http://127.0.0.1:8002`

## Validation commands

1. `bash .ai/scripts/detect-runtime.sh`
2. `bash .ai/scripts/bootstrap-task-env.sh`
3. `python3 -m unittest tests.test_database_notes -v`
4. `python3 -m unittest backend.tests.test_notes_api -v`
5. `npm test`
6. `npm run build`
7. `python3 .ai/scripts/agent-self-review.py --format markdown`
8. `python3 .ai/scripts/check-scale-readiness.py --format markdown`
9. `python3 .ai/scripts/spec-quality-check.py --spec specs/crud-pipeline-smoke/tasks/tasks-trd-p0-f1-t1-crud-pipeline-smoke.md --format markdown`
10. `python3 .ai/scripts/generate-test-matrix.py --spec specs/crud-pipeline-smoke/tasks/tasks-trd-p0-f1-t1-crud-pipeline-smoke.md`
11. Playwright browser flow against `http://127.0.0.1:4178/`

## Results

### Runtime detection

Result: PASS

Output:

```text
Agent runtime detection
runtime: local
task_id: dev-crud-pipeline-smoke
repo: AI-autonomous-page
branch: dev/crud-pipeline-smoke
reasons: none
```

### Task environment bootstrap

Result: PASS

Output:

```text
[agent-bootstrap] task_id=dev-crud-pipeline-smoke
[agent-bootstrap] env_root=.agent/envs/dev-crud-pipeline-smoke
[agent-bootstrap] bootstrap complete
```

### Database repository tests

Result: PASS

Output:

```text
test_create_list_get_update_delete_round_trip ... ok
test_missing_note_returns_none ... ok
test_rejects_empty_titles ... ok
test_schema_defines_expected_columns ... ok
test_schema_enforces_update_timestamp_trigger_and_body_default ... ok
```

### API tests

Result: PASS

Output:

```text
test_cors_preflight_allows_frontend_browser_flow ... ok
test_post_list_get_update_delete_round_trip ... ok
test_validation_and_not_found_contract ... ok
```

### Frontend unit/component tests

Result: PASS

Output:

```text
✓ src/App.test.jsx (2 tests)
✓ App > renders the empty state and creates a note
✓ App > edits and deletes notes from the list
```

### Frontend build

Result: PASS

Output:

```text
✓ built in 768ms
```

### Self-review

Result: PASS

Output:

```text
Quality score: 100/100
No heuristic findings.
```

### Scale/readiness review

Result: PASS WITH NOTES

Output:

```text
Verdict: ready_with_notes
No heuristic scale findings.
```

### Spec quality check

Result: PASS WITH NOTES

Output:

```text
Score: 75 / 100
```

### Traceability matrix generation

Result: PASS

Output:

```text
| AC ID | Requirement | Unit | Component | Integration | Contract | E2E | Dev/QA | Evidence | Status |
|---|---|---|---|---|---|---|---|---|---|
| AC-001 | P0-F1-T1-DB; SQLite schema/repository tests and database layer gate. | unmapped | unmapped | unmapped | unmapped | unmapped | unmapped | unmapped | not_started |
| AC-002 | P0-F1-T2-API; Python API contract/integration tests and API layer gate. | unmapped | unmapped | unmapped | unmapped | unmapped | unmapped | unmapped | not_started |
| AC-003 | P0-F1-T3-UI; React component/E2E/visual evidence and frontend layer gate. | unmapped | unmapped | unmapped | unmapped | unmapped | unmapped | unmapped | not_started |
| AC-004 | P0-F1-T4-QA; QA checklist, PM checklist, test evidence, scale/security review, and PR notification. | unmapped | unmapped | unmapped | unmapped | unmapped | unmapped | unmapped | not_started |
```

### Layered test matrix

Result: PASS

Output:

- Captured in `docs/agentic-evidence/spec-a25b601c60-tasks-trd-p0-f1-t1-crud-pipeline-smoke/p0-f1-t4-qa/layered-test-matrix.md`.

### Browser / E2E validation

Result: PASS

Output:

```text
{
  "status": "Note deleted.",
  "notes": 0
}
```

Browser evidence artifact:

- `.agent/stories/spec-a25b601c60-tasks-trd-p0-f1-t1-crud-pipeline-smoke/p0-f1-t4-qa/browser-flow.png`

Run notes:

- The browser flow used the live frontend build served through a temporary reverse proxy so `/api` requests reached the backend on port `8002`.
- The browser run cleared pre-existing notes before exercising create, edit, and delete so the selector state stayed deterministic.

## Coverage notes

- The database layer remains passed.
- The API layer remains passed.
- The frontend unit/component tests and build now pass locally.
- The browser flow passes against the live frontend server, the proxy, and a clean temporary backend database.
- The browser screenshot artifact was captured for the CRUD smoke flow.

## Current verification

This QA pass was rechecked in this workspace with the following results:

- `python3 -m unittest tests.test_database_notes -v` passed.
- `python3 -m unittest backend.tests.test_notes_api -v` passed.
- `npm test` passed.
- `npm run build` passed.
- Node.js was available as `v22.19.0` and npm as `11.6.0`.

The browser/E2E screenshot evidence remains recorded at:

- `.agent/stories/spec-a25b601c60-tasks-trd-p0-f1-t1-crud-pipeline-smoke/p0-f1-t4-qa/browser-flow.png`

## Risks

- Low. The browser flow depends on the frontend proxy target remaining aligned with the local backend port used for QA.
- Low. The Vitest include/exclude pattern should remain narrow so e2e files are not accidentally pulled into unit runs again.
