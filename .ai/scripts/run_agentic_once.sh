#!/usr/bin/env bash
set -euo pipefail
export AGENTIC_CODEX_MODEL="${AGENTIC_CODEX_MODEL:-gpt-5.5}"
export AGENTIC_CODEX_REASONING_EFFORT="${AGENTIC_CODEX_REASONING_EFFORT:-high}"
MODE="${1:-local}"
MAX="${2:-1}"
cd "$(git rev-parse --show-toplevel)"
python .ai/scripts/agentic_sdlc.py run-once --mode "$MODE" --max-specs "$MAX"
