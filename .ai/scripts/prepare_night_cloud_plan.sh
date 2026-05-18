#!/usr/bin/env bash
set -euo pipefail

echo "Local-first policy: cloud continuation is not automatic."
echo "This script only prepares a cloud-safe plan; it does not run cloud agents."
python .ai/scripts/agentic_sdlc.py cloud-plan
echo "To run cloud mode explicitly, use GitHub workflow 'Agentic SDLC - Explicit cloud continuation' and type I_APPROVE_CLOUD_RUN."
