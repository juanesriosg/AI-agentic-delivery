#!/usr/bin/env bash
set -euo pipefail
export AGENTIC_CODEX_MODEL="${AGENTIC_CODEX_MODEL:-gpt-5.5}"
export AGENTIC_CODEX_REASONING_EFFORT="${AGENTIC_CODEX_REASONING_EFFORT:-high}"
cd "$(git rev-parse --show-toplevel)"
python .ai/scripts/agentic_sdlc.py doctor || true
python .ai/scripts/agentic_sdlc.py watch --mode local --poll-seconds "${AGENT_POLL_SECONDS:-180}" --max-specs "${AGENT_MAX_SPECS:-1}"
