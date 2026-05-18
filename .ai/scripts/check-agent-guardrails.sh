#!/usr/bin/env bash
set -euo pipefail

BASE_REF="${BASE_REF:-origin/${GITHUB_BASE_REF:-main}}"

echo "Running agent guardrail checks against base: ${BASE_REF}"

if ! git rev-parse --verify "${BASE_REF}" >/dev/null 2>&1; then
  echo "Base ref ${BASE_REF} not found locally. Attempting fetch..."
  git fetch --no-tags --depth=100 origin "${GITHUB_BASE_REF:-main}" || true
fi

if git rev-parse --verify "${BASE_REF}" >/dev/null 2>&1; then
  DIFF_RANGE="${BASE_REF}...HEAD"
elif git rev-parse --verify origin/master >/dev/null 2>&1; then
  DIFF_RANGE="origin/master...HEAD"
elif git rev-parse --verify HEAD~1 >/dev/null 2>&1; then
  DIFF_RANGE="HEAD~1...HEAD"
else
  DIFF_RANGE="HEAD"
fi

fail() {
  echo "::error::$1"
  exit 1
}

warn() {
  echo "::warning::$1"
}

echo "Checking deleted files..."
DELETED_FILES="$(git diff --name-status "${DIFF_RANGE}" | awk '$1 ~ /^D/ {print $2}' || true)"
DELETED_COUNT="$(printf '%s\n' "${DELETED_FILES}" | sed '/^$/d' | wc -l | tr -d ' ')"

protected_delete_regex='^(\.github/|\.ai/|infra/|infrastructure/|terraform/|cloudformation/|cdk/|k8s/|kubernetes/|helm/|migrations/|database/|db/migrations/|secrets/|certs/|config/production/|\.env($|\.)|Dockerfile$|docker-compose.*\.ya?ml$|LICENSE|NOTICE|CODEOWNERS)'

if [[ "${DELETED_COUNT}" -gt 5 ]]; then
  fail "More than 5 deleted files detected (${DELETED_COUNT}). Manager approval required before PR is ready."
fi

if [[ -n "${DELETED_FILES}" ]]; then
  while IFS= read -r file; do
    [[ -z "${file}" ]] && continue
    if [[ "${file}" =~ ${protected_delete_regex} ]]; then
      fail "Protected file deletion detected: ${file}. Human approval and policy update required."
    else
      warn "File deletion detected: ${file}. Ensure PR explains deletion and rollback."
    fi
  done <<< "${DELETED_FILES}"
fi

echo "Checking changed protected paths..."
CHANGED_FILES="$(git diff --name-only "${DIFF_RANGE}" || true)"
approval_required_regex='^(\.github/workflows/|infra/|infrastructure/|terraform/|cloudformation/|cdk/|k8s/|kubernetes/|helm/|migrations/|database/migrations/|db/migrations/|auth/|security/|iam/|policies/)'

if [[ -n "${CHANGED_FILES}" ]]; then
  while IFS= read -r file; do
    [[ -z "${file}" ]] && continue
    if [[ "${file}" =~ ${approval_required_regex} ]]; then
      warn "Approval-required path changed: ${file}. Mark PR high-risk and request owner review."
    fi
  done <<< "${CHANGED_FILES}"
fi

echo "Checking for suspicious destructive commands in diff..."
PATCH="$(git diff --unified=0 "${DIFF_RANGE}" || true)"

destructive_patterns=(
  'rm -rf'
  'find .*-delete'
  'git reset --hard'
  'git clean -fdx'
  'git push --force'
  'terraform destroy'
  'kubectl delete'
  'helm uninstall'
  'aws s3 rm .*--recursive'
  'aws cloudformation delete-stack'
  'DROP TABLE'
  'DROP DATABASE'
  'TRUNCATE TABLE'
  'ALTER TABLE .* DROP COLUMN'
  'chmod -R 777'
)

for pattern in "${destructive_patterns[@]}"; do
  if echo "${PATCH}" | grep -E "^\+.*${pattern}" >/dev/null 2>&1; then
    fail "Potential destructive operation added to diff: ${pattern}"
  fi
done

echo "Checking for common secret patterns in diff..."
secret_patterns=(
  'AKIA[0-9A-Z]{16}'
  'aws_secret_access_key'
  '-----BEGIN PRIVATE KEY-----'
  'ghp_[A-Za-z0-9_]{30,}'
  'xox[baprs]-[A-Za-z0-9-]+'
  "password[[:space:]]*=[[:space:]]*[\"'][^\"']+[\"']"
  "secret[[:space:]]*=[[:space:]]*[\"'][^\"']+[\"']"
  "token[[:space:]]*=[[:space:]]*[\"'][^\"']+[\"']"
)

for pattern in "${secret_patterns[@]}"; do
  if echo "${PATCH}" | grep -E "^\+.*${pattern}" >/dev/null 2>&1; then
    fail "Potential secret detected in added lines. Remove secret and rotate credential if real."
  fi
done

echo "Checking PR size..."
added_removed="$(git diff --numstat "${DIFF_RANGE}" | awk '{add+=$1; del+=$2} END {print add+del+0}')"
if [[ "${added_removed}" -gt 400 ]]; then
  warn "Large PR detected: ${added_removed} changed lines. Ensure PR justifies size and review focus."
fi

echo "Checking virtual environment artifacts are not staged..."
if git diff --cached --name-only 2>/dev/null | grep -E '^(\.agent/|\.venv/|node_modules/|vendor/bundle/|__pycache__/|\.pytest_cache/|\.mypy_cache/|target/)' >/dev/null; then
  fail "Generated environment/cache artifacts are staged. Unstage and keep them ignored."
fi

echo "Agent guardrail checks completed."
