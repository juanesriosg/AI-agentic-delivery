# Agentic SDLC v4 — Agile Team Operating System

This repository can run an AI-agent software lifecycle where specialized agents behave like an autonomous agile delivery team.

The v4 goal is not to have one generic coder. The goal is to have a complete delivery system where requirements, design, frontend, backend, cloud, security, testing, product review, release readiness, and logging are handled by specialized agents that exchange feedback and produce evidence before the human AI Project Manager reviews the work.

## Core lifecycle

```text
1. Spec / user story arrives on a watched branch
2. Spec Agent validates and expands requirements
3. Orchestrator creates a story workspace and routes subtasks to specialists
4. Design / UX / architecture agents review the story before coding when relevant
5. Frontend / backend / cloud / data agents implement in focused branches
6. Dev agents run unit, component, integration, E2E, and dev tests as appropriate
7. QA agents create checklists and test the implementation
8. QA findings are sent back to the correct implementation agent
9. Dev agents fix issues and rerun validation
10. QA regression verifies fixes
11. Product Manager Agent reviews intuitiveness, accessibility, business fit, and integration
12. PM findings go back to design/dev agents
13. QA verifies again after product changes
14. PM accepts
15. Release agent prepares promotion to qa-user / staging / prod-ready according to policy
16. PR notification is sent to the human AI PM with screenshots, evidence, logs, risks, and summary
```

## Role of the human AI Project Manager

The human manager owns final judgment, priorities, tradeoffs, code review, and production approval. Agents must reduce the review load by producing tested, annotated, traceable work, not by hiding complexity.

## v4 gates

A user story is not complete when code compiles. It is complete only after:

- Requirements are understood and traceable.
- Implementation satisfies acceptance criteria.
- Relevant automated tests pass.
- QA checklist passes.
- PM checklist passes.
- Visual evidence exists for UI changes.
- Agent-to-agent feedback loops are closed.
- `agents.log` records who did what in each iteration.
- A PR notification is generated for the human AI PM.

## Operating principle

Agents should ask clarifying questions when needed, but they must keep progress moving. While waiting, they continue safe work: repo discovery, test harness setup, design review, fixture creation, characterization tests, visual baseline capture, and non-risky implementation work.

## Relationship to Well-Architected thinking

The lifecycle uses mechanisms rather than good intentions: operations as code, small reversible changes, telemetry, traceability, automated gates, security at all layers, reliability testing, performance awareness, and continuous improvement.
