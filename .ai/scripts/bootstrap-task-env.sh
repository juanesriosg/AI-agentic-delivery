#!/usr/bin/env bash
set -euo pipefail

log() { echo "[agent-bootstrap] $*"; }
warn() { echo "[agent-bootstrap][warn] $*" >&2; }
have() { command -v "$1" >/dev/null 2>&1; }

repo_root="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$repo_root"

if [[ -z "${AGENT_TASK_ID:-}" ]]; then
  branch="$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo unknown-task)"
  AGENT_TASK_ID="$(echo "$branch" | tr '/:@ ' '----' | tr -cd '[:alnum:]_.-')"
  export AGENT_TASK_ID="${AGENT_TASK_ID:-unknown-task}"
fi

AGENT_HOME="${AGENT_HOME:-.agent}"
ENV_ROOT="${AGENT_ENV_ROOT:-${AGENT_HOME}/envs/${AGENT_TASK_ID}}"
mkdir -p "$ENV_ROOT" "${AGENT_HOME}/cache" "${AGENT_HOME}/reports"

# Prevent accidental commits of agent artifacts without modifying tracked .gitignore.
if [[ -d .git ]]; then
  grep -qxF ".agent/" .git/info/exclude 2>/dev/null || echo ".agent/" >> .git/info/exclude
  grep -qxF ".venv/" .git/info/exclude 2>/dev/null || echo ".venv/" >> .git/info/exclude
fi

log "task_id=${AGENT_TASK_ID}"
log "env_root=${ENV_ROOT}"

run_required() {
  log "running: $*"
  "$@"
}

run_best_effort() {
  log "running: $*"
  if ! "$@"; then
    warn "command failed but bootstrap will continue: $*"
  fi
}

# Python
if [[ -f pyproject.toml || -f requirements.txt || -f setup.py || -f poetry.lock || -f Pipfile ]]; then
  if have python3; then
    PY_ENV="${ENV_ROOT}/python"
    if [[ ! -d "$PY_ENV" ]]; then
      run_required python3 -m venv "$PY_ENV"
    fi
    # shellcheck disable=SC1091
    source "$PY_ENV/bin/activate"
    run_best_effort python -m pip install --upgrade pip
    if [[ -f requirements.txt ]]; then
      run_required python -m pip install -r requirements.txt
    elif [[ -f pyproject.toml ]]; then
      run_best_effort python -m pip install -e ".[dev]"
      run_best_effort python -m pip install -e .
    elif [[ -f setup.py ]]; then
      run_required python -m pip install -e .
    fi
    deactivate || true
  else
    warn "Python project detected but python3 is unavailable."
  fi
fi

# Node
if [[ -f package.json ]]; then
  if [[ -f pnpm-lock.yaml ]] && have pnpm; then
    run_required pnpm install --frozen-lockfile
  elif [[ -f package-lock.json ]] && have npm; then
    run_required npm ci
  elif [[ -f yarn.lock ]] && have yarn; then
    run_required yarn install --frozen-lockfile
  elif have npm; then
    warn "No recognized lockfile found; running npm install may modify lockfile. Escalate if unexpected."
    run_best_effort npm install
  else
    warn "Node project detected but npm/pnpm/yarn unavailable."
  fi
fi

# Go
if [[ -f go.mod ]]; then
  if have go; then
    run_required go mod download
  else
    warn "Go project detected but go is unavailable."
  fi
fi

# Rust
if [[ -f Cargo.toml ]]; then
  if have cargo; then
    run_required cargo fetch
  else
    warn "Rust project detected but cargo is unavailable."
  fi
fi

# Java Maven
if [[ -f pom.xml ]]; then
  if [[ -x ./mvnw ]]; then
    run_best_effort ./mvnw -q -DskipTests dependency:go-offline
  elif have mvn; then
    run_best_effort mvn -q -DskipTests dependency:go-offline
  else
    warn "Maven project detected but mvnw/mvn unavailable."
  fi
fi

# Java Gradle
if [[ -f build.gradle || -f build.gradle.kts || -x ./gradlew ]]; then
  if [[ -x ./gradlew ]]; then
    run_best_effort ./gradlew --no-daemon dependencies
  elif have gradle; then
    run_best_effort gradle dependencies
  else
    warn "Gradle project detected but gradlew/gradle unavailable."
  fi
fi

# .NET
if ls *.sln *.csproj >/dev/null 2>&1; then
  if have dotnet; then
    run_required dotnet restore
  else
    warn ".NET project detected but dotnet is unavailable."
  fi
fi

# Ruby
if [[ -f Gemfile ]]; then
  if have bundle; then
    run_required bundle config set path .agent/vendor/bundle
    run_required bundle install
  else
    warn "Ruby project detected but bundle is unavailable."
  fi
fi

log "bootstrap complete"
