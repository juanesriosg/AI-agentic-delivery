# Manifest v13 — POC to PR Workflow

## Added

- `.ai/docs/reference/POC_TO_PR_WORKFLOW_V13.md`
- `.ai/docs/reference/GPT_PRO_POC_SPEC_PUSH_GUIDE.md`
- `.ai/docs/reports/V13_POC_TO_PR_UPDATE_REPORT.md`
- `.github/workflows/agentic-poc-spec-to-pr.yml`
- `.ai/scripts/poc_to_pr.py`
- `.ai/scripts/create_spec_branch.py`
- `.ai/prompts/gpt-pro-poc-to-spec.prompt.md`
- `.ai/specs/poc-to-pr-policy.yml`
- `.ai/specs/gpt-pro-spec-branch-contract.md`
- `.ai/specs/source-spec-branch-integration-mode.md`

## Updated

- `AGENTS.md`
- `.ai/docs/README.md`
- `.ai/docs/START_HERE.md`
- `.ai/automation/agentic.config.json`
- `.ai/scripts/agentic_sdlc.py`
- `.github/workflows/agentic-spec-autostart.yml`

## Default operating mode

```text
source spec branch = implementation branch
final PR = source spec branch → main
```


## v13.1 fix notes

- `agentic-poc-spec-to-pr.yml` now triggers on any push to watched spec/dev branches so implementation pushes can continue the cycle.
- `poc_to_pr.py` now falls back to scanning ready specs already present on the branch.
- `agentic_sdlc.py` now writes and reads task completion markers to avoid repeating completed tasks across ephemeral runners.

- .ai/docs/reports/V13_POC_TO_PR_VALIDATION_REPORT.md


## v13.2 fix notes

- `gpt-pro-poc-to-spec.prompt.md` now includes all fields required by `validate_agentic_spec.py`.
- `gpt-pro-spec-branch-contract.md` now defines `source_branch`, `target_branch`, and `final_pr_base` explicitly for final PRs from spec branch to `main`.
- `create_spec_branch.py` now fills validator-friendly front matter such as `spec_id`, `story_id`, `source_branch`, `target_branch`, `priority`, `risk_level`, and PR strategy.
