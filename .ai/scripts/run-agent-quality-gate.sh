#!/usr/bin/env bash
set -euo pipefail

log() { echo "[agent-quality-gate] $*"; }
warn() { echo "[agent-quality-gate][warn] $*" >&2; }
have() { command -v "$1" >/dev/null 2>&1; }

repo_root="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$repo_root"

status=0
run_gate() {
  log "running: $*"
  if ! "$@"; then
    warn "failed: $*"
    status=1
  fi
}

has_npm_script() {
  local script="$1"
  have node || return 1
  node -e "const p=require('./package.json'); process.exit(p.scripts && p.scripts['${script}'] ? 0 : 1)" 2>/dev/null
}

node_runner=""
if [[ -f package.json ]]; then
  if [[ -f pnpm-lock.yaml ]] && have pnpm; then
    node_runner="pnpm"
  elif [[ -f package-lock.json ]] && have npm; then
    node_runner="npm"
  elif [[ -f yarn.lock ]] && have yarn; then
    node_runner="yarn"
  elif have npm; then
    node_runner="npm"
  fi
fi

run_node_script() {
  local script="$1"
  [[ -n "$node_runner" ]] || return 0
  has_npm_script "$script" || return 0
  case "$node_runner" in
    pnpm) run_gate pnpm run "$script" ;;
    npm) run_gate npm run "$script" ;;
    yarn) run_gate yarn "$script" ;;
  esac
}

# Guardrails first.
if [[ -x .ai/scripts/check-agent-guardrails.sh ]]; then
  run_gate .ai/scripts/check-agent-guardrails.sh
fi

# Explicit override commands take precedence.
if [[ -n "${AGENT_VALIDATION_COMMANDS:-}" ]]; then
  log "running AGENT_VALIDATION_COMMANDS"
  # Intentionally allow shell here because manager/CI may pass a compound command.
  if ! bash -lc "$AGENT_VALIDATION_COMMANDS"; then
    status=1
  fi
else
  # Node
  if [[ -n "$node_runner" ]]; then
    run_node_script test
    run_node_script lint
    if has_npm_script typecheck; then
      run_node_script typecheck
    elif has_npm_script type-check; then
      run_node_script type-check
    fi
    run_node_script build
  fi

  # Python
  if [[ -f pyproject.toml || -f requirements.txt || -d tests ]]; then
    pycmd="python3"
    if [[ -n "${AGENT_TASK_ID:-}" && -x ".agent/envs/${AGENT_TASK_ID}/python/bin/python" ]]; then
      pycmd=".agent/envs/${AGENT_TASK_ID}/python/bin/python"
    fi
    if [[ -d tests ]] && "$pycmd" -m pytest --version >/dev/null 2>&1; then
      run_gate "$pycmd" -m pytest
    fi
    if "$pycmd" -m ruff --version >/dev/null 2>&1; then
      run_gate "$pycmd" -m ruff check .
    fi
    if "$pycmd" -m mypy --version >/dev/null 2>&1; then
      run_gate "$pycmd" -m mypy .
    fi
  fi

  # Go
  if [[ -f go.mod ]] && have go; then
    run_gate go test ./...
  fi

  # Rust
  if [[ -f Cargo.toml ]] && have cargo; then
    run_gate cargo test
    if have cargo-clippy || cargo clippy --version >/dev/null 2>&1; then
      run_gate cargo clippy -- -D warnings
    fi
  fi

  # Java
  if [[ -x ./mvnw ]]; then
    run_gate ./mvnw test
  elif [[ -f pom.xml ]] && have mvn; then
    run_gate mvn test
  fi
  if [[ -x ./gradlew ]]; then
    run_gate ./gradlew test
  elif [[ -f build.gradle || -f build.gradle.kts ]] && have gradle; then
    run_gate gradle test
  fi

  # .NET
  if ls *.sln *.csproj >/dev/null 2>&1 && have dotnet; then
    run_gate dotnet test --no-restore
  fi

  # Ruby
  if [[ -f Gemfile ]] && have bundle; then
    if bundle exec rake -T test >/dev/null 2>&1; then
      run_gate bundle exec rake test
    elif bundle exec rspec --version >/dev/null 2>&1; then
      run_gate bundle exec rspec
    fi
  fi
fi

# Self-review scripts should run but not fail the gate unless their own strict mode is used separately.
if [[ -x .ai/scripts/agent-self-review.py ]]; then
  .ai/scripts/agent-self-review.py --format markdown || true
fi
if [[ -x .ai/scripts/check-scale-readiness.py ]]; then
  .ai/scripts/check-scale-readiness.py --format markdown || true
fi

# v3 optional spec quality and bug-risk scans. Non-blocking by default because they can produce false positives.
if [[ -n "${AGENT_TASK_SPEC:-}" && -f "${AGENT_TASK_SPEC}" && -x .ai/scripts/spec-quality-check.py ]]; then
  .ai/scripts/spec-quality-check.py --spec "${AGENT_TASK_SPEC}" --format markdown || true
fi
if [[ -x .ai/scripts/agent-bug-scan.py ]]; then
  .ai/scripts/agent-bug-scan.py --format markdown || true
fi

if [[ "$status" -ne 0 ]]; then
  echo "::error::Agent quality gate failed. Fix failures or document blocker."
  exit "$status"
fi

log "quality gate complete"

