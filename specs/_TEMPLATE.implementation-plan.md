---
spec_id: SPEC-YYYYMMDD-short-slug
story_id: STORY-short-slug
title: "Implementation plan title"
status: draft
doc_type: implementation_plan
source_prd: "specs/<story-or-feature>/prd.md"
source_branch: "dev/<feature-or-story>"
target_branch: "dev/<feature-or-story>"
manager_github_user: "@juanesriosg"
---

# Implementation Plan

## 1. Short PRD Understanding

Summarize the PRD in 8-10 lines maximum.

- Product / feature: <PRODUCT_OR_FEATURE>
- Primary business goal: <BUSINESS_GOAL>
- MVP / committed scope: <P0_SCOPE>
- Priority order: agents must execute P0 -> P1 -> P2 -> P3 unless this plan records an approved sequencing override.
- Reference repositories or code areas: <REPOS_OR_AREAS_TO_INSPECT>

## 2. Questions for Clarification

Use this section for PRD ambiguity, contradictions, or TBDs.

| Question ID | Blocking? | Question | Safe progress while waiting |
|---|---|---|---|
| Q-001 | yes/no | <QUESTION> | <SAFE_PROGRESS> |

If there are no blocking questions, write:

> At this stage, there are no blocking questions. Remaining TBDs are captured as code-level clarification tasks inside the implementation plan.

## 3. Current Execution Priority

- **Single active source:** this implementation plan is the active backlog for the PRD.
- **Active lane:** <CURRENT_PHASE_OR_TASK_ID>
- **Closed / archival lanes:** <CLOSED_PHASES_OR_NONE>
- **Blocked high-risk areas:** <AUTH_DB_INFRA_SECURITY_OR_PUBLIC_API_BLOCKERS>

## 4. Implementation Plan by Phases

Create phases in priority order. A phase may contain only one responsibility if the work is small.

### Phase 0 - Foundations & Architecture Alignment (P0)

| Task ID | Title | Priority | Type | PRD reference | Description | Repos / areas | Dependencies | Deliverable |
|---|---|---|---|---|---|---|---|---|
| P0-F0-T1 | <TITLE> | P0 | Backend / Frontend / Database / Cloud / Security / Docs / Cross-cutting | Section <N> - <NAME> | <ACTIONABLE_DESCRIPTION>. Code-level clarification task: inspect <FILES_OR_MODULES> before implementation. | <REPO_OR_AREA> | None | <CONCRETE_OUTPUT> |

### Phase 1 - Core P0 Flow (P0)

| Task ID | Title | Priority | Type | PRD reference | Description | Repos / areas | Dependencies | Deliverable |
|---|---|---|---|---|---|---|---|---|
| P0-F1-T1 | <TITLE> | P0 | <TYPE> | Section <N> - <NAME> | <ACTIONABLE_DESCRIPTION> | <REPO_OR_AREA> | P0-F0-T1 | <CONCRETE_OUTPUT> |

### Phase 2 - P1 Enhancements

| Task ID | Title | Priority | Type | PRD reference | Description | Repos / areas | Dependencies | Deliverable |
|---|---|---|---|---|---|---|---|---|
| P1-F2-T1 | <TITLE> | P1 | <TYPE> | Section <N> - <NAME> | <ACTIONABLE_DESCRIPTION> | <REPO_OR_AREA> | <TASK_IDS> | <CONCRETE_OUTPUT> |

## 5. Task ID Rules

- Use stable IDs such as `P0-F0-T1`.
- Every task must map to a PRD section and at least one deliverable.
- Every task that depends on existing code or a TBD must include a `Code-level clarification task:` sentence naming exact files, modules, routes, or folders to inspect.
- If a task touches database, API, and frontend, split it or sequence it by database -> API -> frontend.

## 6. Traceability Summary

| PRD requirement / AC | Implementation task IDs | Validation |
|---|---|---|
| FR-001 / AC-001 | P0-F0-T1 | <TEST_OR_QA_METHOD> |
