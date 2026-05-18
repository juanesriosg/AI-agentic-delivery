# Cloud Agent Operating Model

## Purpose

Allow agents to work in Codex Cloud or similar environments while still behaving like autonomous mid-level engineers.

## Two compatible modes

### Mode A: One task per cloud run

The manager starts a run with one task. The agent completes it, opens a PR, comments with status, and suggests the next ready task.

This is safest when the platform ends the session after each task.

### Mode B: Queue continuation

The manager starts a run with permission to process the queue. The agent claims an `ai:ready` task, completes it, opens a PR, then claims another task if:

- WIP limits allow.
- It will not conflict with its own open PR.
- The next task is clear and bounded.
- No high-risk approval is needed before coding.

## Required queue state transitions

```text
ai:ready -> ai:claimed -> ai:in-progress -> manager:review
```

If blocked:

```text
ai:in-progress -> ai:blocked
```

If high-risk approval is needed:

```text
ai:in-progress -> manager:decision-needed
```

## Notification points

- Task claimed.
- PR ready.
- Blocked.
- Feature agent-complete.
- Epic agent-complete.
- High-risk decision needed.
- Queue empty or WIP limit reached.

## Cloud PR requirement

Because the manager may not see terminal history, the PR is the durable source of truth.
