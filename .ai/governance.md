# Agentic Engineering Governance

## Purpose

Enable AI agents to operate like autonomous mid-level software developers while preserving safety, ownership, reviewability, and business alignment.

## Governance principles

1. Business value first.
2. Ownership is explicit.
3. Work is small and reversible.
4. Risk determines review depth.
5. Automation enforces rules.
6. Agents provide evidence, not opinions.
7. Humans approve high-risk decisions.
8. Agents continue with queued work after producing a reviewable artifact.
9. Every task improves the system or produces learning.
10. Failures are used to improve mechanisms.

## Human roles

### Manager / Agentic Delivery Lead

Owns:

- Priorities.
- Stakeholder alignment.
- Epic sequencing.
- Risk acceptance.
- Final review decisions.
- Cross-repo coordination.
- Ownership boundary resolution.

Does not need to own:

- Every implementation detail.
- Every test run.
- Every small bug fix.
- Every low-risk code review line.

### Repo owner

Owns:

- Repo-level standards.
- Merge decisions.
- Release decisions.
- Ownership boundaries.
- Protected paths.
- Codeowners.
- Production deployment approval.

### Agent

Owns:

- Task execution.
- Local implementation decisions within task scope.
- Testing.
- Evidence collection.
- PR quality.
- Early escalation.
- Continuing with next ready work.

## Risk model

Low-risk work may proceed to PR without interruption.

Medium-risk work may proceed to PR but must be clearly marked for manager review.

High-risk work must stop before implementation unless the task explicitly authorizes the risk.

## Review policy

The manager reviews outcomes, not activity.

Manager review focuses on:

- Acceptance criteria.
- Test evidence.
- Risk.
- Rollback.
- Architecture impact.
- Ownership boundaries.
- Files flagged by the agent.

## Continuous improvement

At least weekly, review:

- Repeated test failures.
- Repeated manager review comments.
- PRs that were too large.
- Blocked work causes.
- Reopened defects.
- CI failures.
- Agent violations of guardrails.
- Missing repo context.
