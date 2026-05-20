---
spec_id: SPEC-20260520-crud-pipeline-smoke
story_id: STORY-crud-pipeline-smoke
title: "Autonomous CRUD Pipeline Smoke PRD"
status: approved
doc_type: prd
source_branch: "dev/crud-pipeline-smoke"
target_branch: "dev/crud-pipeline-smoke"
manager_github_user: "@juanesriosg"
created_at: "2026-05-20"
updated_at: "2026-05-20"
---

# PRD Master: Autonomous CRUD Pipeline Smoke

## 0. How This PRD Should Be Used by AI Agents

Use this PRD as supporting context for the ready task list. Do not expand the product beyond the smoke-test scope.

## 1. Product Vision & Context

### 1.1 Summary

- Product name: Autonomous CRUD Pipeline Smoke
- One-line description: A tiny notes CRUD app used to verify the agentic SDLC can autonomously create database, Python API, React UI, and evidence.
- Primary user type: Internal pipeline verifier.

### 1.2 Purpose & Vision

- Purpose: Prove the pipeline runs end to end, not create a production application.
- Long-term vision: Use this repo as a repeatable autonomous full-stack smoke harness.

### 1.3 Background & Motivation

- Problem / pain point: Pipeline changes can look correct in isolation while failing when asked to create a layered app.
- Who has this problem: The manager and agents relying on autonomous SDLC behavior.
- Why now: The pipeline was synced across repos and needs live verification.

### 1.4 Goals & Success Criteria

| Goal ID | Goal | Success criteria | Priority | Status |
|---|---|---|---|---|
| G-001 | Verify autonomous DB to API to UI execution | Pipeline completes or records exact blockers with evidence | P0 | approved |

### 1.5 Non-Goals

- Production deployment.
- Authentication, authorization, billing, external services, or cloud infrastructure.
- A polished long-term product.

### 1.6 Scope In / Out

#### In Scope

- SQLite schema for notes.
- Python API with CRUD endpoints.
- React page for create, read, update, delete flows.
- Layered tests and evidence.

#### Out of Scope

- Terraform or AWS changes.
- Production database migrations.
- User accounts or secrets.
- Broad refactors of the agentic framework.

## 2. Users, Use Cases & Requirements

### 2.1 Personas

| Persona | Description | Needs | Notes |
|---|---|---|---|
| Pipeline verifier | Manager or agent validating autonomous behavior | Clear pass/fail evidence for the pipeline | Internal only |

### 2.2 Top Use Cases

| Use Case ID | Use case | Primary persona | Expected outcome | Priority |
|---|---|---|---|---|
| UC-001 | As a pipeline verifier, I want agents to create a tiny CRUD app so that I can confirm orchestration works. | Pipeline verifier | Evidence shows DB, API, UI, and QA gates ran | P0 |

### 2.3 Functional Requirements

#### 2.3.1 Feature: Notes CRUD Smoke (P0)

- User story: As a pipeline verifier, I want a small notes app so that the autonomous pipeline can be tested across all app layers.
- System shall:
  - FR-001: Define a SQLite notes table with id, title, body, created_at, and updated_at fields.
  - FR-002: Expose Python API endpoints to list, create, read, update, and delete notes.
  - FR-003: Render a React CRUD page that uses the Python API rather than static-only local state.
  - FR-004: Include tests and evidence for database, API, frontend, integration, visual, QA, and PM gates.
- Edge cases / validations:
  - Empty title is rejected.
  - Missing note id returns a 404 response.
  - UI shows empty, loading, error, create, edit, and delete states or documents exact environment blockers.

### 2.4 Prioritization

- P0: DB schema, API CRUD, React CRUD page, automated or documented validation evidence.
- P1: Styling refinements beyond usable CRUD.

### 2.5 Acceptance Criteria

