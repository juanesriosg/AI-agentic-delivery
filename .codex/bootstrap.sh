#!/usr/bin/env bash
set -euo pipefail

if [[ -x .ai/scripts/detect-runtime.sh ]]; then
  .ai/scripts/detect-runtime.sh
fi

.ai/scripts/bootstrap-task-env.sh
