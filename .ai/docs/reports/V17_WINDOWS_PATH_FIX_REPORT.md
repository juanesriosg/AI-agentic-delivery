# V17 Windows Path Length Fix Report

## Problem

A dry-run on Windows failed with `WinError 3` because internal preview evidence paths became too long, for example:

```text
.agent/runs/<long-spec-id>/tasks/<long-task-id>/evidence-preview/<long-spec-id>/<long-task-id>
```

In the reported case, the path was approximately 285 characters.

## Fix

The orchestrator now uses compact internal runtime IDs by default:

- `run-<hash>-<short-slug>` for run folders.
- `tsk-<hash>-<short-slug>` for worktree run IDs.
- `t-<hash>-<short-task-slug>` for task folders.
- `.agent/runs/.../tasks/.../ev` for dry-run evidence preview.
- `.agent/runs/.../tasks/.../bc` for branch-conflict reports.

The real spec id, task id, branch, and title are still preserved in metadata, evidence content, PR text, and logs. Only internal temporary folder names are shortened.

## Configuration

This is enabled by default through:

```json
{
  "repository": {
    "short_internal_paths": true,
    "max_internal_slug_len": 24
  }
}
```

Set `short_internal_paths` to `false` only if you intentionally want the older verbose internal paths.

## Extra cleanup

The branch-conflict preflight no longer emits duplicate `--exclude-branch` arguments when the current branch is the same as the source branch.

## Validation

Validated with a simulated Windows-like project path and the reported long spec/task names. The dry-run evidence target shortened from roughly 285 characters to about 139 characters in the simulation.
