# v13 POC-to-PR Update Report

## Goal

Make the package match this target workflow:

```text
Boss sends POC
AI PM creates GitHub repo and indexes it to GPT
GPT Pro creates a spec
GPT Pro pushes the spec to a new branch
Codex detects the new spec and implements with all agents
Agents push implementation to the branch where the spec lives
Agents create a final PR tagging the AI PM
```

## Main changes

Added source-spec-branch integration mode:

```json
"branching": {
  "push_tasks_to_source_spec_branch": true,
  "create_task_prs": false,
  "create_final_pr_from_spec_branch": true,
  "final_pr_base_branch": "main"
}
```

## New workflow

```text
.github/workflows/agentic-poc-spec-to-pr.yml
```

This workflow triggers when a spec is pushed to a watched branch and calls:

```bash
python .ai/scripts/poc_to_pr.py --allow-cloud --branch <branch> --mode cloud
```

## New scripts

```text
.ai/scripts/poc_to_pr.py
.ai/scripts/create_spec_branch.py
```

## Updated orchestrator

Updated:

```text
.ai/scripts/agentic_sdlc.py
```

New behavior:

```text
- detects source-spec-branch mode
- uses detached worktrees from the spec branch
- commits validated task output
- pushes task commits to the same spec branch
- creates/updates final PR from spec branch to main
```

## New docs/specs

```text
POC_TO_PR_WORKFLOW_V13.md
GPT_PRO_POC_SPEC_PUSH_GUIDE.md
.ai/prompts/gpt-pro-poc-to-spec.prompt.md
.ai/specs/poc-to-pr-policy.yml
.ai/specs/gpt-pro-spec-branch-contract.md
.ai/specs/source-spec-branch-integration-mode.md
```

## Duplicate workflow prevention

The old automatic `agentic-spec-autostart.yml` workflow is now manual-only to avoid duplicate Codex runs. The new automatic workflow is `agentic-poc-spec-to-pr.yml`.

## Validation

Validated:

```text
- Python compile for new/changed scripts
- YAML parse for new/changed workflows/specs
- JSON parse for automation config
- dry-run POC-to-PR spec detection in a synthetic repo
- dry-run run-spec call path
```

## Remaining environment requirements

A real repo needs:

```text
OPENAI_API_KEY
GitHub Actions enabled
branch protection configured
Codex CLI install step allowed
```

For AWS work, configure the existing Terraform/AWS role secrets before allowing cloud deployment.


## v13.1 fixes added during workflow review

- Removed the `paths:` filter from `agentic-poc-spec-to-pr.yml` so agent implementation/evidence pushes to the spec branch trigger continuation.
- Added ready-spec branch-scan fallback in `poc_to_pr.py` for pushes that do not modify the spec file.
- Added task completion markers under `docs/agentic-evidence/<spec-id>/<task-id>/task-completed.md`.
- Added skip logic so completed tasks are not repeated on later ephemeral GitHub Action/Codex runs.
- Allowed source-spec-branch mode to commit QA/PM/evidence-only task results, because the final PR is the review object.
- Kept template/example specs ignored and blocked from automatic implementation.


## Validation added for v13.1

Validated locally with a simulated git repository:

```text
- Python compile: poc_to_pr.py and agentic_sdlc.py
- YAML parse: all GitHub workflows
- JSON parse: agentic.config.json
- Spec validator: completed synthetic POC spec passes
- Design gate: completed synthetic POC spec passes
- Direct spec dry-run: detects ready spec and starts DB-first task
- Continuation fallback: code-only push scans branch and continues ready spec
- Template guard: explicit _TEMPLATE spec is ignored
- Completion marker skip: database task is skipped after task-completed marker exists
- Layer continuation: API starts after database layer gate exists; frontend remains blocked until API gate exists
```
