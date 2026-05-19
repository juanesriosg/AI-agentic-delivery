# Skill: Create TRD

## Purpose

Create a task requirements document for one implementation-plan task or a tight task cluster.

## Operating context

Use this skill when a task needs an implementation-ready contract. The canonical template is `specs/_TEMPLATE.trd.md`.

## Principles

- A TRD must be usable without rereading the full PRD or implementation plan.
- Keep task scope narrow enough for a one-responsibility PR.
- Be explicit about data/schema, API/service, frontend/UX, acceptance criteria, risks, assumptions, and open questions.
- Do not resolve conflicts between upstream documents by guessing.

## Procedure

1. Require the PRD, implementation plan, and task ID.
2. Read the matching implementation-plan row and related PRD sections.
3. Populate context, links, dependencies, goals, non-goals, functional requirements, and affected files.
4. Mark data/schema, API/service, and frontend/UX as either concrete or `Not applicable`.
5. Add acceptance criteria with `AC-001` style IDs.
6. Add a test and evidence matrix for relevant levels.
7. List risks, constraints, open questions, and assumptions.
8. Keep `status: draft` until a task list or implementation agent can use it directly.

## Quality bar

A good TRD lets a junior implementation agent produce the right change, tests, evidence, and rollback notes without making product or architecture decisions.

## Uncertainty behavior

Ask clarifying questions before drafting when missing information changes behavior, data, security, API contract, or validation. Remaining gaps must be visible as `TBD`, Open Questions, or Assumptions.

## Feedback hooks

When implementation feedback changes the contract, update the TRD and cite the source of the decision.
