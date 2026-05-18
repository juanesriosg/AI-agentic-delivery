# Agentic Delivery Operating Model

## State machine

```text
Backlog
  -> Ready for Agent
  -> Claimed
  -> In Progress
  -> Self Testing
  -> PR Ready
  -> Manager Review
  -> Changes Requested
  -> QA / Staging
  -> Done
```

Blocked work can occur from any active state.

## Task lifecycle

### 1. Intake

A task is ready for agent work only when it has:

- Business goal.
- Technical goal.
- Acceptance criteria.
- Repo.
- Scope boundaries.
- Risk flags.
- Validation expectations.
- Owner/reviewer.

### 2. Claim

The agent marks the task claimed and creates a branch.

### 3. Plan

The agent produces a short implementation plan. For low-risk work, it can plan and code immediately. For high-risk work, it must request approval before coding.

### 4. Implement

The agent makes the smallest safe change that satisfies acceptance criteria.

### 5. Validate

The agent runs tests and quality gates.

### 6. Self-review

The agent scores its work against the quality rubric.

### 7. PR

The agent opens or prepares a PR with evidence.

### 8. Notify

The agent notifies the manager.

### 9. Continue

The agent moves to the next ready task unless WIP limits are reached.

## Epic lifecycle

```text
Epic Planned
  -> Tasks Ready
  -> Tasks In Progress
  -> Feature Agent-Complete
  -> Integration Tested
  -> Manager Acceptance
  -> Stakeholder Acceptance
  -> Done
```

An epic is `agent-complete` when all agent tasks are PR-ready or merged depending on repo policy, integration tests have run or a test plan is provided, and remaining risks are documented.

## Manager daily review

The manager reviews in this order:

1. High-risk PRs.
2. Blocked tasks.
3. Feature-complete notifications.
4. Normal PRs.
5. Delivery metrics.
6. Next-day prioritization.

## Agent continuation rule

When a task is PR-ready, the agent must not wait idle.

The agent should:

1. Notify manager.
2. Mark task `manager:review`.
3. Check WIP limit.
4. Claim next `ai:ready` task.
5. Avoid touching files likely to conflict with its open PRs.

## Quality gates

A PR is not ready until:

- Tests are run or a clear reason is documented.
- Lint/typecheck/build are run when available.
- No unrelated changes are included.
- No protected delete is present.
- Risk is classified.
- Rollback is documented.
- PR size is reasonable or justified.

## Failure handling

If validation fails:

1. Analyze failure.
2. Fix if related to change.
3. Re-run targeted tests.
4. Re-run broader tests when needed.
5. If failure is unrelated, document evidence and escalate.
6. Do not hide or delete failing tests.

## Data feedback loop

Agents produce task metrics. The data analyst agent reviews them and identifies:

- Bottlenecks.
- Rework patterns.
- Repeated test failures.
- Repos missing test commands.
- PRs too large for efficient review.
- High-risk areas repeatedly touched.
- Flaky tests.
- Agent behavior needing governance updates.
