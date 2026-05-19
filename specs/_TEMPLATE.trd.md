---
spec_id: SPEC-YYYYMMDD-short-slug
story_id: STORY-short-slug
task_id: P0-F0-T1
title: "TRD title"
status: draft
doc_type: trd
source_prd: "specs/<story-or-feature>/prd.md"
source_implementation_plan: "specs/<story-or-feature>/implementation-plan.md"
source_branch: "dev/<feature-or-story>"
target_branch: "dev/<feature-or-story>"
manager_github_user: "@juanesriosg"
---

# Task Requirements Document (TRD) - <Task ID(s)>

## 0. Purpose of this TRD

- Short description of the task(s) this TRD covers.
- How this TRD relates to the PRD and Implementation Plan.

## 1. Context & Links

- **Related PRD sections:**
  - <PRD_SECTION>
- **Related Implementation Plan items:**
  - <TASK_ID_AND_TITLE>
- **Base repos and local paths, if provided:**
  - Frontend: <PATH_OR_TBD>
  - Backend: <PATH_OR_TBD>
- **Relevant files / modules to inspect:**
  - <FILE_OR_DIRECTORY>
- **External URLs or docs, if provided:**
  - <URL_OR_DOC_REF>
- **Dependencies on other tasks:**
  - <TASK_IDS_OR_NONE>

## 2. Goals & Non-Goals

- **Goals:**
  - <WHAT_MUST_BE_DELIVERED>
- **Non-Goals / Out of scope:**
  - <WHAT_WILL_NOT_BE_DONE>

## 3. Functional Requirements (Task-Level)

- **High-level description:**
  - <ONE_TO_THREE_BULLETS>
- **Detailed requirements:**
  - FR-001: <REQUIREMENT>
  - FR-002: <REQUIREMENT>
- **Edge cases & validations:**
  - <EDGE_CASE_OR_VALIDATION>

## 4. Data & Schema Requirements

Use `Not applicable` when the task does not touch data or schema.

- **Existing models to reference:**
  - <MODEL_OR_NOT_APPLICABLE>
- **New or updated fields:**
  - <FIELD_DETAILS_OR_NOT_APPLICABLE>
- **Constraints:**
  - <INDEX_UNIQUE_REFERENCE_RULES_OR_NOT_APPLICABLE>
- **Migration notes:**
  - <MIGRATION_AND_ROLLBACK_EXPECTATIONS_OR_NOT_APPLICABLE>

## 5. API / Service Requirements

Use `Not applicable` when the task does not touch APIs or services.

- **New endpoints or handlers:**
  - <METHOD_ROUTE_PURPOSE_OR_NOT_APPLICABLE>
- **Request / response shapes:**
  - <SHAPE_OR_NOT_APPLICABLE>
- **Error handling expectations:**
  - <ERROR_RULES_OR_NOT_APPLICABLE>

## 6. Frontend / UX Requirements

Use `Not applicable` when the task has no user-facing UI.

- **Pages / components impacted:**
  - <ROUTES_OR_COMPONENTS>
- **State / interactions:**
  - <EXPECTED_BEHAVIOR>
- **Copy / labels:**
  - <CRITICAL_TEXT>
- **Visual evidence required:**
  - yes/no; <VIEWPORTS_AND_STATES>

## 7. Acceptance Criteria

- AC-001: <TESTABLE_CRITERION>
- AC-002: <TESTABLE_CRITERION>

## 8. Testing and Evidence Requirements

| Test type | Required? | Scope | Evidence |
|---|---|---|---|
| Unit | yes/no | <SCOPE> | <COMMAND_OR_GAP> |
| Component | yes/no | <SCOPE> | <COMMAND_OR_GAP> |
| Integration | yes/no | <SCOPE> | <COMMAND_OR_GAP> |
| Contract | yes/no | <SCOPE> | <COMMAND_OR_GAP> |
| E2E | yes/no | <SCOPE> | <COMMAND_OR_GAP> |
| Visual QA | yes/no | <SCOPE> | <SCREENSHOTS_OR_GAP> |
| Accessibility QA | yes/no | <SCOPE> | <CHECKLIST_OR_GAP> |

## 9. Risks, Constraints & Trade-offs

- **Risks:**
  - <RISK>
- **Constraints:**
  - <CONSTRAINT>
- **Proposed mitigations:**
  - <MITIGATION>

## 10. Open Questions

- Q-001: <QUESTION_NEEDING_USER_ANSWER>

## 11. Assumptions

- A-001: <ASSUMPTION_TO_VALIDATE>
