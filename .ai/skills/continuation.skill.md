# Skill: Backlog Continuation

## Purpose

Allow agents to continue working while the manager reviews previous PRs.

## Rule

When a task reaches `PR Ready` or `Blocked`, the agent should stop active work on that task and pick another ready task if WIP limits allow.

## Continuation criteria

Agent may continue when:

- Current PR is ready and manager notified.
- Current task is blocked and blocker documented.
- WIP limit is not exceeded.
- Next task does not conflict with open PR.
- Next task is labeled `ai:ready`.

## Do not continue when

- Current task has uncommitted changes.
- Current branch has failing related tests not documented.
- Current PR has not been created or notification not sent.
- WIP limit exceeded.
- Next task touches same files as open PR.
- Next task is high risk and not approved.

## Next task selection

Prioritize:

1. Blocker-free tasks in same repo that do not conflict.
2. Low-risk bug fixes.
3. Test coverage tasks.
4. Small feature tasks.
5. Repo mechanism improvements.
6. Medium-risk tasks.
7. High-risk tasks only with approval.

## Queue empty behavior

If no ready tasks exist, agent should produce:

```md
Status: Queue empty
Repo/project:
Blocked tasks:
Tasks missing ready criteria:
Suggested next tasks:
Mechanism improvements available:
```
