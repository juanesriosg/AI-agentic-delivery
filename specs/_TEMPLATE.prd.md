---
spec_id: SPEC-YYYYMMDD-short-slug
story_id: STORY-short-slug
title: "Product or feature PRD title"
status: draft
doc_type: prd
source_branch: "dev/<feature-or-story>"
target_branch: "dev/<feature-or-story>"
manager_github_user: "@juanesriosg"
created_at: "YYYY-MM-DD"
updated_at: "YYYY-MM-DD"
---

# PRD Master: <PROJECT_NAME_OR_FEATURE>

## 0. How This PRD Should Be Used by AI Agents

- Treat this PRD as the product source of truth for scope, requirements, priorities, product rules, assumptions, and open questions.
- Do not invent content for `TBD` fields. Keep them as `TBD` and list them under Open Questions or Blocked Items.
- If this PRD conflicts with a backlog item, sprint note, TRD, task list, or prior summary, identify the conflict and ask for clarification before changing authoritative scope.
- Reference exact sections from this PRD when creating implementation plans, TRDs, task lists, QA checklists, and PR summaries.

## 1. Product Vision & Context

### 1.1 Summary

- **Product name:** <PRODUCT_NAME>
- **One-line description:** <ONE_LINE_DESCRIPTION>
- **Primary user type(s):**
  - <PRIMARY_USER_TYPE_1>
  - <PRIMARY_USER_TYPE_2>

### 1.2 Purpose & Vision

- **Purpose of the MVP / change:**
  - <WHAT_THIS_WORK_VALIDATES_OR_ENABLES>
- **Long-term vision:**
  - <HOW_THIS_CAN_EVOLVE_IF_SUCCESSFUL>

### 1.3 Background & Motivation

- **Problem / pain point:** <PROBLEM_OR_PAIN_POINT>
- **Who has this problem:** <AFFECTED_USERS_OR_STAKEHOLDERS>
- **Why now:** <WHY_NOW>

### 1.4 Goals & Success Criteria

| Goal ID | Goal | Success criteria | Priority | Status |
|---|---|---|---|---|
| G-001 | <GOAL> | <OBSERVABLE_SUCCESS_SIGNAL> | P0 | proposed |

### 1.5 Non-Goals

- <NON_GOAL_1>
- <NON_GOAL_2>

### 1.6 Scope In / Out

#### In Scope

- <IN_SCOPE_ITEM_1>
- <IN_SCOPE_ITEM_2>

#### Out of Scope

- <OUT_OF_SCOPE_ITEM_1>
- <OUT_OF_SCOPE_ITEM_2>

## 2. Users, Use Cases & Requirements

### 2.1 Personas

| Persona | Description | Needs | Notes |
|---|---|---|---|
| <PERSONA_NAME> | <PERSONA_DESCRIPTION> | <PERSONA_NEEDS> | <NOTES> |

### 2.2 Top Use Cases

| Use Case ID | Use case | Primary persona | Expected outcome | Priority |
|---|---|---|---|---|
| UC-001 | As a <persona>, I want <action> so that <value>. | <PERSONA> | <OUTCOME> | P0 |

### 2.3 Functional Requirements

Group by feature. Every requirement must be observable and testable.

#### 2.3.1 Feature: <FEATURE_NAME> (P0)

- **User story:** As a <persona>, I want <capability> so that <benefit>.
- **System shall:**
  - FR-001: <REQUIREMENT>
  - FR-002: <REQUIREMENT>
- **Edge cases / validations:**
  - <EDGE_CASE_OR_VALIDATION>

### 2.4 Prioritization

- **P0:** required for current committed scope.
- **P1:** important, but not required for current committed scope.
- **P2:** useful enhancement.
- **P3:** future or optional work.

### 2.5 Acceptance Criteria

| Acceptance ID | Related requirement | Acceptance criterion | Validation method | Status |
|---|---|---|---|---|
| AC-001 | FR-001 | <OBSERVABLE_CRITERION> | <TEST_OR_QA_METHOD> | proposed |

## 3. AI / LLM-Specific Design

Use `Not applicable` if this work does not involve AI behavior.

