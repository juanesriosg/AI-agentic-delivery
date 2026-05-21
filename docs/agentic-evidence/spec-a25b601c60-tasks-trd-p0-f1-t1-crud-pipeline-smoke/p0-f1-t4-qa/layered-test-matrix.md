# Layered Test Matrix

## Scope

Task: `p0-f1-t4-qa`
Story: `STORY-crud-pipeline-smoke`
Spec: `SPEC-20260520-crud-pipeline-smoke`

## Matrix

| Layer | Expected validation | Actual status | Evidence |
|---|---|---|---|
| Database | SQLite schema/repository unit tests | PASS | `docs/agentic-evidence/SPEC-20260520-crud-pipeline-smoke/p0-f1-t1-db/test-evidence.md` |
| API | Python API contract/integration tests | PASS | `docs/agentic-evidence/SPEC-20260520-crud-pipeline-smoke/p0-f1-t2-api/test-evidence.md` |
| Frontend unit/component | React component tests | PASS | `docs/agentic-evidence/spec-a25b601c60-tasks-trd-p0-f1-t1-crud-pipeline-smoke/p0-f1-t4-qa/test-evidence.md` |
| Frontend build | React production build | PASS | `docs/agentic-evidence/spec-a25b601c60-tasks-trd-p0-f1-t1-crud-pipeline-smoke/p0-f1-t4-qa/test-evidence.md` |
| Browser/E2E | Playwright or equivalent browser smoke | PASS | `docs/agentic-evidence/spec-a25b601c60-tasks-trd-p0-f1-t1-crud-pipeline-smoke/p0-f1-t4-qa/test-evidence.md` |
| Visual | Screenshots / annotated visual evidence | PASS | `docs/agentic-evidence/spec-a25b601c60-tasks-trd-p0-f1-t1-crud-pipeline-smoke/p0-f1-t4-qa/visual-evidence.md` |
| QA/PM | Checklists and PR notification evidence | PASS | `docs/agentic-evidence/spec-a25b601c60-tasks-trd-p0-f1-t1-crud-pipeline-smoke/p0-f1-t4-qa/qa-checklist.md` |

## Notes

- The database and API layers are already validated.
- The frontend unit, build, browser, and screenshot validations now run in this workspace.
- The browser validation used a temporary reverse proxy so the static frontend build could reach the live API on port `8002`.
- The QA/PM status is PASS because the browser/runtime chain succeeded.
