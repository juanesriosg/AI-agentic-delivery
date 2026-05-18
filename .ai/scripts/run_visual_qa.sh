#!/usr/bin/env bash
set -euo pipefail

STORY_ID="${AGENT_STORY_ID:-${1:-unknown-story}}"
mkdir -p ".agent/stories/${STORY_ID}/screenshots" ".agent/stories/${STORY_ID}/annotations"

echo "Visual QA bootstrap for story: ${STORY_ID}"

if [ -f package.json ] && command -v npx >/dev/null 2>&1; then
  if npx playwright --version >/dev/null 2>&1; then
    echo "Playwright detected. Run repo-specific Playwright tests or use .ai/visual/playwright.visual.template.ts as a scaffold."
    exit 0
  fi
fi

echo "No repo-approved screenshot automation detected. Create manual screenshot evidence or add Playwright/Cypress/Storybook tooling through an approved task."
python .ai/scripts/visual_qa_report.py --story "${STORY_ID}" || true
