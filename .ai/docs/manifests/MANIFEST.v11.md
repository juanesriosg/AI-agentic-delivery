# Manifest v11 — Branch Conflict Avoidance

## Added

```text
.ai/docs/reference/BRANCH_CONFLICT_AVOIDANCE_V11.md
.ai/scripts/branch_conflict_guard.py
.ai/agents/branch-conflict-coordinator.agent.md
.ai/skills/branch-conflict-avoidance.skill.md
.ai/specs/branch-conflict-policy.yml
.ai/specs/path-lease.schema.yml
.github/workflows/agentic-branch-conflict-guard.yml
```

## Updated

```text
AGENTS.md
README.md
.ai/docs/START_HERE.md
.ai/docs/reference/ONE_RESPONSIBILITY_PR_STANDARD.md
.ai/docs/reference/DEV_MANAGER_AGENT_POLICY.md
.ai/automation/agentic.config.json
.ai/scripts/agentic_sdlc.py
.ai/scripts/pr_guardrails.py
.ai/specs/required-status-checks.md
.github/workflows/agentic-pr-guardrails.yml
```

## New behavior

- Dev agents must scan active non-main branches before coding.
- Agents can reserve expected paths using branch-specific path leases.
- If another branch changed or reserved the same implementation file, the task is blocked.
- Blocked tasks are logged and the orchestrator continues with other tasks.
- PR guardrails include branch conflict validation.
- GitHub Actions exposes a required branch conflict status check.
