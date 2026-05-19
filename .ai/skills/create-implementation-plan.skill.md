# Skill: Create Implementation Plan

## Purpose

Convert a PRD into a phase-based implementation plan with stable task IDs, priorities, dependencies, and deliverables.

## Operating context

Use this skill after `prd.md` exists, or when the manager asks for an implementation plan. The canonical template is `specs/_TEMPLATE.implementation-plan.md`.

## Principles

- Respect PRD priority order: P0, then P1, then P2, then P3 unless an approved override is recorded.
- Every task must reference a PRD section and produce a concrete deliverable.
- Use code-level clarification tasks instead of guessing from vague references.
- Split by responsibility and layer order, not by arbitrary file count.

## Procedure

1. Read the PRD completely, including open questions and non-goals.
2. Write a short PRD understanding and clarification table.
3. Define phases in priority order.
4. Create task rows with `Task ID`, `Title`, `Priority`, `Type`, `PRD reference`, `Description`, `Repos / areas`, `Dependencies`, and `Deliverable`.
5. Add code-level clarification tasks wherever existing code, another repo, or a `TBD` affects the implementation.
6. Add a traceability table from PRD requirements and acceptance criteria to task IDs.
7. Keep the plan `status: draft` until task IDs, dependencies, and validation paths are explicit.

## Quality bar

An implementation plan is ready when a TRD can be created for each task without rereading the whole PRD or inventing missing scope.

## Uncertainty behavior

Blocking ambiguity goes into the clarification table. Non-blocking ambiguity stays inside the relevant task as a code-level clarification task with safe progress noted.

## Feedback hooks

When work closes or scope changes, update the current execution priority and relevant task rows instead of relying on stale summaries.
