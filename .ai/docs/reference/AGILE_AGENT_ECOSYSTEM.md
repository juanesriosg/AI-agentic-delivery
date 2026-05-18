# Agile Agent Ecosystem

This file describes the agent team model used by v4.

## Agent families

### Product and requirements

- Product Requirements Agent
- Spec Analyst Agent
- Product Manager Acceptance Agent
- UX Researcher Agent

### Design and user experience

- UI Designer Agent
- Design System Agent
- Accessibility QA Engineer
- Visual QA Engineer

### Engineering implementation

- Frontend Engineer Agent
- Backend Engineer Agent
- API Contract Engineer Agent
- Database Engineer Agent
- Integration Engineer Agent
- Cloud Platform Engineer Agent
- DevOps CI/CD Engineer Agent
- Security Engineer Agent
- Performance Engineer Agent
- Scalability Architect Agent
- SRE Reliability Engineer Agent

### Quality and release

- QA Checklist Engineer Agent
- Component Test Engineer Agent
- Integration/E2E Engineer Agent
- QA Regression Engineer Agent
- Exploratory Bug Hunter Agent
- Release Train Engineer Agent
- Release Readiness Agent

### Coordination and memory

- Agile Delivery Orchestrator Agent
- Agent Feedback Coordinator Agent
- Agent Scribe Logger Agent
- Delivery Data Analyst Agent

## Collaboration contract

Every agent must produce outputs that the next agent can use. Agents do not just say `done`; they create artifacts.

Example:

```text
Spec Agent output       -> acceptance criteria and constraints
Design Agent output     -> UX checklist, layout guidance, accessibility notes
Dev Agent output        -> code, tests, self-review, implementation notes
QA Agent output         -> failed/passed checklist, bugs, screenshots, annotations
Dev Agent output        -> fixes and regression evidence
PM Agent output         -> product acceptance checklist and UX feedback
Release Agent output    -> promotion readiness and PR notification
Scribe Agent output     -> agents.log for every iteration
```

## Feedback loop rule

If QA or PM finds an issue, the issue is routed back to the most appropriate agent, not always to the original developer.

Examples:

- Placeholder overlaps form container -> Frontend Engineer + Visual QA owns fix/verification.
- Button copy is confusing -> Product Manager + UX Designer owns recommendation, Frontend owns implementation.
- Endpoint is too slow -> Backend Engineer + Performance Engineer owns fix/verification.
- Deploy script is fragile -> DevOps CI/CD + Cloud Platform owns fix/verification.
- Data model blocks scale -> Database Engineer + Scalability Architect owns fix/verification.

## Parallel work

Parallelism is allowed only when work has clear boundaries and does not create unsafe merge conflicts.

Safe parallel work:

- Backend API contract and frontend mock UI after contract is defined.
- Visual QA baseline capture while backend implementation continues.
- Accessibility checklist while frontend implementation continues.
- Cloud environment readiness while app code is developed.
- Test harness setup while requirements clarification is pending.

Unsafe parallel work:

- Two agents editing the same component without coordination.
- Frontend and backend inventing different API contracts.
- Deployment automation before environment ownership is clear.
- Database migration implementation before data retention and rollback are approved.

## Required evidence

Every story must leave behind:

```text
.agent/agents.log.jsonl
.agent/reports/agents.log.md
.agent/stories/<story-id>/state.json
.agent/stories/<story-id>/qa-checklist.md
.agent/stories/<story-id>/pm-checklist.md
.agent/stories/<story-id>/test-matrix.md
.agent/stories/<story-id>/visual-evidence.md when UI is affected
.agent/stories/<story-id>/pr-notification.md
```