- **Role of AI in the product:** <ROLE_OF_AI_OR_NOT_APPLICABLE>
- **Inputs to the model:** <USER_SYSTEM_AND_DERIVED_INPUTS>
- **Grounding data:** <INTERNAL_OR_EXTERNAL_CONTEXT>
- **Required behavior:** <REQUIRED_MODEL_BEHAVIOR>
- **Disallowed behavior:** <DISALLOWED_MODEL_BEHAVIOR>
- **Output format:** <MODEL_OUTPUT_FORMAT>
- **Guardrails:** <SAFETY_OR_PRODUCT_GUARDRAILS>
- **Failure modes:** <EXPECTED_FAILURE_HANDLING>

## 4. Non-Functional Requirements

| Area | Requirement | Target / constraint | Validation method |
|---|---|---|---|
| Performance | <PERFORMANCE_REQUIREMENT> | <TARGET> | <VALIDATION> |
| Security & privacy | <SECURITY_REQUIREMENT> | <TARGET> | <VALIDATION> |
| Usability & accessibility | <UX_A11Y_REQUIREMENT> | <TARGET> | <VALIDATION> |
| Reliability & observability | <RELIABILITY_REQUIREMENT> | <TARGET> | <VALIDATION> |
| Maintainability | <MAINTAINABILITY_REQUIREMENT> | <TARGET> | <VALIDATION> |

## 5. Technical Architecture & Data

### 5.1 High-Level Architecture

<HIGH_LEVEL_ARCHITECTURE>

### 5.2 Core Entities

| Entity | Purpose | Key fields | Notes |
|---|---|---|---|
| <ENTITY_NAME> | <ENTITY_PURPOSE> | <KEY_FIELDS> | <NOTES> |

### 5.3 Canonical vs Snapshot / Data Persistence

- **Canonical data:** <CANONICAL_DATA_RULES>
- **Snapshot data:** <SNAPSHOT_DATA_RULES>
- **Historical records:** <HISTORICAL_RECORD_RULES>
- **Temporary or derived data:** <TEMPORARY_OR_DERIVED_DATA_RULES>

### 5.4 External Services

| Service | Purpose | Required / optional | Notes |
|---|---|---|---|
| <SERVICE_NAME> | <SERVICE_PURPOSE> | <REQUIRED_OR_OPTIONAL> | <NOTES> |

### 5.5 Deployment / Environment Assumptions

- <DEPLOYMENT_OR_ENVIRONMENT_ASSUMPTION>

### 5.6 Open Technical Decisions

| Decision ID | Question | Options / context | Status | Owner |
|---|---|---|---|---|
| TD-001 | <QUESTION> | <OPTIONS_OR_CONTEXT> | Open Question | <OWNER> |

## 6. Product Rules

### 6.1 Current Product Rules

- <PRODUCT_RULE>

### 6.2 Business Rules

- <BUSINESS_RULE>

### 6.3 Role / Access Rules

- <ROLE_OR_ACCESS_RULE>

### 6.4 Workflow Rules

- <WORKFLOW_RULE>

### 6.5 Data Rules

- <DATA_RULE>

## 7. Open Questions / Assumptions

### 7.1 Open Questions

| Question ID | Question | Context | Owner | Status |
|---|---|---|---|---|
| Q-001 | <QUESTION> | <CONTEXT> | <OWNER> | Open Question |

### 7.2 Assumptions

| Assumption ID | Assumption | Reason | Validation needed | Status |
|---|---|---|---|---|
| A-001 | <ASSUMPTION> | <REASON> | <VALIDATION_NEEDED> | Assumption |

### 7.3 Blocked Items

| Blocked ID | Item | Blocking dependency | Required resolution | Owner | Status |
|---|---|---|---|---|---|
| B-001 | <ITEM> | <BLOCKING_DEPENDENCY> | <REQUIRED_RESOLUTION> | <OWNER> | Blocked Item |

## 8. Change Log

| Date | Change | Type | Approved by | Notes |
|---|---|---|---|---|
| YYYY-MM-DD | <CHANGE> | Confirmed Decision | <APPROVER> | <NOTES> |
