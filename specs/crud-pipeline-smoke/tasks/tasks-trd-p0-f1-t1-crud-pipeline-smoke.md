---
spec_id: SPEC-20260520-crud-pipeline-smoke
story_id: STORY-crud-pipeline-smoke
task_id: P0-F1-T1
title: "Autonomous CRUD pipeline smoke task list"
status: ready_for_agents
doc_type: task_list
source_trd: "specs/crud-pipeline-smoke/trds/trd-p0-f1-t1-crud-pipeline-smoke.md"
source_prd: "specs/crud-pipeline-smoke/prd.md"
source_implementation_plan: "specs/crud-pipeline-smoke/implementation-plan.md"
source_branch: "dev/crud-pipeline-smoke"
target_branch: "dev/crud-pipeline-smoke"
manager_github_user: "@juanesriosg"
updated_at: "2026-05-21"
---

# Task List - P0-F1-T1

## Description

Deliver a local CRUD smoke app that proves the autonomous SDLC pipeline can create and validate database, Python API, React UI, QA, and PM evidence. The app manages notes and is intentionally small; the valuable output is the pipeline pass/fail evidence.

## Business Need

The manager needs proof that the agentic SDLC can run autonomously on a fresh repo and move work through DB, API, frontend, QA, PM, guardrails, and PR notification gates. This verifies the pipeline behavior after shared agentic files were synced.

## Requirements

- FR-001: Create a SQLite notes schema and repository behavior for create, list, read, update, and delete.
- FR-002: Create a Python API exposing CRUD endpoints with structured validation and not-found errors.
- FR-003: Create a React CRUD page that uses the Python API for list, create, update, and delete.
- FR-004: Create tests and reviewable evidence for database, API, frontend, integration/E2E, visual, accessibility, QA, PM, risk, rollback, and follow-up gaps.
- NFR-REL-001: Record exact environment blockers instead of marking unavailable tests or browser checks as passing.
- NFR-SEC-001: Do not introduce secrets, production data, auth, external services, AWS, Terraform, or deployment.

## Design

Use a small local full-stack structure:

- `database/` for SQLite schema and seed/test notes documentation.
- `backend/` for a Python API and tests.
- `frontend/` for a React CRUD page and tests.
- `docs/agentic-evidence/` for generated pipeline evidence.

The implementation must stay local and one responsibility per task. If a task finds that repo setup is missing, it should add only the minimal setup needed for that layer.

## Architecture

The app uses a local SQLite database as the persistence boundary, a Python API service as the backend boundary, and a React UI as the presentation boundary. The UI calls the API; it must not become a static-only demo unless the evidence records an explicit integration blocker.

## Data Model

`Note` fields:

- `id`: integer primary key.
- `title`: required text.
- `body`: text.
- `created_at`: ISO timestamp.
- `updated_at`: ISO timestamp.

No production migration or cloud database is allowed. Test database files must be ignored or created in temporary paths.

## API Contract

- `GET /api/notes`: list notes.
- `POST /api/notes`: create note from `{ "title": string, "body": string }`.
- `GET /api/notes/{id}`: read one note.
- `PUT /api/notes/{id}`: update note from `{ "title": string, "body": string }`.
- `DELETE /api/notes/{id}`: delete note.
- Empty title returns a validation error.
- Missing note id returns a 404 error.

## Cloud Infrastructure

This task does not create or modify AWS resources, Terraform, deployment workflows, production config, secrets, billing, or auth. If any cloud validation is requested by a tool, mark it not applicable with this rationale.

## Testing Strategy

- Database: schema/repository tests using local SQLite or temporary files.
- API: unit/contract/integration tests against a test database.
- Frontend: component tests and real API/E2E validation when local tooling supports it.
- Visual/accessibility: screenshots or an exact environment blocker.
- QA/PM: evidence files under `docs/agentic-evidence/SPEC-20260520-crud-pipeline-smoke/P0-F1-T1-DB/`, `docs/agentic-evidence/SPEC-20260520-crud-pipeline-smoke/P0-F1-T2-API/`, `docs/agentic-evidence/SPEC-20260520-crud-pipeline-smoke/P0-F1-T3-UI/`, and `docs/agentic-evidence/SPEC-20260520-crud-pipeline-smoke/P0-F1-T4-QA/`.

## Layer Order

```text
database/data model: required first; schema and repository behavior must pass before API completion.
api/backend: required second; API contract and DB-backed behavior must pass before frontend completion.
frontend/ui: required third; UI must integrate with the API or record an exact blocker.
cloud/terraform: not applicable because this is a local-only smoke with no AWS or deployment.
```

## Programming Paradigm