| Acceptance ID | Related requirement | Acceptance criterion | Validation method | Status |
|---|---|---|---|---|
| AC-001 | FR-001 | SQLite schema and repository tests prove create/list/update/delete behavior. | Python test or equivalent DB-backed validation | approved |
| AC-002 | FR-002 | Python API exposes CRUD endpoints with success and error behavior. | API unit/contract/integration tests | approved |
| AC-003 | FR-003 | React page performs CRUD through the API and renders expected states. | Component or E2E validation plus visual evidence or blocker | approved |
| AC-004 | FR-004 | Evidence records commands, results, layer gates, QA checklist, PM checklist, and rollback notes. | Agentic evidence review | approved |

## 3. AI / LLM-Specific Design

Not applicable. This smoke app does not involve LLM product behavior.

## 4. Non-Functional Requirements

| Area | Requirement | Target / constraint | Validation method |
|---|---|---|---|
| Performance | CRUD smoke should use bounded local data. | No unbounded scans beyond local notes table. | Code review and tests |
| Security & privacy | Do not introduce secrets, auth bypasses, or external network dependencies. | Local-only development app. | Static review and evidence |
| Usability & accessibility | Form controls have labels and usable states. | Basic keyboard and screen-reader labels. | UI evidence or blocker |
| Reliability & observability | Errors are surfaced clearly. | API returns structured errors; UI displays failure state. | API/UI tests |
| Maintainability | Keep DB, API, and UI layers separate. | Clear directories and tests. | Review evidence |

## 5. Technical Architecture & Data

### 5.1 High-Level Architecture

The smoke app uses SQLite for local persistence, a Python API service for CRUD, and a React UI that calls the API.

### 5.2 Core Entities

| Entity | Purpose | Key fields | Notes |
|---|---|---|---|
| Note | Smoke CRUD record | id, title, body, created_at, updated_at | Local SQLite only |

### 5.3 Canonical vs Snapshot / Data Persistence

- Canonical data: SQLite notes table in local development.
- Snapshot data: Not applicable.
- Historical records: Not applicable.
- Temporary or derived data: Test database files may be temporary and ignored.

### 5.4 External Services

| Service | Purpose | Required / optional | Notes |
|---|---|---|---|
| None | No external service required | Not applicable | Keep smoke local |

### 5.5 Deployment / Environment Assumptions

- Local-only validation is enough for this smoke.
- Production deployment is out of scope.

### 5.6 Open Technical Decisions

| Decision ID | Question | Options / context | Status | Owner |
|---|---|---|---|---|
| TD-001 | Which Python framework should be used? | Prefer a lightweight repo-native choice; FastAPI is acceptable if dependencies are documented. | Agent decision | Agent |

## 6. Product Rules

### 6.1 Current Product Rules

- Keep the app small enough to validate the pipeline quickly.

### 6.2 Business Rules

- Smoke data has no business-critical meaning.

### 6.3 Role / Access Rules

- Auth is explicitly out of scope.

### 6.4 Workflow Rules

- Agents must work database/data model first, API/backend second, frontend/UI third, QA/PM last.

### 6.5 Data Rules

- Do not persist real user or production data.

## 7. Open Questions / Assumptions

### 7.1 Open Questions

| Question ID | Question | Context | Owner | Status |
|---|---|---|---|---|
| Q-001 | None blocking. | The task is a pipeline smoke, not a product launch. | Manager | Closed |

### 7.2 Assumptions

| Assumption ID | Assumption | Reason | Validation needed | Status |
|---|---|---|---|---|
| A-001 | Local SQLite, Python, and Node tooling may be installed or bootstrapped by repo scripts. | The repo is a local smoke harness. | Record exact blockers if unavailable. | Accepted |

### 7.3 Blocked Items

| Blocked ID | Item | Blocking dependency | Required resolution | Owner | Status |
|---|---|---|---|---|---|
| B-001 | None. | Not applicable. | Not applicable. | Not applicable. | Closed |

## 8. Change Log

| Date | Change | Type | Approved by | Notes |
|---|---|---|---|---|
| 2026-05-20 | Initial smoke PRD | Confirmed Decision | @juanesriosg | Local pipeline verification |

