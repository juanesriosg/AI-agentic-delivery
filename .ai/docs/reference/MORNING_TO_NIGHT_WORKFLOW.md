# v14 correction

Night cloud continuation is no longer scheduled automatically. The default is local mode. Cloud continuation is manual-only and requires explicit confirmation.

# Morning-to-Night Agentic Workflow

## 8:00 AM local: start local loop

```bash
python .ai/scripts/agentic_sdlc.py watch --mode local --poll-seconds 180
```

The local loop can run browser/UI tests, screenshot capture, component tests, E2E checks, and any dev app validation that requires your machine.

## During the day

You stay in ChatGPT Pro writing specs, analyzing product behavior, and reviewing agent PRs. The script watches Git branches for new specs and starts work automatically.

Recommended habit:

```text
spec branch -> agent implementation PRs -> human review at end of day
```

## Before shutting down your PC

Run:

```bash
python .ai/scripts/agentic_sdlc.py cloud-plan
```

This summarizes work that can continue safely in cloud.

## Night: cloud continuation

GitHub Actions runs:

```text
.github/workflows/agentic-night-cloud.yml
```

Cloud work focuses on:

```text
- pending specs
- small code improvements
- CI failures
- Lambda/API debugging where logs and credentials are available
- Terraform plan generation
- static security review
- missing spec analysis
- feedback/data analysis
- test generation
- PR documentation improvements
```

Cloud work should not assume access to local-only services. If a local app cannot be started, the agent must produce a local-test request and continue with cloud-safe validation.

## Next morning

Review:

```bash
python .ai/scripts/agentic_sdlc.py status
```

Then review PRs tagged with your username.


## v14 local-first Codex policy

Agentic SDLC now defaults to local mode with Codex `gpt-5.5` and `model_reasoning_effort=xhigh`. Cloud mode is blocked unless explicitly requested with `--allow-cloud` or `AGENTIC_EXPLICIT_CLOUD=true`. See `.ai/docs/reference/LOCAL_FIRST_CODEX_RUNTIME_V14.md`.
