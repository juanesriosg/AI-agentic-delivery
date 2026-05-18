#!/usr/bin/env bash
set -euo pipefail

runtime="local"
reasons=()

if [[ "${CI:-}" == "true" ]]; then
  runtime="ci"
  reasons+=("CI=true")
fi

if [[ "${GITHUB_ACTIONS:-}" == "true" ]]; then
  runtime="github_actions"
  reasons+=("GITHUB_ACTIONS=true")
fi

if [[ -n "${CODESPACES:-}" || -n "${GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN:-}" ]]; then
  runtime="codespaces"
  reasons+=("codespaces env detected")
fi

if [[ -n "${CODEX:-}" || -n "${CODEX_SANDBOX:-}" || -n "${OPENAI_CODEX:-}" || -n "${CODEX_ENVIRONMENT:-}" ]]; then
  runtime="codex_cloud"
  reasons+=("codex-like env variable detected")
fi

if [[ -f /.dockerenv ]]; then
  reasons+=("container detected")
fi

if [[ -z "${AGENT_TASK_ID:-}" ]]; then
  branch="$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo unknown-task)"
  sanitized="$(echo "$branch" | tr '/:@ ' '----' | tr -cd '[:alnum:]_.-')"
  export AGENT_TASK_ID="${sanitized:-unknown-task}"
fi

cat <<EOF
Agent runtime detection
runtime: ${runtime}
task_id: ${AGENT_TASK_ID}
repo: $(basename "$(git rev-parse --show-toplevel 2>/dev/null || pwd)")
branch: $(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo unknown)
reasons: ${reasons[*]:-none}
EOF
