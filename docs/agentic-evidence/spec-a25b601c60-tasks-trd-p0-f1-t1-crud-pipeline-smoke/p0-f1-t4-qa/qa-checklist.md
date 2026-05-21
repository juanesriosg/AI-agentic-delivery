# QA Checklist

## Spec comprehension summary

Business goal: prove the autonomous CRUD smoke pipeline can be validated end to end with honest evidence.
Technical goal: verify the passed lower layers and record the exact reason the frontend/E2E layer cannot complete in this runtime.
Acceptance criteria with IDs:
- AC-001: Database layer evidence exists and remains passed.
- AC-002: API layer evidence exists and remains passed.
- AC-003: Frontend UI evidence includes unit, build, browser, and screenshot validation.
- AC-004: QA evidence records pass status accurately.
Assumptions:
- This task may fix narrow in-scope regressions that block QA evidence.
- The browser step is valid when Chromium is installed and the local frontend/backend servers are reachable.
Clarifications needed:
- None.
Safe progress while waiting:
- Collect validation outputs and write reviewable evidence.
Test traceability:
- `python3 -m unittest tests.test_database_notes -v`
- `python3 -m unittest backend.tests.test_notes_api -v`
- `npm test`
- `npm run build`
- `node --input-type=module ... Playwright browser flow against http://127.0.0.1:4178/`
- `python3 .ai/scripts/agent-self-review.py --format markdown`
- `python3 .ai/scripts/check-scale-readiness.py --format markdown`
- `python3 .ai/scripts/spec-quality-check.py --spec specs/crud-pipeline-smoke/tasks/tasks-trd-p0-f1-t1-crud-pipeline-smoke.md --format markdown`
- `python3 .ai/scripts/generate-test-matrix.py --spec specs/crud-pipeline-smoke/tasks/tasks-trd-p0-f1-t1-crud-pipeline-smoke.md`

## Functional checklist

- [x] Database layer gate evidence reviewed.
- [x] API layer gate evidence reviewed.
- [x] The UI source and test files were inspected for accessibility and CRUD coverage.
- [x] The frontend test harness was repaired so Vitest runs only the component tests.
- [x] Spec quality and traceability outputs were collected for this QA task.
- [x] Frontend unit/component tests executed locally.
- [x] Frontend build executed locally.
- [x] Browser/E2E flow executed locally.
- [x] Visual screenshot evidence captured.
- [x] The browser flow used a temporary local reverse proxy and cleared pre-existing notes before running CRUD assertions.

## Test checklist

- [x] `python3 -m unittest tests.test_database_notes -v` passed.
- [x] `python3 -m unittest backend.tests.test_notes_api -v` passed.
- [x] `npm test` passed after scoping Vitest to `src/**` and fixing the component locator regression.
- [x] `npm run build` passed.
- [x] Browser/E2E CRUD flow passed against the live frontend/backend servers.
- [x] `python3 .ai/scripts/agent-self-review.py --format markdown` returned no heuristic findings.
- [x] `python3 .ai/scripts/check-scale-readiness.py --format markdown` returned `ready_with_notes`.
- [x] `python3 .ai/scripts/spec-quality-check.py --spec specs/crud-pipeline-smoke/tasks/tasks-trd-p0-f1-t1-crud-pipeline-smoke.md --format markdown` returned a 75/100 task-list report.
- [x] `python3 .ai/scripts/generate-test-matrix.py --spec specs/crud-pipeline-smoke/tasks/tasks-trd-p0-f1-t1-crud-pipeline-smoke.md` returned the current unmapped traceability matrix.

## Regression checklist

- [x] The evidence reports the real state of the repo rather than inventing a frontend pass.
- [x] The earlier blocker was specific and reproducible.
- [x] Lower-layer validation remains intact and documented.
- [x] The PM layer gate is recorded as passed after browser/runtime validation succeeded.

## Pass / Fail

- Status: PASS
- Notes: The QA task now has direct evidence for DB, API, frontend unit/build, browser/E2E, and screenshot validation in this workspace. The local rerun in this pass confirmed the DB/API/frontend unit/build checks, and the browser artifact remains recorded from the successful live E2E run.
