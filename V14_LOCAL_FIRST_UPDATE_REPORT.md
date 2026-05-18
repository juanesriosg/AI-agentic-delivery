# v14 Local-first Codex runtime update report

## Manager request

Codex should run the agentic SDLC in local mode by default using the latest configured model, currently `gpt-5.5`, with extra-high reasoning. Cloud execution should happen only when explicitly stated.

## Implemented changes

- Set the default runtime mode to `local` in the repo automation config.
- Set the Codex model to `gpt-5.5`.
- Set the Codex reasoning effort to `xhigh`, mapped from the manager preference `extra_high` because the Codex config key supports `xhigh`.
- Added explicit Codex CLI arguments in the orchestrator:
  - `codex exec`
  - `--model gpt-5.5`
  - `-c model_reasoning_effort=xhigh`
  - `-c model_reasoning_summary=concise`
  - `-c model_verbosity=high`
- Blocked `--mode cloud` unless one of these explicit approvals exists:
  - `--allow-cloud`
  - `AGENTIC_EXPLICIT_CLOUD=true`
  - manual GitHub workflow input `allow_cloud=true`
  - manual cloud continuation confirmation `I_APPROVE_CLOUD_RUN`
- Removed scheduled night cloud behavior. The cloud continuation workflow is manual-only.
- Updated POC-to-PR and spec autostart workflows to default to `local`.
- Updated Codex PR review action to use `model: gpt-5.5` and `effort: xhigh`.

## Main files changed

- `LOCAL_FIRST_CODEX_RUNTIME_V14.md`
- `.ai/automation/agentic.config.json`
- `.ai/scripts/agentic_sdlc.py`
- `.ai/scripts/poc_to_pr.py`
- `.github/workflows/agentic-poc-spec-to-pr.yml`
- `.github/workflows/agentic-spec-autostart.yml`
- `.github/workflows/agentic-night-cloud.yml`
- `.github/workflows/agentic-codex-pr-review.yml`
- `.codex/config.local-first.toml.example`
- `README.md`
- `START_HERE.md`

## Validation performed

- Python compile check for all `.ai/scripts/*.py`.
- JSON parse and policy assertions for `.ai/automation/agentic.config.json`.
- YAML parse check for all GitHub workflows.
- Simulated repo dry-run:
  - `agentic_sdlc.py --dry-run run-once --mode local` exits `0`.
  - `agentic_sdlc.py --dry-run run-once --mode cloud` exits `2` when not explicitly allowed.
  - `AGENTIC_EXPLICIT_CLOUD=true agentic_sdlc.py --dry-run run-once --mode cloud` exits `0`.
  - `poc_to_pr.py --mode cloud` exits `2` when not explicitly allowed.
  - `poc_to_pr.py --mode local` exits `0`.
  - `poc_to_pr.py --mode cloud --allow-cloud` exits `0`.
- Fake Codex CLI test confirmed the orchestrator passes:
  - `--model gpt-5.5`
  - `-c model_reasoning_effort=xhigh`
  - `--sandbox workspace-write`

## Not validated

- Real Codex execution with a live account and credentials.
- Real GitHub PR creation through `gh`.
- Real app-specific local tests because no project app was installed in this package test.
- Real AWS or Terraform operations.
