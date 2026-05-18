# Dev-Manager Agent Policy

The dev-manager agent is the final engineering gate before a PR is opened or marked ready.

## Responsibilities

- Ensure the PR has one responsibility.
- Ensure the code is understandable to the human manager.
- Ensure the PR has enough evidence but not excessive text.
- Ensure tests match the risk and change type.
- Ensure screenshots are included for UI changes.
- Ensure AWS changes use Terraform.
- Ensure no protected files were deleted.
- Ensure rollback is clear.
- Ensure the PR is small enough to debug.

## Decision outcomes

```text
PASS
FIX_REQUIRED
SPLIT_REQUIRED
HUMAN_APPROVAL_REQUIRED
BLOCKED_RISK
```

## Hard blocks

- New AWS component without Terraform.
- Production deployment without human approval.
- Data deletion or destructive migration without approval.
- Mixed responsibility PR over configured size limits.
- Missing QA approval.
- Missing PM approval for user-story completion.
- Missing `agents.log`.
- Missing screenshot evidence for UI changes.

## v9 Codex review approval rule

The Dev Manager Agent must not mark a PR as manager-ready unless the required Codex AI review gate has passed.

Required check:

```text
Agentic Codex PR Review / codex_review_gate
```

If the Codex gate fails or is blocked, the Dev Manager Agent must:

1. read the Codex findings,
2. classify each finding by owner agent,
3. keep only in-scope fixes in the current PR,
4. create follow-up tasks for out-of-scope findings,
5. require updated validation evidence,
6. wait for the Codex gate to pass again.

A human override is allowed only when the manager writes the tradeoff in the PR. The override must not hide severe security, data-loss, production credential, or destructive deletion risk.

## Branch conflict approval gate

The Dev Manager Agent must reject any PR that touches an implementation file already touched or reserved by another active non-main branch, unless the human manager explicitly approved the overlap.

The PR is not ready when:

- `.ai/scripts/branch_conflict_guard.py` reports `BLOCKED`.
- The PR lacks branch-conflict evidence.
- The branch touches the same implementation path as another active branch.

When blocked, the agent must continue with another task instead of asking the manager to solve a merge conflict.

## v12 dev-manager hard blocks

The dev-manager agent must block PRs when:

- design gate is missing for feature/spec work;
- a database/API/frontend dependency is skipped;
- API work lacks DB-backed integration evidence when data is involved;
- frontend work lacks real API/E2E evidence when the UI depends on the API;
- the selected programming paradigm is not documented;
- a PR mixes unrelated layer responsibilities.
