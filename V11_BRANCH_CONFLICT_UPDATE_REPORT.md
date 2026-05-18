# v11 Update Report — Branch Conflict Avoidance

## Problem solved

Parallel agent branches can create annoying merge conflicts when two dev agents touch the same implementation file. v11 prevents that by adding branch scanning, path leases, preflight checks, postflight checks, and PR guardrails.

## Core rule

Two active non-main branches must not edit the same implementation file.

## Agent behavior

When conflict is detected, the agent must:

1. stop that task,
2. log the conflict,
3. avoid opening a PR,
4. continue with another ready task,
5. escalate only if the overlap is truly unavoidable.

## Architecture effect

This reinforces:

- SOLID principles
- single responsibility
- clean architecture
- one responsibility per PR
- small reversible changes
- easier debugging
- less manager time spent resolving conflicts

## Main validation command

```bash
python .ai/scripts/branch_conflict_guard.py guard \
  --mode pr \
  --base main \
  --current-diff-base dev/my-feature \
  --exclude-branch dev/my-feature
```
