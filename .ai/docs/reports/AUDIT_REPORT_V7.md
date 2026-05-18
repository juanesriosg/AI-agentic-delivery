# Agentic Delivery OS v7 Audit Report

This package was reviewed as a reusable repo-level agentic SDLC kit. The audit focused on automation safety, branch/spec detection, Codex/local/cloud execution behavior, PR evidence gates, Terraform/AWS guardrails, and GitHub workflow correctness.

## Corrected issues

1. **Template specs could be treated as implementation specs.**
   - Added template/example ignore rules to spec scanning.
   - `run-spec` now blocks `_TEMPLATE` paths explicitly.
   - The spec validator now fails reusable template files instead of reporting them as ready.

2. **Local/offline repos failed too early.**
   - `scan --no-fetch` and `run-once --no-fetch` now work when no `origin` remote exists.
   - Branch and spec reads fall back to local branch refs when remote refs are unavailable.

3. **Duplicate automation could trigger on the same spec.**
   - The legacy ingestion/story workflows are manual-only in v7.
   - Automatic spec-to-code execution is centralized in `agentic-spec-autostart.yml`.

4. **Installing/upgrading `.ai` files could trigger agents.**
   - The auto-start workflow now watches spec paths only, not `.ai/**` or `AGENTS.md`.

5. **Codex missing could silently look successful.**
   - Real runs now fail with a non-zero exit when Codex is missing unless the repo explicitly allows prompt-only mode.
   - Dry runs still generate plans/prompts safely.

6. **Evidence-only PRs could be created.**
   - The orchestrator now checks for meaningful non-evidence changes before opening a PR.
   - Runtime and generated artifacts are excluded from reviewable change detection.

7. **Placeholder evidence could pass too easily.**
   - PR/stage gates now block `PENDING_AGENT_VERIFICATION`, default automation text, missing QA/PM status lines, and missing required evidence files.

8. **PR guardrails missed uncommitted local changes.**
   - Guardrails now inspect committed, staged, unstaged, and untracked files.
   - Untracked directories expand to concrete files so line/file limits and tests are evaluated correctly before commit.

9. **AWS guardrails missed uncommitted shell/scripts.**
   - AWS/Terraform guardrails now inspect staged, unstaged, and untracked content for raw mutating AWS CLI commands.

10. **GitHub Actions used secrets directly in an `if:` condition.**
    - The Terraform plan workflow now maps the secret to a job env variable and checks the env variable.

11. **Initial spec commits could skip validation.**
    - The spec validation workflow now falls back to `git ls-files` when `HEAD~1` does not exist.

12. **PR body generation had a runtime variable mismatch.**
    - `create_pr_body` now receives the runtime mode explicitly.

## Validation performed

- Python scripts compile.
- Shell scripts pass `bash -n`.
- YAML files parse.
- Completed example spec passes validation.
- Template spec fails validation as expected.
- Local repo with no `origin` can scan and dry-run a ready spec.
- Direct run against `_TEMPLATE` spec is blocked.
- Real run with missing Codex exits non-zero and does not create a false PR.
- PR guardrails fail pending/default evidence and pass completed evidence with tests.
- AWS guardrails block raw mutating AWS CLI commands and allow Terraform-backed AWS changes.

## Known limits

- This audit did not execute real Codex Cloud jobs.
- This audit did not assume an AWS account or run real Terraform plans against AWS.
- Local-only app tests still require a runnable local or CI environment; cloud agents must record those gaps instead of claiming completion.
