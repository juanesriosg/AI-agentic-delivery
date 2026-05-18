# Local Runtime Runbook

Use this when running agents on a developer workstation or local container.

## Start a task

```bash
export AGENT_TASK_ID="TASK-123"
.ai/scripts/detect-runtime.sh
.ai/scripts/bootstrap-task-env.sh
```

## Run the full local gate

```bash
.ai/scripts/run-agent-quality-gate.sh
.ai/scripts/agent-self-review.py --format markdown
.ai/scripts/check-scale-readiness.py --format markdown
```

## Local safety rules

- Do not install global packages.
- Do not modify shell startup files.
- Do not change local git identity.
- Do not use production credentials.
- Do not delete files outside the repository.
- Do not clean the workspace with `git clean`, `git reset --hard`, or `rm -rf`.

## Recommended local loop

```bash
while true; do
  # manager/queue command selects next task
  .ai/scripts/bootstrap-task-env.sh
  # agent implements task
  .ai/scripts/run-agent-quality-gate.sh
  .ai/scripts/agent-self-review.py --format markdown
  .ai/scripts/check-scale-readiness.py --format markdown
  # agent opens PR and notifies manager
  # agent stops if WIP limit reached or queue empty
  break
done
```
