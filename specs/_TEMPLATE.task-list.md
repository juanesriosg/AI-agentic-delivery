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

# Task List - <TRD file name or Task ID(s)>

## Source Documents

- PRD: `specs/<story-or-feature>/prd.md`
- Implementation plan: `specs/<story-or-feature>/implementation-plan.md`
- TRD: `specs/<story-or-feature>/trds/trd-<task-id>-<short-slug>.md`

## Acceptance Criteria Coverage

Map every TRD acceptance criterion to at least one task.

| AC ID | Covered by task(s) | Validation |
|---|---|---|
| AC-001 | 1.1, 2.1 | <TEST_OR_QA_METHOD> |

## Relevant Files

- **New** `path/to/new-file` - <short purpose>
- **Existing** `path/to/existing-file` - <short purpose>

### Notes

- <Important implementation notes or open items derived from the TRD>
- <Ambiguities or TBDs that should be clarified before implementation>

## Tasks

- [ ] 1.0 <Parent task title>
  - [ ] 1.1 <Sub-task no larger than half a day>
  - [ ] 1.2 <Sub-task no larger than half a day>
- [ ] 2.0 <Parent task title>
  - [ ] 2.1 <Sub-task no larger than half a day>
  - [ ] 2.2 <Sub-task no larger than half a day>
- [ ] 3.0 Validation, evidence, and documentation
  - [ ] 3.1 Run the targeted validation from the TRD and capture output.
  - [ ] 3.2 Update evidence under `docs/agentic-evidence/<spec-id>/<task-id>/`.
  - [ ] 3.3 Update PR notification with scope, validation, risk, rollback, and files worth review.

## Validation Checklist

- [ ] Every FR-* from the TRD maps to at least one task.
- [ ] Every AC-* from the TRD maps to validation evidence or a documented gap.
- [ ] Data/API/frontend work follows database -> API -> frontend order when applicable.
- [ ] UI work has visual and accessibility evidence, or an explicit non-applicable note.
- [ ] High-risk work has approval or is blocked.

---

Task list created: tasks-<TRD-basename>.md. Ready for review.
