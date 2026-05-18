# v14 correction

Cloud continuation is explicit-only. Do not run this workflow automatically or by schedule. Use it only with `AGENTIC_EXPLICIT_CLOUD=true` or the manual GitHub workflow confirmation.

# Cloud Continuation Guide

Cloud continuation lets agents keep working after your local machine is off.

## Cloud-safe tasks

- Repository analysis.
- Spec gap analysis.
- Test generation.
- CI failure debugging.
- Static security review.
- Lambda/API debugging if logs and safe credentials are available.
- Terraform fmt/validate/plan.
- PR documentation.
- Feedback/data analysis from committed artifacts, logs, or configured APIs.

## Cloud-unsafe tasks without explicit setup

- Testing a local-only app that requires your laptop.
- Accessing local databases.
- Manual browser checks against localhost unless the app can run in the CI environment.
- Production deployment without environment approval.

## Required behavior when cloud cannot test locally

The agent must:

1. Continue with all cloud-safe validation.
2. Record the missing local test as a QA gap.
3. Create a local-test request in the PR evidence.
4. Avoid claiming that the feature is fully tested.

## Running cloud continuation manually

```bash
python .ai/scripts/agentic_sdlc.py --allow-cloud run-once --mode cloud --max-specs 2
```

## GitHub scheduled mode

Use:

```text
.github/workflows/agentic-night-cloud.yml
```

Set repo secrets:

```text
OPENAI_API_KEY
```

For AWS Terraform apply workflows, configure GitHub OIDC and the role ARN secrets described in the Terraform workflow files.


## v14 local-first Codex policy

Agentic SDLC now defaults to local mode with Codex `gpt-5.5` and `model_reasoning_effort=xhigh`. Cloud mode is blocked unless explicitly requested with `--allow-cloud` or `AGENTIC_EXPLICIT_CLOUD=true`. See `.ai/docs/reference/LOCAL_FIRST_CODEX_RUNTIME_V14.md`.
