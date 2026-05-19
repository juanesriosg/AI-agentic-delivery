# Skill: Create Task List

## Purpose

Convert a single TRD into an executable task checklist with parent tasks, sub-tasks, relevant files, and validation coverage.

## Operating context

Use this skill after a TRD exists, or when the manager asks for a task list. The canonical template is `specs/_TEMPLATE.task-list.md`.

## Principles

- Base the task list only on the TRD and explicitly linked documents.
- Keep sub-tasks small enough for half a day of focused work or less.
- Map every FR and AC from the TRD to work and validation.
- Order layered work as database/data model, API/backend, frontend/UI, then validation and docs.

## Procedure

1. Read the TRD and optional file name.
2. Draft 4-7 parent tasks first when interactive review is needed.
3. Expand each parent task into 3-7 concrete sub-tasks.
4. Fill Relevant Files with new/existing paths and one-line purposes.
5. Add Acceptance Criteria Coverage mapping each AC to tasks and validation.
6. Add validation, evidence, and documentation tasks.
7. Keep `status: draft` until the task list is ready to drive implementation.

## Quality bar

A task list is ready when an implementation agent can execute it directly and a reviewer can trace every task back to a TRD requirement and acceptance criterion.

## Uncertainty behavior

Do not add new behavior that is not in the TRD. Put ambiguities in Notes and ask focused clarification before implementation starts.

## Feedback hooks

After implementation, update checkboxes and notes only when the repo workflow calls for committed evidence. Do not move completed task lists to archival folders without approval.
