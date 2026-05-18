# Branch Conflict Avoidance v11

## Goal

When agents work in parallel, two branches should not edit the same implementation file. Merge conflicts slow down the manager and break the purpose of autonomous agents.

The new rule is:

> If a dev agent needs to edit a file that is already edited or reserved by another non-main branch, the agent must stop that task and move to another task.

## Why this exists

Parallel agent work needs the same discipline as a strong engineering team:

- one responsibility per PR
- SOLID boundaries
- small files and small components
- clean architecture
- no god files
- no accidental cross-branch coupling
- no noisy merge conflict resolution for the manager

## How it works

1. The Spec Task Splitter extracts expected files for each task.
2. The Branch Conflict Coordinator checks active branches before code is written.
3. If the path is free, the agent writes a branch-specific path lease.
4. The dev agent implements the task.
5. Before PR creation, the guard checks the actual changed files.
6. If overlap is found, the PR is blocked and the agent continues with another task.

## New script

```bash
python .ai/scripts/branch_conflict_guard.py guard \
  --mode preflight \
  --base main \
  --current-diff-base dev/my-feature \
  --exclude-branch dev/my-feature \
  --path src/components/RegisterForm.tsx
```

For PR/postflight checks:

```bash
python .ai/scripts/branch_conflict_guard.py guard \
  --mode postflight \
  --base main \
  --current-diff-base dev/my-feature \
  --exclude-branch dev/my-feature
```

## Path leases

The guard can create lease files like:

```text
docs/agentic-path-leases/ai__register-form__frontend-register-form.json
```

The lease advertises:

```json
{
  "branch": "ai/register-form/frontend-register-form",
  "task_id": "frontend-register-form",
  "reserved_paths": ["src/components/RegisterForm.tsx"]
}
```

Other agents scan those leases before coding.

## What happens when a conflict is detected

The agent must:

```text
1. Stop the current task.
2. Log the conflict in agents.log.
3. Keep the worktree/branch for debugging if changes already exist.
4. Do not open a PR.
5. Select another ready task.
6. Ask manager only when overlap is unavoidable.
```

## How this encourages better architecture

If many tasks need the same file, that is usually an architectural smell. The agent should consider:

- extracting a component
- extracting a hook/use case/service
- adding an adapter/strategy/provider
- creating a new module instead of editing a god file
- splitting API, UI, database, cloud, and security work into separate PRs

## Manager override

Default is strict. A manager can approve overlap only when the file is truly shared, such as:

- router/index file
- public API contract
- Terraform module root
- database schema
- security policy

The override should be explicit and documented in the PR evidence.

## Local and cloud coordination

When enabled, the path lease branch is pushed early so local agents and Codex Cloud agents can see the same reserved paths before they start editing files. If the repository has no remote or credentials, the push attempt is non-blocking and the local guard still works.
