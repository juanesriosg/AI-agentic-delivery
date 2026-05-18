# Source Spec Branch Integration Mode

In this mode, the branch that contains the spec is also the implementation branch.

## Why

The AI PM wants to interact with code as little as possible:

```text
GPT Pro writes the spec
Codex implements on the spec branch
AI PM receives one final PR
```

## How it works

For every task:

```text
1. Agent checks out the latest source spec branch.
2. Agent runs branch conflict preflight.
3. Agent performs one-responsibility work.
4. Agent runs DB/API/frontend layer gate as applicable.
5. Agent runs QA/PM/dev-manager gates.
6. Agent commits the task to the source spec branch.
7. Agent pushes to origin/<source-spec-branch>.
```

After all tasks are done:

```text
1. Final PR is created from source spec branch to main.
2. Manager is tagged.
3. Codex AI PR review is requested.
4. Human approval waits for automated gates.
```

## Tradeoff

This mode gives fewer PRs for the AI PM to review. For very large features, use task-branch mode instead.

## Guardrails

```text
- One responsibility per task commit.
- Evidence required per task.
- DB before API.
- API before frontend.
- No frontend done without real API/E2E evidence when API is required.
- No new AWS component without Terraform.
- No production deployment without human approval.
```
