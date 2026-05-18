#!/usr/bin/env bash
set -euo pipefail

.ai/scripts/run-agent-quality-gate.sh
.ai/scripts/agent-self-review.py --format markdown
.ai/scripts/check-scale-readiness.py --format markdown

# Optional: set AGENT_TASK_SPEC=path/to/task.md before running this command to include spec quality checks.
