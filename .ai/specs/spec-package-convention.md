# PRD/TRD/Task Spec Package Convention

This repo supports both the older single-file agentic spec and the richer PRD/TRD/task-list package used in the reference repos.

## Preferred structure

```text
specs/<story-or-feature>/
  prd.md
  implementation-plan.md
  trds/
    trd-<task-id>-<short-slug>.md
  tasks/
    tasks-trd-<task-id>-<short-slug>.md
```

## Document roles

| Document | Role | Should trigger implementation? |
|---|---|---|
| `prd.md` | Product source of truth, priorities, product rules, acceptance criteria | Only when plan/TRDs/tasks do not exist yet |
| `implementation-plan.md` | Phase/task sequence, dependencies, deliverables | Usually triggers TRD creation or task splitting |
| `trds/*.md` | Task-level implementation contract | Can trigger task-list generation or implementation |
| `tasks/*.md` | Executable checklist for one TRD | Preferred implementation trigger |

## Required front matter

Every package document should include:

```yaml
spec_id: SPEC-YYYYMMDD-short-slug
story_id: STORY-short-slug
title: Human title
status: draft
doc_type: prd | implementation_plan | trd | task_list
source_branch: dev/<feature>
target_branch: dev/<feature>
manager_github_user: "@juanesriosg"
```

Use `status: ready_for_agents` only on the most granular document that should start work.

## Agent reading order

When implementing from a task list, agents must read:

1. `AGENTS.md`
2. `.ai/specs/spec-package-convention.md`
3. the task list
4. the linked TRD
5. the linked implementation plan
6. the linked PRD

If the documents conflict, stop the risky path, record the conflict, and ask a focused clarification.
