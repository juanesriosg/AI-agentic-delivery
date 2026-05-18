# Runtime Contract for Local and Cloud Agents

This contract makes every agent portable between a local workstation, Codex Cloud, GitHub-hosted checks, or another remote sandbox.

## Principles

1. Repository instructions are the source of truth.
2. Runtime setup must be reproducible from committed files.
3. Task environments are isolated and ignored by git.
4. Cloud sandboxes are ephemeral; agents must not depend on previous sessions.
5. Secrets are never assumed, printed, copied, or committed.
6. Validation must be executable by another agent or human reviewer.

## Required runtime phases

### 1. Detect

Run:

```bash
.ai/scripts/detect-runtime.sh
```

The agent records whether it is local, CI, Codespaces, Codex-like cloud, containerized, or unknown.

### 2. Bootstrap

Run:

```bash
.ai/scripts/bootstrap-task-env.sh
```

The agent creates task-scoped virtual environments and installs dependencies using the repository's lockfiles and wrappers.

### 3. Implement

The agent makes the smallest safe change that satisfies acceptance criteria.

### 4. Validate

Run:

```bash
.ai/scripts/run-agent-quality-gate.sh
```

The agent also runs any task-specific validation commands.

### 5. Self-review and improve

Run:

```bash
.ai/scripts/agent-self-review.py --format markdown
.ai/scripts/check-scale-readiness.py --format markdown
```

The agent fixes meaningful findings before PR.

### 6. Notify and continue

The agent opens or prepares a PR, posts the required status, moves the task to manager review, then continues with the next `ai:ready` task if the runtime/session permits and WIP limits allow.

## Cloud-specific rules

In cloud environments:

- Do not start long-lived background services unless they are part of a test command and are cleaned up by the command.
- Do not rely on external network access unless the repo already requires it and the task allows it.
- Do not persist credentials, package caches, or artifacts outside approved directories.
- Prefer deterministic commands and lockfile-based installs.
- Produce concise PR evidence because the manager may not see the full terminal history.

## Local-specific rules

In local environments:

- Do not modify the developer's global shell, package managers, or credentials.
- Do not install global dependencies without explicit approval.
- Keep task environments under `.agent/` or another ignored path.
- Clean up only the agent's own temporary resources; never run broad destructive cleanup commands.
