# Skill: Branch Conflict Avoidance

## Goal
Keep parallel agent work independent by preventing two active branches from editing the same implementation file.

## Required sequence

### 1. Identify intended files
Before implementation, extract likely paths from:

- spec `Files and areas to touch`
- task plan `expected_paths`
- existing architecture boundaries
- test file conventions

### 2. Preflight branch scan
Run:

```bash
python .ai/scripts/branch_conflict_guard.py guard \
  --mode preflight \
  --base main \
  --current-diff-base <source-spec-branch> \
  --exclude-branch <source-spec-branch> \
  --path src/example/file.ts \
  --json-output .agent/branch-conflict/preflight.json \
  --markdown-output .agent/branch-conflict/preflight.md
```

If the command exits non-zero, stop this task and select another task.

### 3. Reserve paths
When the preflight passes, create a branch-specific lease:

```bash
python .ai/scripts/branch_conflict_guard.py guard \
  --mode preflight \
  --base main \
  --current-diff-base <source-spec-branch> \
  --exclude-branch <source-spec-branch> \
  --path src/example/file.ts \
  --write-lease \
  --commit-lease
```

The lease file lives under `docs/agentic-path-leases/` and advertises intent to other agents.

### 4. Postflight branch scan
Before PR creation, run:

```bash
python .ai/scripts/branch_conflict_guard.py guard \
  --mode postflight \
  --base main \
  --current-diff-base <source-spec-branch> \
  --exclude-branch <source-spec-branch> \
  --json-output docs/agentic-evidence/<story>/<task>/branch-conflict-report.json \
  --markdown-output docs/agentic-evidence/<story>/<task>/branch-conflict-report.md
```

The PR cannot be opened or considered complete if this fails.

## Decision rule

- No overlap: continue.
- Overlap with another active branch: switch task.
- Overlap only in branch-specific evidence or lease files: ignore.
- Unavoidable overlap: ask manager for explicit exception.
