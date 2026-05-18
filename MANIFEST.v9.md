# Manifest v9 — Mandatory Codex PR Review

Built from v8 audited-fixed.

## New files

```text
CODEX_PR_REVIEW_GATE_V9.md
.github/workflows/agentic-codex-pr-review.yml
.github/workflows/agentic-codex-review-request.yml
.github/codex/prompts/pr-review.md
.ai/scripts/codex_pr_review_gate.py
.ai/agents/codex-pr-reviewer.agent.md
.ai/skills/codex-pr-review.skill.md
.ai/specs/codex-pr-review-policy.yml
.ai/specs/required-status-checks.md
.ai/examples/example-codex-pr-review.md
```

## Updated files

```text
AGENTS.md
README.md
START_HERE.md
.github/PULL_REQUEST_TEMPLATE.md
.ai/automation/agentic.config.json
DEV_MANAGER_AGENT_POLICY.md
.ai/scripts/agentic_sdlc.py
.ai/scripts/generate_pr_notification.py
```

## Required branch protection check

```text
Agentic Codex PR Review / codex_review_gate
```

## Required secret

```text
OPENAI_API_KEY
```

## Optional repository setup

Enable Codex code review in Codex settings so the automatic `@codex review` request creates a native Codex PR review.
