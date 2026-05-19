# Skill: Create PRD

## Purpose

Create a product requirements document using the PRD Master structure from the reference repos.

## Operating context

Use this skill when a manager asks for a PRD, product spec, MVP requirements, or product source of truth. The canonical template is `specs/_TEMPLATE.prd.md`.

## Principles

- Treat the PRD as product truth, not an implementation checklist.
- Preserve priorities, product rules, open questions, assumptions, blocked items, and change log separately.
- Do not invent content for vague or `TBD` fields.
- Keep product decisions traceable to user input or approved source documents.

## Procedure

1. Read any provided brief, screenshots, issues, notes, and existing docs.
2. Ask grouped discovery questions when required fields are missing.
3. Populate `specs/<story-or-feature>/prd.md` from `specs/_TEMPLATE.prd.md`.
4. Mark unresolved details as `TBD` and list them under Open Questions or Blocked Items.
5. Assign stable IDs for goals, use cases, functional requirements, acceptance criteria, decisions, assumptions, and blockers.
6. Keep `status: draft` until product scope and acceptance criteria are concrete enough for planning.
7. When ready, change only the intended document to `status: ready_for_agents`.

## Quality bar

A strong PRD lets another agent create an implementation plan without guessing product behavior, user value, priorities, or non-goals.

## Uncertainty behavior

Ask focused questions when ambiguity affects behavior, risk, data shape, public contract, ownership, or validation. Continue safe work by recording known facts and explicit gaps.

## Feedback hooks

Record manager corrections in the PRD change log. If the correction generalizes to agent behavior, capture feedback through the self-improvement process instead of silently changing policy.
