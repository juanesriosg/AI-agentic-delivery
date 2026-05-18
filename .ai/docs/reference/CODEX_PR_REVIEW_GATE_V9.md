# v9 — Mandatory Codex Review for Every Pull Request

## Goal

Every PR must be reviewed by AI before the human AI PM / senior developer approves it.

This package uses two mechanisms:

1. **Required Codex PR Review Gate** — a GitHub Actions status check using `openai/codex-action@v1`.
2. **Optional official `@codex review` request** — an automatic PR comment that asks the Codex GitHub integration to review the PR like a teammate.

The required merge control is the status check:

```text
Agentic Codex PR Review / codex_review_gate
```

Configure branch protection so this check is required before merge.

## Why both mechanisms exist

The `@codex review` comment is useful because it uses the official Codex GitHub review experience when the repo has Codex code review enabled.

The GitHub Action gate is useful because it creates a deterministic status check that branch protection can require.

## Workflow

```text
Agent opens PR
  ↓
GitHub posts @codex review request
  ↓
Codex PR Review GitHub Action runs
  ↓
Codex reviews diff, specs, evidence, tests, screenshots, security, scale, AWS/Terraform
  ↓
Parser enforces PASS / FAIL / BLOCKED
  ↓
Review artifact and PR comment are created
  ↓
Human AI PM approval is allowed only if the Codex gate passes
```

## Files added

```text
.github/workflows/agentic-codex-pr-review.yml
.github/workflows/agentic-codex-review-request.yml
.github/codex/prompts/pr-review.md
.ai/scripts/codex_pr_review_gate.py
.ai/agents/codex-pr-reviewer.agent.md
.ai/skills/codex-pr-review.skill.md
.ai/specs/codex-pr-review-policy.yml
.ai/examples/example-codex-pr-review.md
```

## Required setup

Add this GitHub secret:

```text
OPENAI_API_KEY
```

Then enable branch protection and require this status check:

```text
Agentic Codex PR Review / codex_review_gate
```

For the optional official Codex comment flow, enable Codex code review for the repository in Codex settings.

## Pass criteria

Codex may pass a PR only when:

```text
- one responsibility per PR
- spec and acceptance criteria are satisfied
- tests/evidence are appropriate
- QA/PM/dev-manager evidence is not fake or pending
- UI screenshots exist when relevant
- security/reliability/scale risks are acceptable
- AWS changes use Terraform/IaC
- rollback is clear
- no protected deletion or data-loss risk is hidden
```

## Fail behavior

When the Codex gate fails:

```text
1. The PR remains blocked.
2. The responsible agent fixes the issue.
3. Tests/evidence are updated.
4. The PR is pushed again.
5. Codex reviews again.
```

The manager can override only by documenting the risk in the PR. Do not override secrets exposure, destructive deletion, or production credential risk without security/owner approval.
