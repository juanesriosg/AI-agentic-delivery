# Agentic Delivery OS v8 audit and fix report

Date: 2026-05-14
Reviewer: GPT-5.5 Pro
Scope: reusable repo-level agentic SDLC package for local execution, Codex/Codex Cloud style execution, GitHub Actions, branch-spec ingestion, QA/PM gates, PR guardrails, and AWS/Terraform deployment controls.

## Executive feedback

The package is conceptually strong and aligned with the intended operating model: ChatGPT Pro creates specs, repo automation detects ready specs, specialist agents implement one-responsibility PRs, QA/PM/dev-manager gates review the work, and the human AI PM performs the final review.

The main issues were not about the agent definitions; they were automation-safety defects that could create noise, false confidence, or failed workflows. I corrected those defects and added validation coverage.

## Bugs fixed

### 1. Spec detection script could fail at runtime

`detect_new_specs.py` referenced undefined names and had duplicated argparse/default sections. This could break the GitHub spec ingestion workflow before dispatching agents.

**Fix:** rewrote `detect_new_specs.py` with explicit branch/path matching, ready-status handling, template/example ignore rules, placeholder blocking, JSON/Markdown output, and no external dependencies.

### 2. Template specs could be treated as real work

The package includes reusable spec templates. In inherited dev branches, those files can appear under watched spec paths and accidentally trigger automation.

**Fix:** template and example files are now hard-blocked in the orchestrator and detector. The spec validator reports templates as skipped templates, not implementation-ready feature specs.

### 3. Copied-but-incomplete specs could start implementation

A user could copy a template, rename it, set `status: ready_for_agents`, and leave placeholders such as `<feature>`, `{{ title }}`, or `owner/repo`.

**Fix:** the orchestrator runs `validate_agentic_spec.py` before coding. Placeholder specs are displayed as `not-ready:validation-failed` during scan and are skipped by `run-once`.

### 4. Scan output could say `ready` even when validation would later fail

Before the patch, `scan` only checked status/path readiness. It did not include the structural validation gate in the displayed readiness result.

**Fix:** `scan` now reports `not-ready:validation-failed` when the validator blocks the spec.

### 5. Title extraction could read comments or front-matter incorrectly

Specs with YAML front matter or comments could generate poor branch names and PR names.

**Fix:** added front-matter-aware title extraction. The orchestrator now prefers `title:` and only falls back to markdown headings after front matter.

### 6. Fallback planning could over-detect cloud work

Generic spec templates often mention AWS, Terraform, or database paths as examples. A simple frontend spec could be routed as cloud work if fallback routing read generic/template text too aggressively.

**Fix:** fallback routing now removes placeholders/examples, reads the explicit AWS/cloud section, inspects expected file paths, and respects explicit `no AWS/no infrastructure/no Terraform` answers.

### 7. Local/offline repositories needed safer branch behavior

Repos without `origin` or without fetched remote branches can still be used for dry-run and local workflows.

**Fix:** the orchestrator falls back to local branches when remotes are unavailable and avoids hard failures in local/offline scans.

### 8. Missing Codex could create false progress

A real run without Codex installed must not silently continue as if agents wrote code.

**Fix validated:** real runs fail non-zero when Codex is missing, while dry-runs still generate safe prompts/plans.

### 9. PR guardrails needed to catch default/pending evidence

Agents should not produce PRs with placeholder QA/PM/test evidence.

**Fix validated:** `pr_guardrails.py` blocks `PENDING_AGENT_VERIFICATION`, missing evidence, pending QA/PM decisions, evidence-only PRs, broad multi-domain PRs, protected deletions, and code changes without tests.

### 10. AWS changes must be Terraform-backed

New AWS components must not be created through ad-hoc AWS CLI commands.

**Fix validated:** `aws_terraform_guardrails.py` blocks mutating AWS CLI commands such as `aws lambda create-function` and allows Terraform-backed AWS changes while requiring the Terraform plan workflow to validate real infrastructure changes.

## Validation performed

- Python compilation for all `.ai/scripts/*.py` files.
- Bash syntax checks for all `.sh` files.
- JSON parsing for all `.json` files.
- YAML parsing for all `.yml` / `.yaml` files, including GitHub workflows.
- Completed example spec passes validation.
- Template spec files are skipped as templates.
- Remote-branch simulation with `dev/register-form` detects only the real spec, not templates.
- Dry-run implementation plans the frontend/register-form task and does not dirty the repo.
- GitHub-style `detect_new_specs.py` dispatches a ready completed spec.
- Placeholder copied template is blocked by both detector and orchestrator validation.
- Real run without Codex exits non-zero and does not pretend success.
- Local-only repo with no `origin` can scan and dry-run a ready spec.
- PR guardrails fail pending/default evidence and pass completed evidence with tests.
- AWS guardrails fail raw mutating AWS CLI and pass Terraform-backed AWS change with warning when Terraform CLI is unavailable.

## Remaining assumptions

- I did not run a real Codex Cloud workspace.
- I did not create a real GitHub PR using `gh`.
- I did not run real AWS credentials, a Terraform backend, or Terraform apply.
- I did not run application-specific unit/integration/E2E suites because this package is reusable and not installed into a real app repo yet.

## Recommended pilot flow

```bash
python .ai/scripts/agentic_sdlc.py doctor
python .ai/scripts/agentic_sdlc.py --dry-run scan
python .ai/scripts/agentic_sdlc.py --dry-run run-once --mode local --max-specs 1
```

Then create one completed spec under `specs/<feature>.spec.md`, push it to `dev/<feature>`, and enable full Codex execution only after the dry-run looks correct.