```text
selected: hybrid
reason: Data-driven schema and API contracts keep the smoke small, while simple service/repository boundaries keep DB, API, and UI layers separated.
patterns to use: repository for persistence, adapter boundary for API calls, simple component composition for React.
patterns to avoid: god service, hidden global state, broad refactor, unrelated changes.
```

## Source Documents

- PRD: `specs/crud-pipeline-smoke/prd.md`
- Implementation plan: `specs/crud-pipeline-smoke/implementation-plan.md`
- TRD: `specs/crud-pipeline-smoke/trds/trd-p0-f1-t1-crud-pipeline-smoke.md`

## Acceptance Criteria Coverage

| AC ID | Covered by task(s) | Validation |
|---|---|---|
| AC-001 | P0-F1-T1-DB | SQLite schema/repository tests and database layer gate. |
| AC-002 | P0-F1-T2-API | Python API contract/integration tests and API layer gate. |
| AC-003 | P0-F1-T3-UI | React component/E2E/visual evidence and frontend layer gate. |
| AC-004 | P0-F1-T4-QA | QA checklist, PM checklist, test evidence, scale/security review, and PR notification. |

## Relevant Files

- **New** `database/schema.sql` - SQLite notes schema.
- **New** `database/README.md` - local data model notes and rollback guidance.
- **New** `tests/test_database_notes.py` - database/repository validation.
- **New** `backend/app/main.py` - Python API app.
- **New** `backend/app/repository.py` - SQLite-backed note repository.
- **New** `backend/app/__init__.py` - backend package marker.
- **New** `backend/requirements.txt` - minimal Python API dependencies if needed.
- **New** `backend/tests/test_notes_api.py` - API contract/integration tests.
- **New** `frontend/package.json` - React test/build scripts if needed.
- **New** `frontend/src/App.jsx` - CRUD page.
- **New** `frontend/src/api.js` - API client adapter.
- **New** `frontend/src/App.test.jsx` - React component tests.
- **New** `frontend/e2e/notes-crud.spec.js` - E2E smoke when feasible.
- **New** `docs/agentic-evidence/SPEC-20260520-crud-pipeline-smoke/` - reviewable pipeline evidence.

### Notes

- This is a local smoke. Do not add production deployment or cloud resources.
- If dependencies cannot install, record command, error, and fallback validation in evidence.
- Manager approval is limited to local smoke implementation; high-risk auth, infrastructure, or production data changes remain out of scope and blocked.

## Agentic Split Task Progress

- [x] `P0-F1-T1-DB` Design and implement SQLite database notes model.
- [ ] `P0-F1-T2-API` Build Python API CRUD endpoints.
- [ ] `P0-F1-T3-UI` Build React UI CRUD page.
- [ ] `P0-F1-T4-QA` Run QA E2E and PM evidence.

## Tasks

- [ ] 1.0 Database/data-model task
  - [ ] 1.1 Create local SQLite notes schema.
  - [ ] 1.2 Add repository or schema validation tests.
  - [ ] 1.3 Write database layer evidence and rollback notes.
- [ ] 2.0 API/backend task
  - [ ] 2.1 Add Python CRUD endpoints.
  - [ ] 2.2 Add API contract and integration tests.
  - [ ] 2.3 Write API layer evidence.
- [ ] 3.0 Frontend/UI task
  - [ ] 3.1 Add React CRUD page and API client.
  - [ ] 3.2 Add component, E2E, visual, and accessibility evidence or exact blockers.
  - [ ] 3.3 Write frontend layer evidence.
- [ ] 4.0 Validation, evidence, and documentation
  - [ ] 4.1 Run available validation and capture output.
  - [ ] 4.2 Complete QA and PM checklists.
  - [ ] 4.3 Update PR notification with scope, validation, risk, rollback, and files worth review.

## Validation Checklist

- [ ] Every FR-* from the TRD maps to at least one task.
- [ ] Every AC-* from the TRD maps to validation evidence or a documented gap.
- [ ] Data/API/frontend work follows database to API to frontend order.
- [ ] UI work has visual and accessibility evidence, or an explicit environment blocker.
- [ ] High-risk work outside this smoke is blocked.
- [ ] Terraform and AWS are not applicable because no cloud resources are created.
- [ ] Evidence records exact commands, results, failures, rollback, and follow-up actions.

---

Task list created: tasks-trd-p0-f1-t1-crud-pipeline-smoke.md. Ready for autonomous pipeline verification.

---

Task completed by agentic SDLC.

- Completed task id: `p0-f1-t1-db`
- Completed task title: Design and implement SQLite database notes model.
- Runtime mode: `local`
- Completed at: `2026-05-21T01:06:36Z`
- Evidence: `docs/agentic-evidence/spec-a25b601c60-tasks-trd-p0-f1-t1-crud-pipeline-smoke/p0-f1-t1-db/`

