---
spec_id: SPEC-YYYYMMDD-short-slug
story_id: STORY-short-slug
title: "Short product or feature title"
status: draft
doc_type: spec_package
source_branch: "dev/<feature-or-story>"
target_branch: "dev/<feature-or-story>"
manager_github_user: "@juanesriosg"
---

# Spec Package Template

Use this folder structure for implementation-ready specs:

```text
specs/<story-or-feature>/
  prd.md
  implementation-plan.md
  trds/
    trd-<task-id>-<short-slug>.md
  tasks/
    tasks-trd-<task-id>-<short-slug>.md
```

## Source-of-truth order

Agents must read the documents in this order:

1. `prd.md` - product scope, business rules, users, priorities, acceptance criteria.
2. `implementation-plan.md` - phase/task sequencing and priority order.
3. `trds/*.md` - implementation-ready contract for one task or tight task cluster.
4. `tasks/*.md` - executable checklist for one TRD.

When documents conflict, the more authoritative upstream document wins unless the downstream document records an approved change. Agents must surface the conflict and ask for clarification instead of guessing.

## Required package lifecycle

| Stage | Output | Required before next stage |
|---|---|---|
| Product definition | `prd.md` | Goals, scope, priorities, acceptance criteria, open questions |
| Technical planning | `implementation-plan.md` | Phases, task IDs, dependencies, deliverables |
| Task contract | `trds/trd-*.md` | Task-level FRs, data/API/UI requirements, acceptance criteria |
| Execution checklist | `tasks/tasks-trd-*.md` | Parent tasks, sub-tasks, relevant files, validation mapping |

## Readiness rules

- Keep each file `status: draft` until placeholders are resolved.
- Change only the execution document that should trigger work to `status: ready_for_agents`.
- Prefer dispatching the most granular ready file:
  - task list for implementation work;
  - TRD when the task list still needs generation;
  - implementation plan when TRDs still need generation;
  - PRD when the plan still needs generation.
- Do not dispatch directly from a vague PRD when task IDs, acceptance criteria, dependencies, or validation are missing.

## Templates

- PRD: `specs/_TEMPLATE.prd.md`
- Implementation plan: `specs/_TEMPLATE.implementation-plan.md`
- TRD: `specs/_TEMPLATE.trd.md`
- Task list: `specs/_TEMPLATE.task-list.md`
