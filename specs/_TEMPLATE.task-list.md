---
spec_id: SPEC-YYYYMMDD-short-slug
story_id: STORY-short-slug
task_id: P0-F0-T1
title: "Task list title"
status: draft
doc_type: task_list
source_trd: "specs/<story-or-feature>/trds/trd-p0-f0-t1-short-slug.md"
source_prd: "specs/<story-or-feature>/prd.md"
source_implementation_plan: "specs/<story-or-feature>/implementation-plan.md"
source_branch: "dev/<feature-or-story>"
target_branch: "dev/<feature-or-story>"
manager_github_user: "@juanesriosg"
---

# Task List - TASK-ID

## Description

Describe what this task will deliver in one to three short paragraphs. Include what exists after the task is complete and what this task intentionally avoids.

## Business Need

Explain why this task matters for the product or platform. Include the operational, cost, reliability, data quality, or user outcome that this task enables.

## Requirements

List task-level requirements using stable IDs. Every requirement should map to the TRD and to at least one task item.

- FR-001: Replace with a task-level requirement.
- FR-002: Replace with a task-level requirement.
- NFR-COST-001: Replace with cost or resource guardrail when relevant.
- NFR-REL-001: Replace with reliability or idempotency guardrail when relevant.
- NFR-SEC-001: Replace with security or approval guardrail when relevant.

## Design

Describe the implementation design for this task. Keep it scoped to one responsibility. State the main modules, adapters, commands, or documents to create or update.

## Architecture

Describe how this task fits the system architecture. Mention relevant boundaries such as worker runtime, orchestrator, storage, DynamoDB state, Terraform, CloudWatch, or data lake when applicable.

## Data Model

Describe data entities, fields, schema, indexes, retention, and migration behavior touched by this task. If not applicable, explain why in a full sentence and name any future entities only as context.

## API Contract

Describe endpoints, CLI contracts, event payloads, manifest shape, environment variables, or service interfaces touched by this task. If not applicable, explain why in a full sentence.

## Cloud Infrastructure

Describe AWS or Terraform components touched by this task. If not applicable, explicitly state that the task does not create or modify AWS resources and list any cloud guardrails that still apply.

## Testing Strategy

Describe required validation commands and evidence. Include unit, integration, contract, Terraform plan, Docker smoke, E2E, visual, or accessibility notes as applicable.

## Layer Order

State database and data-model, API and backend, frontend and UI, and cloud execution order for this task. Mark layers that do not apply with a full-sentence explanation.

```text
database/data model: replace with required or not applicable and why
api/backend: replace with required or not applicable and why
frontend/ui: replace with required or not applicable and why
cloud/terraform: replace with required or not applicable and why
```

## Programming Paradigm

State the selected approach and why.

```text
selected: replace with data-driven, object-oriented, event-driven, functional-procedural, hybrid, or documentation-first
reason: replace with why this is the simplest correct approach
patterns to use: replace with adapter, repository, strategy, or none
patterns to avoid: god service, hidden global state, broad refactor, unrelated changes
```

## Source Documents

- PRD: `specs/<story-or-feature>/prd.md`
- Implementation plan: `specs/<story-or-feature>/implementation-plan.md`
- TRD: `specs/<story-or-feature>/trds/trd-<task-id>-<short-slug>.md`

## Acceptance Criteria Coverage

Map every TRD acceptance criterion to at least one task.

| AC ID | Covered by task(s) | Validation |
|---|---|---|
| AC-001 | 1.1, 2.1 | Replace with validation method. |

## Relevant Files

- **New** `path/to/new-file` - short purpose.
- **Existing** `path/to/existing-file` - short purpose.

### Notes

- Important implementation notes or open items derived from the TRD.
- Ambiguities or open questions that should be clarified before implementation.

## Tasks

- [ ] 1.0 Parent task title
  - [ ] 1.1 Sub-task no larger than half a day.
  - [ ] 1.2 Sub-task no larger than half a day.
- [ ] 2.0 Parent task title
  - [ ] 2.1 Sub-task no larger than half a day.
  - [ ] 2.2 Sub-task no larger than half a day.
- [ ] 3.0 Validation, evidence, and documentation
  - [ ] 3.1 Run the targeted validation from the TRD and capture output.
  - [ ] 3.2 Update evidence under `docs/agentic-evidence/<spec-id>/<task-id>/`.
  - [ ] 3.3 Update PR notification with scope, validation, risk, rollback, and files worth review.

## Validation Checklist

- [ ] Every FR-* from the TRD maps to at least one task.
- [ ] Every AC-* from the TRD maps to validation evidence or a documented gap.
- [ ] Data/API/frontend work follows database to API to frontend order when applicable.
- [ ] UI work has visual and accessibility evidence, or an explicit non-applicable note.
- [ ] High-risk work has approval or is blocked.
- [ ] The Description through Programming Paradigm sections are complete and have no unresolved placeholders before `ready_for_agents`.
- [ ] Terraform changes are plan-only unless human approval explicitly allows apply.
- [ ] AWS Well-Architected cost, security, reliability, operational, performance, and sustainability tradeoffs are noted when applicable.

---

Task list created: tasks-TRD-basename.md. Ready for review.
