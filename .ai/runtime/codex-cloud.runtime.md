# Codex Cloud Runtime Runbook

This file describes how agents should behave in Codex Cloud or any similar cloud coding runner.

The exact platform integration can change, so the repository uses portable hooks instead of assuming a proprietary API.

## Recommended configuration

Setup command:

```bash
.codex/bootstrap.sh
```

Validation command:

```bash
.codex/run-quality-gate.sh
```

Agent instructions:

```md
Read AGENTS.md first.
Follow .ai/runtime/runtime-contract.md.
Use .ai/specs/* as policy.
Before coding, run .ai/scripts/bootstrap-task-env.sh.
Before PR, run .ai/scripts/run-agent-quality-gate.sh, agent-self-review.py, and check-scale-readiness.py.
Open a PR with the required template sections.
After PR, notify the manager and continue to the next ai:ready task if the session supports it.
```

## Task modes

### Single-task cloud mode

The cloud runner receives one explicit task. The agent completes that task, opens a PR, notifies the manager, and records the suggested next task.

Use this when the platform ends the session after the task.

### Queue-driven cloud mode

The cloud runner receives permission to select from the issue/task queue. The agent claims one `ai:ready` task, completes it, opens a PR, then claims the next task if WIP limits allow.

Use this when the platform session remains active or can be restarted automatically by your workflow.

## Cloud constraints

Agents must assume:

- Filesystem is ephemeral.
- Internet access may be restricted.
- Secrets may not be available.
- Background processes may be terminated.
- Terminal history may not be visible to the manager.

Therefore, agents must write important evidence in PR bodies and task comments.

## Required PR evidence

Every cloud-created PR must include:

- Runtime detected.
- Bootstrap commands run.
- Validation commands and results.
- Self-review findings.
- Scale-readiness findings.
- Risk level.
- Rollback plan.
- Manager action needed.
