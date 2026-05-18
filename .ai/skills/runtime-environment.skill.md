# Skill: Runtime Environment Setup

## Purpose

Create repeatable task-scoped environments for local and cloud agents.

## Steps

1. Read `.ai/runtime/runtime-contract.md`.
2. Set or infer `AGENT_TASK_ID`.
3. Run `.ai/scripts/detect-runtime.sh`.
4. Run `.ai/scripts/bootstrap-task-env.sh`.
5. Record setup commands and failures.
6. Continue only if the repo can be validated or the blocker is documented.

## Rules

- Prefer lockfiles and repo wrappers.
- Do not install global packages.
- Do not use sudo.
- Do not commit `.agent/`, virtual environments, caches, or build artifacts.
- Escalate when system packages or secrets are required.

## Evidence

Include in PR:

```text
Runtime:
Bootstrap commands:
Bootstrap result:
Environment limitations:
```
