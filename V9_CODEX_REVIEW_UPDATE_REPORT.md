# v9 Codex Review Update Report

## Change requested

Every pull request must have a Codex/AI review before the human AI PM approves it.

## Implemented

Added a mandatory Codex PR review gate and an optional official `@codex review` request workflow.

### Required merge gate

```text
.github/workflows/agentic-codex-pr-review.yml
```

This workflow runs on PR open/sync/reopen/ready-for-review, calls `openai/codex-action@v1`, saves Codex output, parses the final decision, uploads evidence, and posts/updates a PR comment.

Required status check name:

```text
Agentic Codex PR Review / codex_review_gate
```

### Optional official Codex mention

```text
.github/workflows/agentic-codex-review-request.yml
```

This workflow posts an idempotent `@codex review` comment once per PR head SHA. It uses `pull_request_target` only to comment; it does not checkout or execute untrusted PR code.

### Gate parser

```text
.ai/scripts/codex_pr_review_gate.py
```

The parser requires Codex output to include:

```text
<!-- codex-pr-review-status: PASS|FAIL|BLOCKED -->
<!-- codex-pr-review-risk: Low|Medium|High -->
```

It fails the status check unless the status is explicitly `PASS` and the markers are present.

### New policy and instructions

```text
.ai/specs/codex-pr-review-policy.yml
.ai/specs/required-status-checks.md
.ai/agents/codex-pr-reviewer.agent.md
.ai/skills/codex-pr-review.skill.md
CODEX_PR_REVIEW_GATE_V9.md
```

### Updated files

```text
AGENTS.md
README.md
START_HERE.md
.github/PULL_REQUEST_TEMPLATE.md
.ai/automation/agentic.config.json
.ai/scripts/agentic_sdlc.py
.ai/scripts/generate_pr_notification.py
DEV_MANAGER_AGENT_POLICY.md
```

## Required repository setup

Add repository secret:

```text
OPENAI_API_KEY
```

Add this branch protection required check:

```text
Agentic Codex PR Review / codex_review_gate
```

Optionally enable Codex code review in Codex settings so the `@codex review` comment triggers a native Codex review.

## Validation performed

- Python compile check for all `.ai/scripts/*.py`
- Bash syntax check for `.ai/scripts/*.sh` and `.codex/*.sh`
- YAML parse check for all GitHub workflows and YAML specs
- JSON parse check for `.ai/automation/agentic.config.json`
- Parser simulation:
  - explicit PASS marker exits 0
  - explicit FAIL marker exits 1
  - missing output exits 1
  - fallback Status/Risk without final markers exits 1
- Removed `__pycache__`, `.pyc`, and runtime `.agent` artifacts from the package

## Important limitation

The package cannot verify a real Codex GitHub review or OpenAI API key inside this sandbox. That validation happens after installation in a real repo with `OPENAI_API_KEY` configured.
